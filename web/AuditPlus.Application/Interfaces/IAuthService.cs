using AuditPlus.Application.DTOs;

namespace AuditPlus.Application.Interfaces;

/// <summary>
/// Interface do serviço de autenticação.
/// Define operações de login, registro e gerenciamento de usuários.
/// </summary>
public interface IAuthService
{
    /// <summary>
    /// Autentica um usuário e retorna um token JWT
    /// </summary>
    Task<LoginResponse?> LoginAsync(LoginRequest request);
    
    /// <summary>
    /// Registra um novo usuário
    /// </summary>
    Task<UserResponse?> RegisterAsync(RegisterRequest request);
    
    /// <summary>
    /// Obtém dados do usuário por ID
    /// </summary>
    Task<UserResponse?> GetUserByIdAsync(int userId);
    
    /// <summary>
    /// Altera a senha de um usuário
    /// </summary>
    Task<bool> ChangePasswordAsync(int userId, ChangePasswordRequest request);
    
    /// <summary>
    /// Valida se um token JWT é válido
    /// </summary>
    bool ValidateToken(string token);
}
