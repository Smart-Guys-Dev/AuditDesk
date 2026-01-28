namespace AuditPlus.Domain.Entities;

/// <summary>
/// Entidade de log de execução.
/// Registra cada operação de processamento de XMLs.
/// </summary>
public class Execucao : BaseEntity
{
    /// <summary>
    /// Tipo de operação: IMPORTACAO, VALIDACAO, CORRECAO, HASH
    /// </summary>
    public string TipoOperacao { get; set; } = string.Empty;
    
    /// <summary>
    /// Status da execução: INICIADO, CONCLUIDO, ERRO
    /// </summary>
    public string Status { get; set; } = "INICIADO";
    
    /// <summary>
    /// Total de arquivos processados
    /// </summary>
    public int TotalArquivos { get; set; }
    
    /// <summary>
    /// Arquivos processados com sucesso
    /// </summary>
    public int ArquivosSucesso { get; set; }
    
    /// <summary>
    /// Arquivos com erro
    /// </summary>
    public int ArquivosErro { get; set; }
    
    /// <summary>
    /// Data/hora de início
    /// </summary>
    public DateTime DataInicio { get; set; } = DateTime.UtcNow;
    
    /// <summary>
    /// Data/hora de término
    /// </summary>
    public DateTime? DataFim { get; set; }
    
    /// <summary>
    /// Duração em segundos
    /// </summary>
    public int? DuracaoSegundos { get; set; }
    
    /// <summary>
    /// ID do usuário que executou
    /// </summary>
    public int? UserId { get; set; }
    
    /// <summary>
    /// Navegação para o usuário
    /// </summary>
    public User? User { get; set; }
    
    /// <summary>
    /// Mensagem de erro (se houver)
    /// </summary>
    public string? MensagemErro { get; set; }
}
