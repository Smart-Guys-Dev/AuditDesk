using System.Text;
using System.Threading.RateLimiting;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.AspNetCore.RateLimiting;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;
using AuditPlus.Infrastructure.Data;
using AuditPlus.Domain.Interfaces;
using AuditPlus.Infrastructure.Repositories;
using AuditPlus.Application.Interfaces;
using AuditPlus.Application.Services;
using AuditPlus.Application.Settings;

var builder = WebApplication.CreateBuilder(args);

// ============================================
// CONFIGURAÇÃO DE SERVIÇOS
// ============================================

// Controllers
builder.Services.AddControllers();

// JWT Settings — OWASP A02: Nunca usar fallback hardcoded em produção
var jwtSettings = builder.Configuration.GetSection(JwtSettings.SectionName).Get<JwtSettings>();
if (jwtSettings is null || string.IsNullOrWhiteSpace(jwtSettings.SecretKey) 
    || jwtSettings.SecretKey.StartsWith("CHANGE_ME"))
{
    if (!builder.Environment.IsDevelopment())
    {
        throw new InvalidOperationException(
            "SECURITY: JwtSettings:SecretKey is not configured. " +
            "Set it via environment variable or User Secrets.");
    }
    // Em dev, usar chave padrão com warning
    jwtSettings = new JwtSettings
    {
        SecretKey = "DevOnlySecretKey2024!@#VeryLongSecretKeyFor256BitsSecurity",
        Issuer = "AuditPlus",
        Audience = "AuditPlusWeb",
        ExpirationHours = 8
    };
    Console.WriteLine("⚠️  AVISO: Usando JWT secret de desenvolvimento. NÃO use em produção!");
}
builder.Services.Configure<JwtSettings>(builder.Configuration.GetSection(JwtSettings.SectionName));

// Swagger/OpenAPI - .NET 10 built-in support
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddOpenApi();

// JWT Authentication
builder.Services.AddAuthentication(options =>
{
    options.DefaultAuthenticateScheme = JwtBearerDefaults.AuthenticationScheme;
    options.DefaultChallengeScheme = JwtBearerDefaults.AuthenticationScheme;
})
.AddJwtBearer(options =>
{
    options.TokenValidationParameters = new TokenValidationParameters
    {
        ValidateIssuerSigningKey = true,
        IssuerSigningKey = new SymmetricSecurityKey(
            Encoding.UTF8.GetBytes(jwtSettings.SecretKey)),
        ValidateIssuer = true,
        ValidIssuer = jwtSettings.Issuer,
        ValidateAudience = true,
        ValidAudience = jwtSettings.Audience,
        ValidateLifetime = true,
        ClockSkew = TimeSpan.FromSeconds(30) // Pequena tolerância para relógios dessincronizados
    };
});

builder.Services.AddAuthorization();

// Entity Framework Core — Provider configurável via appsettings
var dbProvider = builder.Configuration["Database:Provider"] ?? "Sqlite";

builder.Services.AddDbContext<AppDbContext>(options =>
{
    if (dbProvider.Equals("Oracle", StringComparison.OrdinalIgnoreCase))
    {
        options.UseOracle(builder.Configuration.GetConnectionString("OracleConnection")
            ?? throw new InvalidOperationException("OracleConnection não configurada."));
    }
    else
    {
        options.UseSqlite(builder.Configuration.GetConnectionString("DefaultConnection") 
            ?? "Data Source=auditplus.db");
    }
});

// Dependency Injection - Repositories
builder.Services.AddScoped<IUserRepository, UserRepository>();
builder.Services.AddScoped<IRegraRepository, RegraRepository>();
builder.Services.AddScoped<IExecucaoRepository, ExecucaoRepository>();

// Dependency Injection - Services
// Password hasher: BCrypt (dev/SQLite) ou SHA256+MD5 (Oracle/ODA)
if (dbProvider.Equals("Oracle", StringComparison.OrdinalIgnoreCase))
    builder.Services.AddSingleton<IPasswordHasher, Sha256Md5PasswordHasher>();
else
    builder.Services.AddSingleton<IPasswordHasher, BcryptPasswordHasher>();

builder.Services.AddScoped<IAuthService, AuthService>();
builder.Services.AddScoped<XmlValidationService>();
builder.Services.AddScoped<RuleImportService>();
builder.Services.AddScoped<HashCalculatorService>();

// CORS — OWASP A05: Origins configuráveis via appsettings
var allowedOrigins = builder.Configuration
    .GetSection("Cors:AllowedOrigins").Get<string[]>()
    ?? ["http://localhost:4200"];

builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowConfigured", policy =>
    {
        policy.WithOrigins(allowedOrigins)
              .AllowAnyHeader()
              .AllowAnyMethod();
    });
});

