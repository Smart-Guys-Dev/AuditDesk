using Microsoft.EntityFrameworkCore;
using AuditPlus.Domain.Entities;
using AuditPlus.Domain.Enums;
using AuditPlus.Domain.Interfaces;
using AuditPlus.Infrastructure.Data;

namespace AuditPlus.Infrastructure.Repositories;

/// <summary>
/// Implementação do repositório de regras.
/// Estende Repository base com operações específicas.
/// </summary>
public class RegraRepository : Repository<Regra>, IRegraRepository
{
    public RegraRepository(AppDbContext context) : base(context)
    {
    }
    
    /// <inheritdoc/>
    public async Task<Regra?> GetByCodigoAsync(string codigo)
    {
        return await _dbSet.FirstOrDefaultAsync(r => r.Codigo == codigo);
    }
    
    /// <inheritdoc/>
    public async Task<IEnumerable<Regra>> GetAtivasAsync()
    {
        return await _dbSet.Where(r => r.Ativo).OrderBy(r => r.Prioridade).ToListAsync();
    }
    
    /// <inheritdoc/>
    public async Task<IEnumerable<Regra>> GetByCategoriaAsync(RuleCategory categoria)
    {
        return await _dbSet.Where(r => r.Categoria == categoria).ToListAsync();
    }
    
    /// <inheritdoc/>
    public async Task<IEnumerable<Regra>> GetByGrupoAsync(RuleGroup grupo)
    {
        return await _dbSet.Where(r => r.Grupo == grupo).ToListAsync();
    }
    
    /// <inheritdoc/>
    public async Task<IEnumerable<Regra>> GetOrderedByPrioridadeAsync()
    {
        return await _dbSet.OrderBy(r => r.Prioridade).ToListAsync();
    }
}
