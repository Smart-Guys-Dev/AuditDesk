namespace AuditPlus.Domain.Entities;

/// <summary>
/// Entidade de fatura.
/// Representa uma fatura importada para auditoria.
/// </summary>
public class Fatura : BaseEntity
{
    /// <summary>
    /// Número da fatura (único)
    /// </summary>
    public string NumeroFatura { get; set; } = string.Empty;
    
    /// <summary>
    /// Status: PENDENTE, ENVIADA, CANCELADA, GLOSADA
    /// </summary>
    public string Status { get; set; } = "PENDENTE";
    
    /// <summary>
    /// Código da Unimed
    /// </summary>
    public string? UnimedCodigo { get; set; }
    
    /// <summary>
    /// Nome da Unimed
    /// </summary>
    public string? UnimedNome { get; set; }
    
    /// <summary>
    /// Valor total da fatura
    /// </summary>
    public decimal Valor { get; set; }
    
    /// <summary>
    /// Competência no formato MM/YYYY
    /// </summary>
    public string? Competencia { get; set; }
    
    /// <summary>
    /// Responsável pela fatura
    /// </summary>
    public string? Responsavel { get; set; }
    
    /// <summary>
    /// Data de envio
    /// </summary>
    public DateTime? DataEnvio { get; set; }
    
    /// <summary>
    /// Data de importação no sistema
    /// </summary>
    public DateTime DataImportacao { get; set; } = DateTime.UtcNow;
    
    /// <summary>
    /// Se foi corrigida pelo AuditPlus
    /// </summary>
    public bool CorrigidaAuditPlus { get; set; } = false;
    
    /// <summary>
    /// Caminho do arquivo de origem
    /// </summary>
    public string? ArquivoOrigem { get; set; }
}
