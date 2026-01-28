namespace AuditPlus.Domain.Enums;

/// <summary>
/// Grupos funcionais de regras de auditoria.
/// Organiza as regras por área de atuação.
/// </summary>
public enum RuleGroup
{
    /// <summary>
    /// Equipe Profissional - CPF, CBO, Conselho
    /// </summary>
    EQUIPE_PROF,
    
    /// <summary>
    /// Tipo de Participação - tp_Participacao
    /// </summary>
    PARTICIPACAO,
    
    /// <summary>
    /// Regras de Internação
    /// </summary>
    INTERNACAO,
    
    /// <summary>
    /// Procedimentos e Serviços
    /// </summary>
    PROCEDIMENTOS,
    
    /// <summary>
    /// Dados de Auditoria
    /// </summary>
    AUDITORIA,
    
    /// <summary>
    /// CNES de Prestadores
    /// </summary>
    CNES,
    
    /// <summary>
    /// Ordem/estrutura de XML
    /// </summary>
    LAYOUT,
    
    /// <summary>
    /// Conversão PJ para PF
    /// </summary>
    CONVERSAO,
    
    /// <summary>
    /// Terapias Seriadas
    /// </summary>
    TERAPIAS,
    
    /// <summary>
    /// Outras regras não categorizadas
    /// </summary>
    OUTROS
}
