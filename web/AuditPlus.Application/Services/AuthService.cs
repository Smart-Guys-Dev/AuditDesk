using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using System.Text.RegularExpressions;
using Microsoft.Extensions.Options;
using Microsoft.IdentityModel.Tokens;
using AuditPlus.Application.DTOs;
using AuditPlus.Application.Interfaces;
using AuditPlus.Application.Settings;
using AuditPlus.Domain.Entities;
using AuditPlus.Domain.Interfaces;

namespace AuditPlus.Application.Services;

/// <summary>
/// Implementação do serviço de autenticação.
/// Gerencia login, registro e tokens JWT.
/// </summary>
public class AuthService : IAuthService
{
    private readonly IUserRepository _userRepository;
    private readonly IPasswordHasher _passwordHasher;
    private readonly JwtSettings _jwtSettings;
    
    public AuthService(
        IUserRepository userRepository,
        IPasswordHasher passwordHasher,
        IOptions<JwtSettings> jwtSettings)
    {
        _userRepository = userRepository;
        _passwordHasher = passwordHasher;
        _jwtSettings = jwtSettings.Value;
    }
    
    /// <inheritdoc/>
    public async Task<LoginResponse?> LoginAsync(LoginRequest request)
    {
        // Buscar usuário
        var user = await _userRepository.GetByUsernameAsync(request.Username);
        if (user == null || !user.IsActive)
            return null;
            
        // Verificar se está bloqueado
        if (user.LockedUntil.HasValue && user.LockedUntil > DateTime.UtcNow)
            return null;
            
        // Verificar senha
        if (!_passwordHasher.VerifyPassword(request.Password, user.PasswordHash))
        {
            // Incrementar tentativas falhas
            user.FailedLoginAttempts++;
            if (user.FailedLoginAttempts >= 5)
            {
                user.LockedUntil = DateTime.UtcNow.AddMinutes(15);
            }
            await _userRepository.UpdateAsync(user);
            return null;
        }
        
        // Login bem-sucedido - resetar tentativas
        user.FailedLoginAttempts = 0;
        user.LockedUntil = null;
        user.LastLoginAt = DateTime.UtcNow;
        await _userRepository.UpdateAsync(user);
        
        // Gerar token
        var token = GenerateJwtToken(user);
        var expiresAt = DateTime.UtcNow.AddHours(_jwtSettings.ExpirationHours);
        
        return new LoginResponse(
            Token: token,
            Username: user.Username,
            FullName: user.FullName,
            Role: user.Role.ToString(),
            ExpiresAt: expiresAt
        );
    }
    
    /// <inheritdoc/>
    public async Task<UserResponse?> RegisterAsync(RegisterRequest request)
    {
        // Verificar se username já existe
        if (await _userRepository.UsernameExistsAsync(request.Username))
            return null;
        
        // OWASP A07: Validar força da senha
        var passwordErrors = ValidatePasswordStrength(request.Password);
        if (passwordErrors.Count > 0)
            throw new ArgumentException(
                $"Senha fraca: {string.Join("; ", passwordErrors)}");
            
        // Criar usuário
        var user = new User
        {
            Username = request.Username,
            PasswordHash = _passwordHasher.HashPassword(request.Password),
            FullName = request.FullName,
            Email = request.Email,
            Role = Enum.Parse<Domain.Enums.UserRole>(request.Role, ignoreCase: true),
            IsActive = true,
            CreatedAt = DateTime.UtcNow
        };
        
        await _userRepository.AddAsync(user);
        
        return new UserResponse(
            Id: user.Id,
            Username: user.Username,
            FullName: user.FullName,
            Email: user.Email,
            Role: user.Role.ToString(),
            LastLoginAt: user.LastLoginAt
        );
    }
    
    /// <inheritdoc/>
    public async Task<UserResponse?> GetUserByIdAsync(int userId)
    {
        var user = await _userRepository.GetByIdAsync(userId);
        if (user == null)
            return null;
            
        return new UserResponse(
            Id: user.Id,
            Username: user.Username,
            FullName: user.FullName,
            Email: user.Email,
            Role: user.Role.ToString(),
            LastLoginAt: user.LastLoginAt
        );
    }
    
