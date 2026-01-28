namespace AuditPlus.Domain.Enums;

/// <summary>
/// Grupos funcionais de regras de auditoria.
/// Organiza as regras por área de atuação.
/// </summary>
public enum RuleGroup
{
    // Grupos de campo de atuação
    DATAS,
    VALORES,
    QUANTIDADES,
    CODIGOS,
    DUPLICIDADES,
    AUTORIZACAO,
    BENEFICIARIO,
    PRESTADOR,
    TISS,
    
    // Grupos funcionais
    EQUIPE_PROF,
    PARTICIPACAO,
    INTERNACAO,
    PROCEDIMENTOS,
    AUDITORIA,
    CNES,
    LAYOUT,
    CONVERSAO,
    TERAPIAS,
    
    OUTROS
}