// OWASP A04: Rate Limiting — prevenção de brute-force
builder.Services.AddRateLimiter(options =>
{
    options.RejectionStatusCode = StatusCodes.Status429TooManyRequests;
    
    // Política para login: 5 tentativas por minuto por IP
    options.AddFixedWindowLimiter("login", limiterOptions =>
    {
        limiterOptions.PermitLimit = 5;
        limiterOptions.Window = TimeSpan.FromMinutes(1);
        limiterOptions.QueueProcessingOrder = QueueProcessingOrder.OldestFirst;
        limiterOptions.QueueLimit = 0;
    });
    
    // Política geral para API: 100 requests por minuto por IP
    options.AddFixedWindowLimiter("api", limiterOptions =>
    {
        limiterOptions.PermitLimit = 100;
        limiterOptions.Window = TimeSpan.FromMinutes(1);
        limiterOptions.QueueProcessingOrder = QueueProcessingOrder.OldestFirst;
        limiterOptions.QueueLimit = 2;
    });
    
    // Partição por IP
    options.GlobalLimiter = PartitionedRateLimiter.Create<HttpContext, string>(context =>
        RateLimitPartition.GetFixedWindowLimiter(
            partitionKey: context.Connection.RemoteIpAddress?.ToString() ?? "unknown",
            factory: _ => new FixedWindowRateLimiterOptions
            {
                PermitLimit = 200,
                Window = TimeSpan.FromMinutes(1)
            }));
});

var app = builder.Build();

// ============================================
// CONFIGURAÇÃO DO PIPELINE HTTP
// ============================================

// OWASP A05: Security Headers — Defesa em profundidade
app.Use(async (context, next) =>
{
    var headers = context.Response.Headers;
    headers.Append("X-Content-Type-Options", "nosniff");
    headers.Append("X-Frame-Options", "DENY");
    headers.Append("X-XSS-Protection", "0"); // Desabilitado em favor do CSP
    headers.Append("Referrer-Policy", "strict-origin-when-cross-origin");
    headers.Append("Permissions-Policy", "camera=(), microphone=(), geolocation=()");
    headers.Append("Content-Security-Policy", 
        "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self'");
    headers.Append("Cache-Control", "no-store");
    headers.Append("Pragma", "no-cache");
    // OWASP: HSTS — forçar HTTPS
    headers.Append("Strict-Transport-Security", "max-age=31536000; includeSubDomains");
    await next();
});

// Development settings
if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();
}
else
{
    app.UseHsts();
}

app.UseHttpsRedirection();
app.UseCors("AllowConfigured");

// OWASP A04: Rate Limiting
app.UseRateLimiter();

// Authentication & Authorization
app.UseAuthentication();
app.UseAuthorization();

app.MapControllers();

// Criar banco de dados e seed de dados em desenvolvimento
if (app.Environment.IsDevelopment())
{
    await SeedDevelopmentDataAsync(app);
}

app.Run();

