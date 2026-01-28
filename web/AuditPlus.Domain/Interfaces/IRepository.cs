using AuditPlus.Domain.Entities;

namespace AuditPlus.Domain.Interfaces;

/// <summary>
/// Interface base para repositórios.
/// Define operações CRUD genéricas.
/// </summary>
/// <typeparam name="T">Tipo da entidade</typeparam>
public interface IRepository<T> where T : BaseEntity
{
    /// <summary>
    /// Obtém entidade por ID
    /// </summary>
    Task<T?> GetByIdAsync(int id);
    
    /// <summary>
    /// Obtém todas as entidades
    /// </summary>
    Task<IEnumerable<T>> GetAllAsync();
    
    /// <summary>
    /// Adiciona nova entidade
    /// </summary>
    Task<T> AddAsync(T entity);
    
    /// <summary>
    /// Atualiza entidade existente
    /// </summary>
    Task UpdateAsync(T entity);
    
    /// <summary>
    /// Remove entidade
    /// </summary>
    Task DeleteAsync(int id);
    
    /// <summary>
    /// Verifica se existe entidade com o ID
    /// </summary>
    Task<bool> ExistsAsync(int id);
}
