namespace AuditPlus.Application.DTOs;

/// <summary>
/// DTO para requisição de login
/// </summary>
public record LoginRequest(string Username, string Password);

/// <summary>
/// DTO para resposta de login com token JWT
/// </summary>
public record LoginResponse(
    string Token,
    string Username,
    string FullName,
    string Role,
    DateTime ExpiresAt
);

/// <summary>
/// DTO para registro de novo usuário
/// </summary>
public record RegisterRequest(
    string Username,
    string Password,
    string FullName,
    string? Email,
    string Role = "AUDITOR"
);

/// <summary>
/// DTO para dados do usuário atual
/// </summary>
public record UserResponse(
    int Id,
    string Username,
    string FullName,
    string? Email,
    string Role,
    DateTime? LastLoginAt
);

/// <summary>
/// DTO para alteração de senha
/// </summary>
public record ChangePasswordRequest(
    string CurrentPassword,
    string NewPassword
);
