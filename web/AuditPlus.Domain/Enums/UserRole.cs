namespace AuditPlus.Domain.Enums;

/// <summary>
/// Roles de usuário do sistema.
/// Define os níveis de permissão.
/// </summary>
public enum UserRole
{
    /// <summary>
    /// Administrador do sistema - acesso total
    /// </summary>
    ADMIN,
    
    /// <summary>
    /// Auditor - acesso a funcionalidades de auditoria
    /// </summary>
    AUDITOR,
    
    /// <summary>
    /// Visualizador - apenas leitura
    /// </summary>
    VIEWER
}