// ============================================
// SEED — Dados de desenvolvimento (async)
// ============================================
static async Task SeedDevelopmentDataAsync(WebApplication app)
{
    using var scope = app.Services.CreateScope();
    var logger = scope.ServiceProvider.GetRequiredService<ILoggerFactory>()
        .CreateLogger("Seed");
    var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
    await db.Database.EnsureCreatedAsync();
    
    // Seed: Criar usuário admin se não existir
    var userRepo = scope.ServiceProvider.GetRequiredService<IUserRepository>();
    var adminPassword = app.Configuration["Security:AdminDefaultPassword"] ?? "AuditPlus@2024!Secure";
    
    var passwordHasher = scope.ServiceProvider.GetRequiredService<IPasswordHasher>();
    
    if (!await userRepo.UsernameExistsAsync("admin"))
    {
        await userRepo.AddAsync(new AuditPlus.Domain.Entities.User
        {
            Username = "admin",
            PasswordHash = passwordHasher.HashPassword(adminPassword),
            FullName = "Administrador",
            Role = AuditPlus.Domain.Enums.UserRole.ADMIN,
            IsActive = true,
            CreatedAt = DateTime.UtcNow
        });
        logger.LogInformation("Usuário admin criado com senha padrão");
    }
    
    // Seed: Criar regras de exemplo se não existirem
    var regraRepo = scope.ServiceProvider.GetRequiredService<IRegraRepository>();
    var regras = await regraRepo.GetAllAsync();
    if (!regras.Any())
    {
        var regrasExemplo = new[]
        {
            new AuditPlus.Domain.Entities.Regra
            {
                Codigo = "REGRA_CPF_PRESTADOR_9134",
                Nome = "Validar CPF do Prestador CNS 9134",
                Descricao = "Corrige CPF quando começa com 9134 (CNS)",
                Categoria = AuditPlus.Domain.Enums.RuleCategory.GLOSA_GUIA,
                Grupo = AuditPlus.Domain.Enums.RuleGroup.PRESTADOR,
                Ativo = true,
                Prioridade = 10,
                TotalAplicacoes = 245,
                TotalGlosasEvitadas = 180,
                CreatedAt = DateTime.UtcNow
            },
            new AuditPlus.Domain.Entities.Regra
            {
                Codigo = "REGRA_DATA_EXEC_FUTURA",
                Nome = "Validar Data Execução não Futura",
                Descricao = "Impede datas de execução no futuro",
                Categoria = AuditPlus.Domain.Enums.RuleCategory.VALIDACAO,
                Grupo = AuditPlus.Domain.Enums.RuleGroup.DATAS,
                Ativo = true,
                Prioridade = 5,
                TotalAplicacoes = 520,
                TotalGlosasEvitadas = 420,
                CreatedAt = DateTime.UtcNow
            },
            new AuditPlus.Domain.Entities.Regra
            {
                Codigo = "REGRA_DUPLICIDADE_GUIA",
                Nome = "Detectar Guias Duplicadas",
                Descricao = "Identifica e remove guias duplicadas no lote",
                Categoria = AuditPlus.Domain.Enums.RuleCategory.GLOSA_GUIA,
                Grupo = AuditPlus.Domain.Enums.RuleGroup.DUPLICIDADES,
                Ativo = true,
                Prioridade = 1,
                TotalAplicacoes = 89,
                TotalGlosasEvitadas = 89,
                CreatedAt = DateTime.UtcNow
            },
            new AuditPlus.Domain.Entities.Regra
            {
                Codigo = "REGRA_VALOR_ZERO",
                Nome = "Validar Valor Unitário não Zero",
                Descricao = "Impede envio de procedimentos com valor R$ 0,00",
                Categoria = AuditPlus.Domain.Enums.RuleCategory.GLOSA_ITEM,
                Grupo = AuditPlus.Domain.Enums.RuleGroup.VALORES,
                Ativo = true,
                Prioridade = 15,
                TotalAplicacoes = 312,
                TotalGlosasEvitadas = 290,
                CreatedAt = DateTime.UtcNow
            },
            new AuditPlus.Domain.Entities.Regra
            {
                Codigo = "REGRA_OTIM_HASH",
                Nome = "Otimizar Hash de Arquivos",
                Descricao = "Gera hash para controle de duplicidade",
                Categoria = AuditPlus.Domain.Enums.RuleCategory.OTIMIZACAO,
                Grupo = AuditPlus.Domain.Enums.RuleGroup.OUTROS,
                Ativo = true,
                Prioridade = 100,
                TotalAplicacoes = 1500,
                TotalGlosasEvitadas = 0,
                CreatedAt = DateTime.UtcNow
            }
        };
        
        foreach (var regra in regrasExemplo)
        {
            await regraRepo.AddAsync(regra);
        }
        logger.LogInformation("{Count} regras de exemplo criadas", regrasExemplo.Length);
    }
    
    // Seed: Criar execuções de exemplo
    var execucaoRepo = scope.ServiceProvider.GetRequiredService<IExecucaoRepository>();
    var execucoes = await execucaoRepo.GetAllAsync();
    if (!execucoes.Any())
    {
        var random = new Random(42);
        var execucoesExemplo = Enumerable.Range(1, 12).Select(i =>
        {
            var data = DateTime.UtcNow.AddMonths(-12 + i).AddDays(random.Next(-5, 5));
            var arquivos = random.Next(50, 200);
            var sucesso = (int)(arquivos * (0.85 + random.NextDouble() * 0.14));
            return new AuditPlus.Domain.Entities.Execucao
            {
                TipoOperacao = "CORRECAO",
                Status = random.NextDouble() > 0.1 ? "CONCLUIDO" : "ERRO",
                TotalArquivos = arquivos,
                ArquivosSucesso = sucesso,
                ArquivosErro = arquivos - sucesso,
                DataInicio = data,
                DataFim = data.AddMinutes(random.Next(5, 45)),
                DuracaoSegundos = random.Next(300, 2700),
                TotalCorrecoes = random.Next(100, 500),
                ValorEconomizado = random.Next(5000, 50000),
                CreatedAt = data
            };
        }).ToList();
        
        foreach (var exec in execucoesExemplo)
        {
            await execucaoRepo.AddAsync(exec);
        }
        logger.LogInformation("{Count} execuções de exemplo criadas", execucoesExemplo.Count);
    }
}
