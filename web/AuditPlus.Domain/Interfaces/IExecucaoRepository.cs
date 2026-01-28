using AuditPlus.Domain.Entities;

namespace AuditPlus.Domain.Interfaces;

/// <summary>
/// Interface do repositório de execuções.
/// Estende IRepository com operações específicas de Execucao.
/// </summary>
public interface IExecucaoRepository : IRepository<Execucao>
{
    /// <summary>
    /// Busca execuções por usuário
    /// </summary>
    Task<IEnumerable<Execucao>> GetByUserIdAsync(int userId);
    
    /// <summary>
    /// Busca execuções por tipo de operação
    /// </summary>
    Task<IEnumerable<Execucao>> GetByTipoOperacaoAsync(string tipoOperacao);
    
    /// <summary>
    /// Busca execuções recentes (últimas N)
    /// </summary>
    Task<IEnumerable<Execucao>> GetRecentAsync(int count = 10);
    
    /// <summary>
    /// Busca execuções em um período
    /// </summary>
    Task<IEnumerable<Execucao>> GetByPeriodoAsync(DateTime inicio, DateTime fim);
}
