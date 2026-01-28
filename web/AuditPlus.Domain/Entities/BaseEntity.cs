namespace AuditPlus.Domain.Entities;

/// <summary>
/// Entidade base com propriedades comuns a todas as entidades.
/// Implementa auditoria de criação e atualização.
/// </summary>
public abstract class BaseEntity
{
    /// <summary>
    /// Identificador único da entidade
    /// </summary>
    public int Id { get; set; }
    
    /// <summary>
    /// Data de criação do registro
    /// </summary>
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    
    /// <summary>
    /// Data da última atualização
    /// </summary>
    public DateTime? UpdatedAt { get; set; }
    
    /// <summary>
    /// Usuário que criou o registro
    /// </summary>
    public string? CreatedBy { get; set; }
    
    /// <summary>
    /// Usuário que atualizou o registro
    /// </summary>
    public string? UpdatedBy { get; set; }
}