    /// <inheritdoc/>
    public async Task<bool> ChangePasswordAsync(int userId, ChangePasswordRequest request)
    {
        var user = await _userRepository.GetByIdAsync(userId);
        if (user == null)
            return false;
            
        // Verificar senha atual
        if (!_passwordHasher.VerifyPassword(request.CurrentPassword, user.PasswordHash))
            return false;
        
        // OWASP A07: Validar força da nova senha
        var passwordErrors = ValidatePasswordStrength(request.NewPassword);
        if (passwordErrors.Count > 0)
            throw new ArgumentException(
                $"Senha fraca: {string.Join("; ", passwordErrors)}");
            
        // Atualizar senha
        user.PasswordHash = _passwordHasher.HashPassword(request.NewPassword);
        await _userRepository.UpdateAsync(user);
        
        return true;
    }
    
    /// <inheritdoc/>
    public bool ValidateToken(string token)
    {
        var tokenHandler = new JwtSecurityTokenHandler();
        var key = Encoding.UTF8.GetBytes(_jwtSettings.SecretKey);
        
        try
        {
            tokenHandler.ValidateToken(token, new TokenValidationParameters
            {
                ValidateIssuerSigningKey = true,
                IssuerSigningKey = new SymmetricSecurityKey(key),
                ValidateIssuer = true,
                ValidIssuer = _jwtSettings.Issuer,
                ValidateAudience = true,
                ValidAudience = _jwtSettings.Audience,
                ValidateLifetime = true,
                ClockSkew = TimeSpan.Zero
            }, out _);
            
            return true;
        }
        catch
        {
            return false;
        }
    }
    
    /// <summary>
    /// Gera um token JWT para o usuário
    /// </summary>
    private string GenerateJwtToken(User user)
    {
        var key = Encoding.UTF8.GetBytes(_jwtSettings.SecretKey);
        var securityKey = new SymmetricSecurityKey(key);
        var credentials = new SigningCredentials(securityKey, SecurityAlgorithms.HmacSha256);
        
        var claims = new[]
        {
            new Claim(ClaimTypes.NameIdentifier, user.Id.ToString()),
            new Claim(ClaimTypes.Name, user.Username),
            new Claim(ClaimTypes.GivenName, user.FullName),
            new Claim(ClaimTypes.Role, user.Role.ToString()),
            new Claim(JwtRegisteredClaimNames.Jti, Guid.NewGuid().ToString())
        };
        
        var token = new JwtSecurityToken(
            issuer: _jwtSettings.Issuer,
            audience: _jwtSettings.Audience,
            claims: claims,
            expires: DateTime.UtcNow.AddHours(_jwtSettings.ExpirationHours),
            signingCredentials: credentials
        );
        
        return new JwtSecurityTokenHandler().WriteToken(token);
    }
    
    /// <summary>
    /// OWASP A07: Valida força da senha.
    /// Mínimo 8 caracteres, maiúscula, minúscula, dígito e especial.
    /// </summary>
    private static List<string> ValidatePasswordStrength(string password)
    {
        var errors = new List<string>();
        
        if (string.IsNullOrWhiteSpace(password))
        {
            errors.Add("Senha não pode ser vazia");
            return errors;
        }
        
        if (password.Length < 8)
            errors.Add("Mínimo 8 caracteres");
        if (!Regex.IsMatch(password, @"[A-Z]"))
            errors.Add("Deve conter letra maiúscula");
        if (!Regex.IsMatch(password, @"[a-z]"))
            errors.Add("Deve conter letra minúscula");
        if (!Regex.IsMatch(password, @"[0-9]"))
            errors.Add("Deve conter dígito");
        if (!Regex.IsMatch(password, @"[!@#$%^&*()_+\-=\[\]{};':""\\|,.<>\/?]"))
            errors.Add("Deve conter caractere especial (!@#$%...)");
        
        return errors;
    }
}
