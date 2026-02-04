using AuditPlus.Domain.Entities;

namespace AuditPlus.Domain.Entities;

/// <summary>
/// Representa uma regra de validação com suas condições e ações.
/// Mapeamento do formato JSON do desktop para o banco.
/// </summary>
public class ValidationRule : BaseEntity
{
    /// <summary>
    /// Código único da regra (ex: REGRA_CPF_PRESTADOR_24018)
    /// </summary>
    public string Codigo { get; set; } = string.Empty;
    
    /// <summary>
    /// Descrição legível da regra
    /// </summary>
    public string Descricao { get; set; } = string.Empty;
    
    /// <summary>
    /// Grupo da regra (CPF, CNES, Equipe, etc.)
    /// </summary>
    public string Grupo { get; set; } = string.Empty;
    
    /// <summary>
    /// Tipo de elemento XML alvo (procedimentosExecutados, guia_SP_SADT, etc.)
    /// </summary>
    public string TipoElemento { get; set; } = string.Empty;
    
    /// <summary>
    /// Condições em formato JSON (preserva estrutura original)
    /// </summary>
    public string CondicoesJson { get; set; } = "{}";
    
    /// <summary>
    /// Ações em formato JSON
    /// </summary>
    public string AcoesJson { get; set; } = "{}";
    
    /// <summary>
    /// Mensagem de log quando regra é aplicada
    /// </summary>
    public string LogSucesso { get; set; } = string.Empty;
    
    /// <summary>
    /// Categoria de impacto (VALIDACAO, GLOSA_GUIA, GLOSA_ITEM, OTIMIZACAO)
    /// </summary>
    public string Categoria { get; set; } = "VALIDACAO";
    
    /// <summary>
    /// Nível de impacto (ALTO, MEDIO, BAIXO)
    /// </summary>
    public string Impacto { get; set; } = "MEDIO";
    
    /// <summary>
    /// Se a regra está ativa
    /// </summary>
    public bool Ativo { get; set; } = true;
    
    /// <summary>
    /// Ordem de prioridade (menor = maior prioridade)
    /// </summary>
    public int Prioridade { get; set; } = 100;
    
    /// <summary>
    /// Contador de vezes que a regra foi aplicada
    /// </summary>
    public int TotalAplicacoes { get; set; } = 0;
}
