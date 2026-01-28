namespace AuditPlus.Domain.Enums;

/// <summary>
/// Categorias de impacto das regras de auditoria.
/// Define o tipo de glosa que a regra pode evitar.
/// </summary>
public enum RuleCategory
{
    /// <summary>
    /// Correções que evitam glosa da guia inteira
    /// </summary>
    GLOSA_GUIA,
    
    /// <summary>
    /// Correções que evitam glosa de item/procedimento específico
    /// </summary>
    GLOSA_ITEM,
    
    /// <summary>
    /// Validações de formato/estrutura do XML
    /// </summary>
    VALIDACAO,
    
    /// <summary>
    /// Otimizações sem impacto direto em glosa
    /// </summary>
    OTIMIZACAO
}
