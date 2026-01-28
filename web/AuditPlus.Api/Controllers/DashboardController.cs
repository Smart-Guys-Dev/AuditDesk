using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using AuditPlus.Infrastructure.Data;
using AuditPlus.Domain.Interfaces;

namespace AuditPlus.Api.Controllers;

/// <summary>
/// Controller para o Dashboard.
/// Fornece estatísticas e métricas do sistema.
/// </summary>
[ApiController]
[Route("api/[controller]")]
public class DashboardController : ControllerBase
{
    private readonly AppDbContext _context;
    private readonly IRegraRepository _regraRepository;
    private readonly IExecucaoRepository _execucaoRepository;
    private readonly ILogger<DashboardController> _logger;
    
    public DashboardController(
        AppDbContext context,
        IRegraRepository regraRepository,
        IExecucaoRepository execucaoRepository,
        ILogger<DashboardController> logger)
    {
        _context = context;
        _regraRepository = regraRepository;
        _execucaoRepository = execucaoRepository;
        _logger = logger;
    }
    
    /// <summary>
    /// Obtém estatísticas gerais do sistema
    /// </summary>
    [HttpGet("stats")]
    public async Task<ActionResult<DashboardStats>> GetStats()
    {
        var stats = new DashboardStats
        {
            TotalRegras = await _context.Regras.CountAsync(),
            RegrasAtivas = await _context.Regras.CountAsync(r => r.Ativo),
            TotalExecucoes = await _context.Execucoes.CountAsync(),
            TotalFaturas = await _context.Faturas.CountAsync(),
            ExecucoesSucesso = await _context.Execucoes.CountAsync(e => e.Status == "CONCLUIDO"),
            ExecucoesErro = await _context.Execucoes.CountAsync(e => e.Status == "ERRO"),
            TotalArquivosProcessados = await _context.Execucoes.SumAsync(e => e.TotalArquivos),
            UltimaExecucao = await _context.Execucoes
                .OrderByDescending(e => e.DataInicio)
                .Select(e => e.DataInicio)
                .FirstOrDefaultAsync()
        };
        
        // Taxa de sucesso
        if (stats.TotalExecucoes > 0)
        {
            stats.TaxaSucesso = Math.Round(
                (double)stats.ExecucoesSucesso / stats.TotalExecucoes * 100, 2);
        }
        
        return Ok(stats);
    }
    
    /// <summary>
    /// Obtém as últimas execuções
    /// </summary>
    [HttpGet("execucoes-recentes")]
    public async Task<ActionResult<IEnumerable<object>>> GetExecucoesRecentes([FromQuery] int count = 10)
    {
        var execucoes = await _execucaoRepository.GetRecentAsync(count);
        return Ok(execucoes);
    }
    
    /// <summary>
    /// Obtém contagem de regras por categoria
    /// </summary>
    [HttpGet("regras-por-categoria")]
    public async Task<ActionResult<IEnumerable<object>>> GetRegrasPorCategoria()
    {
        var result = await _context.Regras
            .GroupBy(r => r.Categoria)
            .Select(g => new 
            { 
                Categoria = g.Key.ToString(), 
                Quantidade = g.Count() 
            })
            .ToListAsync();
            
        return Ok(result);
    }
    
    /// <summary>
    /// Obtém contagem de regras por grupo
    /// </summary>
    [HttpGet("regras-por-grupo")]
    public async Task<ActionResult<IEnumerable<object>>> GetRegrasPorGrupo()
    {
        var result = await _context.Regras
            .GroupBy(r => r.Grupo)
            .Select(g => new 
            { 
                Grupo = g.Key.ToString(), 
                Quantidade = g.Count() 
            })
            .ToListAsync();
            
        return Ok(result);
    }
}

/// <summary>
/// DTO para estatísticas do dashboard
/// </summary>
public record DashboardStats
{
    public int TotalRegras { get; set; }
    public int RegrasAtivas { get; set; }
    public int TotalExecucoes { get; set; }
    public int TotalFaturas { get; set; }
    public int ExecucoesSucesso { get; set; }
    public int ExecucoesErro { get; set; }
    public int TotalArquivosProcessados { get; set; }
    public double TaxaSucesso { get; set; }
    public DateTime? UltimaExecucao { get; set; }
}
