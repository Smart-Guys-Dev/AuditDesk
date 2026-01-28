using AuditPlus.Domain.Entities;

namespace AuditPlus.Domain.Interfaces;

/// <summary>
/// Interface do repositório de usuários.
/// Estende IRepository com operações específicas de User.
/// </summary>
public interface IUserRepository : IRepository<User>
{
    /// <summary>
    /// Busca usuário por username
    /// </summary>
    Task<User?> GetByUsernameAsync(string username);
    
    /// <summary>
    /// Busca usuário por email
    /// </summary>
    Task<User?> GetByEmailAsync(string email);
    
    /// <summary>
    /// Busca usuários ativos
    /// </summary>
    Task<IEnumerable<User>> GetActiveUsersAsync();
    
    /// <summary>
    /// Verifica se username já existe
    /// </summary>
    Task<bool> UsernameExistsAsync(string username);
}
