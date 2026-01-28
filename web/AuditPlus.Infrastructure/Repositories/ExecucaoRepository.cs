using Microsoft.EntityFrameworkCore;
using AuditPlus.Domain.Entities;
using AuditPlus.Domain.Interfaces;
using AuditPlus.Infrastructure.Data;

namespace AuditPlus.Infrastructure.Repositories;

/// <summary>
/// Implementação do repositório de execuções.
/// Estende Repository base com operações específicas.
/// </summary>
public class ExecucaoRepository : Repository<Execucao>, IExecucaoRepository
{
    public ExecucaoRepository(AppDbContext context) : base(context)
    {
    }
    
    /// <inheritdoc/>
    public async Task<IEnumerable<Execucao>> GetByUserIdAsync(int userId)
    {
        return await _dbSet
            .Where(e => e.UserId == userId)
            .OrderByDescending(e => e.DataInicio)
            .ToListAsync();
    }
    
    /// <inheritdoc/>
    public async Task<IEnumerable<Execucao>> GetByTipoOperacaoAsync(string tipoOperacao)
    {
        return await _dbSet
            .Where(e => e.TipoOperacao == tipoOperacao)
            .OrderByDescending(e => e.DataInicio)
            .ToListAsync();
    }
    
    /// <inheritdoc/>
    public async Task<IEnumerable<Execucao>> GetRecentAsync(int count = 10)
    {
        return await _dbSet
            .Include(e => e.User)
            .OrderByDescending(e => e.DataInicio)
            .Take(count)
            .ToListAsync();
    }
    
    /// <inheritdoc/>
    public async Task<IEnumerable<Execucao>> GetByPeriodoAsync(DateTime inicio, DateTime fim)
    {
        return await _dbSet
            .Where(e => e.DataInicio >= inicio && e.DataInicio <= fim)
            .OrderByDescending(e => e.DataInicio)
            .ToListAsync();
    }
}
