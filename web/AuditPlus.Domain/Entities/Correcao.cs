namespace AuditPlus.Domain.Entities;

/// <summary>
/// Representa uma correção aplicada a um arquivo XML.
/// </summary>
public class Correcao : BaseEntity
{
    /// <summary>
    /// ID do arquivo XML
    /// </summary>
    public int ArquivoXmlId { get; set; }
    
    /// <summary>
    /// ID da regra aplicada
    /// </summary>
    public int ValidationRuleId { get; set; }
    
    /// <summary>
    /// Código da regra (para referência rápida)
    /// </summary>
    public string CodigoRegra { get; set; } = string.Empty;
    
    /// <summary>
    /// Elemento XML afetado (XPath)
    /// </summary>
    public string ElementoAfetado { get; set; } = string.Empty;
    
    /// <summary>
    /// Valor anterior (antes da correção)
    /// </summary>
    public string? ValorAnterior { get; set; }
    
    /// <summary>
    /// Novo valor (após correção)
    /// </summary>
    public string? ValorNovo { get; set; }
    
    /// <summary>
    /// Tipo de ação aplicada
    /// </summary>
    public string TipoAcao { get; set; } = string.Empty;
    
    /// <summary>
    /// Status: PENDENTE, APLICADO, REJEITADO
    /// </summary>
    public string Status { get; set; } = "PENDENTE";
    
    /// <summary>
    /// Indica se a correção foi aplicada ao arquivo
    /// </summary>
    public bool Aplicada { get; set; } = false;
    
    /// <summary>
    /// Data em que a correção foi aplicada
    /// </summary>
    public DateTime? DataAplicacao { get; set; }
    
    /// <summary>
    /// Navegação
    /// </summary>
    public ArquivoXml? ArquivoXml { get; set; }
    public ValidationRule? ValidationRule { get; set; }
}
