using AuditPlus.Domain.Enums;

namespace AuditPlus.Domain.Entities;

/// <summary>
/// Entidade de regra de auditoria.
/// Armazena as regras de validação/correção de XML TISS.
/// </summary>
public class Regra : BaseEntity
{
    /// <summary>
    /// Código único da regra (ex: REGRA_CPF_PRESTADOR_9134)
    /// </summary>
    public string Codigo { get; set; } = string.Empty;
    
    /// <summary>
    /// Nome descritivo da regra
    /// </summary>
    public string Nome { get; set; } = string.Empty;
    
    /// <summary>
    /// Descrição detalhada do que a regra faz
    /// </summary>
    public string? Descricao { get; set; }
    
    /// <summary>
    /// Categoria de impacto da regra
    /// </summary>
    public RuleCategory Categoria { get; set; }
    
    /// <summary>
    /// Grupo funcional da regra
    /// </summary>
    public RuleGroup Grupo { get; set; }
    
    /// <summary>
    /// Se a regra está ativa
    /// </summary>
    public bool Ativo { get; set; } = true;
    
    /// <summary>
    /// Prioridade de execução (menor = maior prioridade)
    /// </summary>
    public int Prioridade { get; set; } = 100;
    
    /// <summary>
    /// Condições da regra em formato JSON
    /// </summary>
    public string Condicoes { get; set; } = "{}";
    
    /// <summary>
    /// Ação a ser executada em formato JSON
    /// </summary>
    public string Acao { get; set; } = "{}";
    
    /// <summary>
    /// Mensagem de log quando a regra é aplicada com sucesso
    /// </summary>
    public string? LogSucesso { get; set; }
    
    /// <summary>
    /// Impacto financeiro estimado: BAIXO, MEDIO, ALTO
    /// </summary>
    public string ImpactoFinanceiro { get; set; } = "MEDIO";
    
    /// <summary>
    /// Se deve contabilizar no cálculo de ROI
    /// </summary>
    public bool ContabilizarRoi { get; set; } = true;
    
    /// <summary>
    /// Versão da regra para controle de alterações
    /// </summary>
    public int Versao { get; set; } = 1;
    
    /// <summary>
    /// Total de vezes que a regra foi aplicada
    /// </summary>
    public int TotalAplicacoes { get; set; }
    
    /// <summary>
    /// Total de glosas evitadas por esta regra
    /// </summary>
    public int TotalGlosasEvitadas { get; set; }
}
