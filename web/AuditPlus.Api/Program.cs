using System.Text;
using Microsoft.AspNetCore.Authentication.JwtBearer;
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

// JWT Settings
var jwtSettings = builder.Configuration.GetSection(JwtSettings.SectionName).Get<JwtSettings>() 
    ?? new JwtSettings { SecretKey = "AuditPlusSecretKey2024!@#VeryLongSecretKey256bits" };
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
        ClockSkew = TimeSpan.Zero
    };
});

builder.Services.AddAuthorization();

// Entity Framework Core - SQLite
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseSqlite(builder.Configuration.GetConnectionString("DefaultConnection") 
        ?? "Data Source=auditplus.db"));

// Dependency Injection - Repositories
builder.Services.AddScoped<IUserRepository, UserRepository>();
builder.Services.AddScoped<IRegraRepository, RegraRepository>();
builder.Services.AddScoped<IExecucaoRepository, ExecucaoRepository>();

// Dependency Injection - Services
builder.Services.AddScoped<IAuthService, AuthService>();

// CORS para Angular
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowAngular", policy =>
    {
        policy.WithOrigins("http://localhost:4200")
              .AllowAnyHeader()
              .AllowAnyMethod();
    });
});

var app = builder.Build();

// ============================================
// CONFIGURAÇÃO DO PIPELINE HTTP
// ============================================

// Development settings
if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();
}

app.UseHttpsRedirection();
app.UseCors("AllowAngular");

// Authentication & Authorization
app.UseAuthentication();
app.UseAuthorization();

app.MapControllers();

// Criar banco de dados e seed de dados em desenvolvimento
if (app.Environment.IsDevelopment())
{
    using var scope = app.Services.CreateScope();
    var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
    db.Database.EnsureCreated();
    
    // Seed: Criar usuário admin se não existir
    var userRepo = scope.ServiceProvider.GetRequiredService<IUserRepository>();
    var adminExists = userRepo.UsernameExistsAsync("admin").GetAwaiter().GetResult();
    if (!adminExists)
    {
        userRepo.AddAsync(new AuditPlus.Domain.Entities.User
        {
            Username = "admin",
            PasswordHash = BCrypt.Net.BCrypt.HashPassword("admin123"),
            FullName = "Administrador",
            Role = AuditPlus.Domain.Enums.UserRole.ADMIN,
            IsActive = true,
            CreatedAt = DateTime.UtcNow
        }).GetAwaiter().GetResult();
        Console.WriteLine("✅ Usuário admin criado: admin / admin123");
    }
    
    // Seed: Criar regras de exemplo se não existirem
    var regraRepo = scope.ServiceProvider.GetRequiredService<IRegraRepository>();
    var regrasExistem = regraRepo.GetAllAsync().GetAwaiter().GetResult().Any();
    if (!regrasExistem)
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
            regraRepo.AddAsync(regra).GetAwaiter().GetResult();
        }
        Console.WriteLine($"✅ {regrasExemplo.Length} regras de exemplo criadas");
    }
    
    // Seed: Criar execuções de exemplo
    var execucaoRepo = scope.ServiceProvider.GetRequiredService<IExecucaoRepository>();
    var execucoesExistem = execucaoRepo.GetAllAsync().GetAwaiter().GetResult().Any();
    if (!execucoesExistem)
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
            execucaoRepo.AddAsync(exec).GetAwaiter().GetResult();
        }
        Console.WriteLine($"✅ {execucoesExemplo.Count} execuções de exemplo criadas");
    }
}

app.Run();

