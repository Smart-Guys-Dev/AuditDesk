using Microsoft.EntityFrameworkCore;
using AuditPlus.Domain.Entities;
using AuditPlus.Domain.Interfaces;
using AuditPlus.Infrastructure.Data;

namespace AuditPlus.Infrastructure.Repositories;

/// <summary>
/// Implementação do repositório de usuários.
/// Estende Repository base com operações específicas.
/// </summary>
public class UserRepository : Repository<User>, IUserRepository
{
    public UserRepository(AppDbContext context) : base(context)
    {
    }
    
    /// <inheritdoc/>
    public async Task<User?> GetByUsernameAsync(string username)
    {
        return await _dbSet.FirstOrDefaultAsync(u => u.Username == username);
    }
    
    /// <inheritdoc/>
    public async Task<User?> GetByEmailAsync(string email)
    {
        return await _dbSet.FirstOrDefaultAsync(u => u.Email == email);
    }
    
    /// <inheritdoc/>
    public async Task<IEnumerable<User>> GetActiveUsersAsync()
    {
        return await _dbSet.Where(u => u.IsActive).ToListAsync();
    }
    
    /// <inheritdoc/>
    public async Task<bool> UsernameExistsAsync(string username)
    {
        return await _dbSet.AnyAsync(u => u.Username == username);
    }
}
