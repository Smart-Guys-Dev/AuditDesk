using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using AuditPlus.Infrastructure.Data;

namespace AuditPlus.Api.Controllers;

/// <summary>
/// Controller para Relatórios.
/// Fornece endpoints para geração de relatórios gerenciais.
/// </summary>
[ApiController]
[Route("api/[controller]")]
[Authorize]
public class RelatoriosController : ControllerBase
{
    private readonly AppDbContext _context;
    private readonly ILogger<RelatoriosController> _logger;
    
    public RelatoriosController(AppDbContext context, ILogger<RelatoriosController> logger)
    {
        _context = context;
        _logger = logger;
    }
    
    /// <summary>
    /// Relatório de glosas evitadas por período
    /// </summary>
    [HttpGet("glosas-evitadas")]
    public async Task<ActionResult<RelatorioGlosasEvitadas>> GetGlosasEvitadas(
        [FromQuery] DateTime? dataInicio,
        [FromQuery] DateTime? dataFim)
    {
        var inicio = dataInicio ?? DateTime.Today.AddMonths(-1);
        var fim = dataFim ?? DateTime.Today;
        
        var execucoes = await _context.Execucoes
            .Where(e => e.DataInicio >= inicio && e.DataInicio <= fim && e.Status == "CONCLUIDO")
            .ToListAsync();
        
        var relatorio = new RelatorioGlosasEvitadas
        {
            DataInicio = inicio,
            DataFim = fim,
            TotalExecucoes = execucoes.Count,
            TotalArquivosProcessados = execucoes.Sum(e => e.TotalArquivos),
            TotalCorrecoes = execucoes.Sum(e => e.TotalCorrecoes),
            ValorTotalEvitado = execucoes.Sum(e => e.ValorEconomizado),
            MediaPorExecucao = execucoes.Count > 0 
                ? execucoes.Average(e => e.ValorEconomizado) 
                : 0
        };
        
        return Ok(relatorio);
    }
    
    /// <summary>
    /// Relatório de regras por efetividade
    /// </summary>
    [HttpGet("regras-efetividade")]
    public async Task<ActionResult<IEnumerable<RegraEfetividade>>> GetRegrasEfetividade()
    {
        var regras = await _context.Regras
            .Where(r => r.Ativo)
            .Select(r => new RegraEfetividade
            {
                Codigo = r.Codigo,
                Nome = r.Nome,
                Categoria = r.Categoria.ToString(),
                TotalAplicacoes = r.TotalAplicacoes,
                TotalGlosasEvitadas = r.TotalGlosasEvitadas,
                TaxaEfetividade = r.TotalAplicacoes > 0 
                    ? Math.Round((double)r.TotalGlosasEvitadas / r.TotalAplicacoes * 100, 2) 
                    : 0
            })
            .OrderByDescending(r => r.TaxaEfetividade)
            .ToListAsync();
        
        return Ok(regras);
    }
    
    /// <summary>
    /// Resumo mensal de execuções
    /// </summary>
    [HttpGet("resumo-mensal")]
    public async Task<ActionResult<IEnumerable<ResumoMensal>>> GetResumoMensal(
        [FromQuery] int ano = 0)
    {
        var anoFiltro = ano > 0 ? ano : DateTime.Today.Year;
        
        var resumo = await _context.Execucoes
            .Where(e => e.DataInicio.Year == anoFiltro)
            .GroupBy(e => e.DataInicio.Month)
            .Select(g => new ResumoMensal
            {
                Mes = g.Key,
                MesNome = GetNomeMes(g.Key),
                TotalExecucoes = g.Count(),
                TotalArquivos = g.Sum(e => e.TotalArquivos),
                TotalCorrecoes = g.Sum(e => e.TotalCorrecoes),
                ValorEconomizado = g.Sum(e => e.ValorEconomizado),
                TaxaSucesso = Math.Round(
                    (double)g.Count(e => e.Status == "CONCLUIDO") / g.Count() * 100, 2)
            })
            .OrderBy(r => r.Mes)
            .ToListAsync();
        
        return Ok(resumo);
    }
    
    private static string GetNomeMes(int mes) => mes switch
    {
        1 => "Janeiro", 2 => "Fevereiro", 3 => "Março", 4 => "Abril",
        5 => "Maio", 6 => "Junho", 7 => "Julho", 8 => "Agosto",
        9 => "Setembro", 10 => "Outubro", 11 => "Novembro", 12 => "Dezembro",
        _ => "Desconhecido"
    };
}

// DTOs
public record RelatorioGlosasEvitadas
{
    public DateTime DataInicio { get; init; }
    public DateTime DataFim { get; init; }
    public int TotalExecucoes { get; init; }
    public int TotalArquivosProcessados { get; init; }
    public int TotalCorrecoes { get; init; }
    public decimal ValorTotalEvitado { get; init; }
    public decimal MediaPorExecucao { get; init; }
}

public record RegraEfetividade
{
    public string Codigo { get; init; } = string.Empty;
    public string Nome { get; init; } = string.Empty;
    public string Categoria { get; init; } = string.Empty;
    public int TotalAplicacoes { get; init; }
    public int TotalGlosasEvitadas { get; init; }
    public double TaxaEfetividade { get; init; }
}

public record ResumoMensal
{
    public int Mes { get; init; }
    public string MesNome { get; init; } = string.Empty;
    public int TotalExecucoes { get; init; }
    public int TotalArquivos { get; init; }
    public int TotalCorrecoes { get; init; }
    public decimal ValorEconomizado { get; init; }
    public double TaxaSucesso { get; init; }
}
