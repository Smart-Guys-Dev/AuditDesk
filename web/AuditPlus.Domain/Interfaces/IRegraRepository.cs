using AuditPlus.Domain.Entities;
using AuditPlus.Domain.Enums;

namespace AuditPlus.Domain.Interfaces;

/// <summary>
/// Interface do repositório de regras.
/// Estende IRepository com operações específicas de Regra.
/// </summary>
public interface IRegraRepository : IRepository<Regra>
{
    /// <summary>
    /// Busca regra por código
    /// </summary>
    Task<Regra?> GetByCodigoAsync(string codigo);
    
    /// <summary>
    /// Busca regras ativas
    /// </summary>
    Task<IEnumerable<Regra>> GetAtivasAsync();
    
    /// <summary>
    /// Busca regras por categoria
    /// </summary>
    Task<IEnumerable<Regra>> GetByCategoriaAsync(RuleCategory categoria);
    
    /// <summary>
    /// Busca regras por grupo
    /// </summary>
    Task<IEnumerable<Regra>> GetByGrupoAsync(RuleGroup grupo);
    
    /// <summary>
    /// Busca regras ordenadas por prioridade
    /// </summary>
    Task<IEnumerable<Regra>> GetOrderedByPrioridadeAsync();
}
