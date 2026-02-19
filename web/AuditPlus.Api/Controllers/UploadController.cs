using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using AuditPlus.Domain.Interfaces;
using AuditPlus.Domain.Entities;

namespace AuditPlus.Api.Controllers;

/// <summary>
/// Controller para Upload e Processamento de XMLs.
/// Gerencia lotes de arquivos para validação.
/// </summary>
[ApiController]
[Route("api/[controller]")]
[Authorize]
public class UploadController : ControllerBase
{
    private readonly IExecucaoRepository _execucaoRepo;
    private readonly IWebHostEnvironment _env;
    private readonly ILogger<UploadController> _logger;
    
    public UploadController(
        IExecucaoRepository execucaoRepo,
        IWebHostEnvironment env,
        ILogger<UploadController> logger)
    {
        _execucaoRepo = execucaoRepo;
        _env = env;
        _logger = logger;
    }
    
    /// <summary>
    /// Upload de arquivos XML para processamento
    /// </summary>
    [HttpPost]
    [RequestSizeLimit(100_000_000)] // 100MB max
    public async Task<ActionResult<UploadResult>> UploadFiles(IFormFileCollection files)
    {
        if (files == null || files.Count == 0)
        {
            return BadRequest(new { message = "Nenhum arquivo enviado" });
        }
        
        // Criar pasta para este lote
        var loteId = Guid.NewGuid().ToString("N")[..8];
        var uploadPath = Path.Combine(_env.ContentRootPath, "uploads", loteId);
        Directory.CreateDirectory(uploadPath);
        
        var resultado = new UploadResult
        {
            LoteId = loteId,
            TotalArquivos = files.Count,
            ArquivosAceitos = 0,
            ArquivosRejeitados = 0,
            Arquivos = new List<ArquivoInfo>()
        };
        
        foreach (var file in files)
        {
            var info = new ArquivoInfo
            {
                Nome = file.FileName,
                Tamanho = file.Length
            };
            
            // Validar extensão
            if (!file.FileName.EndsWith(".xml", StringComparison.OrdinalIgnoreCase))
            {
                info.Status = "REJEITADO";
                info.Motivo = "Apenas arquivos XML são aceitos";
                resultado.ArquivosRejeitados++;
            }
            else
            {
                try
                {
                    var filePath = Path.Combine(uploadPath, file.FileName);
                    using var stream = new FileStream(filePath, FileMode.Create);
                    await file.CopyToAsync(stream);
                    
                    info.Status = "ACEITO";
                    resultado.ArquivosAceitos++;
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, "Erro ao salvar arquivo {FileName}", file.FileName);
                    info.Status = "ERRO";
                    info.Motivo = "Erro ao salvar arquivo";
                    resultado.ArquivosRejeitados++;
                }
            }
            
            resultado.Arquivos.Add(info);
        }
        
        // Criar registro de execução
        var execucao = new Execucao
        {
            TipoOperacao = "UPLOAD",
            Status = "PENDENTE",
            TotalArquivos = resultado.ArquivosAceitos,
            ArquivosSucesso = 0,
            ArquivosErro = 0,
            DataInicio = DateTime.UtcNow,
            CreatedAt = DateTime.UtcNow
        };
        
        await _execucaoRepo.AddAsync(execucao);
        resultado.ExecucaoId = execucao.Id;
        
        _logger.LogInformation("Upload concluído: Lote {LoteId}, {Aceitos}/{Total} arquivos", 
            loteId, resultado.ArquivosAceitos, resultado.TotalArquivos);
        
        return Ok(resultado);
    }
    
    /// <summary>
    /// Listar lotes de upload
    /// </summary>
    [HttpGet("lotes")]
    public async Task<ActionResult<IEnumerable<Execucao>>> GetLotes()
    {
        var execucoes = await _execucaoRepo.GetRecentAsync(50);
        return Ok(execucoes.Where(e => e.TipoOperacao == "UPLOAD" || e.TipoOperacao == "CORRECAO"));
    }
    
    /// <summary>
    /// Detalhes de um lote
    /// </summary>
    [HttpGet("lotes/{id}")]
    public async Task<ActionResult<Execucao>> GetLote(int id)
    {
        var execucao = await _execucaoRepo.GetByIdAsync(id);
        if (execucao == null)
            return NotFound();
        
        return Ok(execucao);
    }
}

// DTOs
public record UploadResult
{
    public string LoteId { get; set; } = string.Empty;
    public int ExecucaoId { get; set; }
    public int TotalArquivos { get; set; }
    public int ArquivosAceitos { get; set; }
    public int ArquivosRejeitados { get; set; }
    public List<ArquivoInfo> Arquivos { get; set; } = new();
}

public record ArquivoInfo
{
    public string Nome { get; set; } = string.Empty;
    public long Tamanho { get; set; }
    public string Status { get; set; } = string.Empty;
    public string? Motivo { get; set; }
}
