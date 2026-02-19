namespace AuditPlus.Domain.Entities;

/// <summary>
/// OWASP A09: Entidade de log de auditoria de segurança.
/// Registra eventos como login, lockout, alteração de senha, etc.
/// </summary>
public class AuditLog : BaseEntity
{
    /// <summary>
    /// Tipo do evento (LOGIN_SUCCESS, LOGIN_FAILURE, PASSWORD_CHANGE, LOCKOUT, etc.)
    /// </summary>
    public string EventType { get; set; } = string.Empty;
    
    /// <summary>
    /// Username envolvido no evento
    /// </summary>
    public string? Username { get; set; }
    
    /// <summary>
    /// Endereço IP de origem
    /// </summary>
    public string? IpAddress { get; set; }
    
    /// <summary>
    /// Detalhes adicionais do evento
    /// </summary>
    public string? Details { get; set; }
    
    /// <summary>
    /// Se o evento indica sucesso ou falha
    /// </summary>
    public bool Success { get; set; }
    
    /// <summary>
    /// Timestamp do evento
    /// </summary>
    public DateTime EventTimestamp { get; set; } = DateTime.UtcNow;
}
