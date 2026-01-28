using Microsoft.EntityFrameworkCore;
using AuditPlus.Domain.Entities;
using AuditPlus.Domain.Interfaces;
using AuditPlus.Infrastructure.Data;

namespace AuditPlus.Infrastructure.Repositories;

/// <summary>
/// Implementação base do repositório genérico.
/// Fornece operações CRUD básicas usando EF Core.
/// </summary>
/// <typeparam name="T">Tipo da entidade</typeparam>
public class Repository<T> : IRepository<T> where T : BaseEntity
{
    protected readonly AppDbContext _context;
    protected readonly DbSet<T> _dbSet;
    
    public Repository(AppDbContext context)
    {
        _context = context;
        _dbSet = context.Set<T>();
    }
    
    /// <inheritdoc/>
    public virtual async Task<T?> GetByIdAsync(int id)
    {
        return await _dbSet.FindAsync(id);
    }
    
    /// <inheritdoc/>
    public virtual async Task<IEnumerable<T>> GetAllAsync()
    {
        return await _dbSet.ToListAsync();
    }
    
    /// <inheritdoc/>
    public virtual async Task<T> AddAsync(T entity)
    {
        await _dbSet.AddAsync(entity);
        await _context.SaveChangesAsync();
        return entity;
    }
    
    /// <inheritdoc/>
    public virtual async Task UpdateAsync(T entity)
    {
        _dbSet.Update(entity);
        await _context.SaveChangesAsync();
    }
    
    /// <inheritdoc/>
    public virtual async Task DeleteAsync(int id)
    {
        var entity = await GetByIdAsync(id);
        if (entity != null)
        {
            _dbSet.Remove(entity);
            await _context.SaveChangesAsync();
        }
    }
    
    /// <inheritdoc/>
    public virtual async Task<bool> ExistsAsync(int id)
    {
        return await _dbSet.AnyAsync(e => e.Id == id);
    }
}
