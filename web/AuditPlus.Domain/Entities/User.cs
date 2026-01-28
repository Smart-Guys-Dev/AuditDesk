using AuditPlus.Domain.Enums;

namespace AuditPlus.Domain.Entities;

/// <summary>
/// Entidade de usuário do sistema.
/// Contém dados de autenticação e perfil.
/// </summary>
public class User : BaseEntity
{
    /// <summary>
    /// Nome de usuário para login (único)
    /// </summary>
    public string Username { get; set; } = string.Empty;
    
    /// <summary>
    /// Hash da senha (bcrypt)
    /// </summary>
    public string PasswordHash { get; set; } = string.Empty;
    
    /// <summary>
    /// Nome completo do usuário
    /// </summary>
    public string FullName { get; set; } = string.Empty;
    
    /// <summary>
    /// Email do usuário
    /// </summary>
    public string? Email { get; set; }
    
    /// <summary>
    /// Role/Perfil do usuário
    /// </summary>
    public UserRole Role { get; set; } = UserRole.AUDITOR;
    
    /// <summary>
    /// Se o usuário está ativo no sistema
    /// </summary>
    public bool IsActive { get; set; } = true;
    
    /// <summary>
    /// Data do último login
    /// </summary>
    public DateTime? LastLoginAt { get; set; }
    
    /// <summary>
    /// Número de tentativas de login falhas
    /// </summary>
    public int FailedLoginAttempts { get; set; } = 0;
    
    /// <summary>
    /// Data até quando a conta está bloqueada
    /// </summary>
    public DateTime? LockedUntil { get; set; }
}
