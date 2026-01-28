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
}

app.Run();
