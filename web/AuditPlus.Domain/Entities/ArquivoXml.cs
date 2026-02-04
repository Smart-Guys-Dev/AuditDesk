namespace AuditPlus.Domain.Entities;

/// <summary>
/// Representa um arquivo XML dentro de um lote de processamento.
/// </summary>
public class ArquivoXml : BaseEntity
{
    /// <summary>
    /// ID da execução/lote ao qual pertence
    /// </summary>
    public int ExecucaoId { get; set; }
    
    /// <summary>
    /// Nome do arquivo
    /// </summary>
    public string NomeArquivo { get; set; } = string.Empty;
    
    /// <summary>
    /// Caminho completo do arquivo
    /// </summary>
    public string CaminhoArquivo { get; set; } = string.Empty;
    
    /// <summary>
    /// Hash MD5 do conteúdo original
    /// </summary>
    public string HashOriginal { get; set; } = string.Empty;
    
    /// <summary>
    /// Hash MD5 após correções
    /// </summary>
    public string? HashCorrigido { get; set; }
    
    /// <summary>
    /// Tamanho em bytes
    /// </summary>
    public long TamanhoBytes { get; set; }
    
    /// <summary>
    /// Status: PENDENTE, VALIDADO, CORRIGIDO, ERRO
    /// </summary>
    public string Status { get; set; } = "PENDENTE";
    
    /// <summary>
    /// Número de regras aplicadas
    /// </summary>
    public int RegrasAplicadas { get; set; } = 0;
    
    /// <summary>
    /// Mensagens de log do processamento
    /// </summary>
    public string? LogProcessamento { get; set; }
    
    /// <summary>
    /// Caminho do arquivo após correções
    /// </summary>
    public string? CaminhoCorrigido { get; set; }
    
    /// <summary>
    /// Navegação para Execução
    /// </summary>
    public Execucao? Execucao { get; set; }
}
