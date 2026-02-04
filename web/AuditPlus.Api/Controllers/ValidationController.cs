using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using AuditPlus.Application.Services;
using AuditPlus.Infrastructure.Data;
using Microsoft.EntityFrameworkCore;

namespace AuditPlus.Api.Controllers;

/// <summary>
/// Controller para validação e processamento de XMLs.
/// </summary>
[ApiController]
[Route("api/[controller]")]
[Authorize]
public class ValidationController : ControllerBase
{
    private readonly XmlValidationService _validationService;
    private readonly HashCalculatorService _hashService;
    private readonly AppDbContext _context;
    private readonly ILogger<ValidationController> _logger;
    private readonly IWebHostEnvironment _env;
    
    public ValidationController(
        XmlValidationService validationService,
        HashCalculatorService hashService,
        AppDbContext context,
        ILogger<ValidationController> logger,
        IWebHostEnvironment env)
    {
        _validationService = validationService;
        _hashService = hashService;
        _context = context;
        _logger = logger;
        _env = env;
    }
    
    /// <summary>
    /// Faz upload de arquivos ZIP para processamento posterior
    /// </summary>
    [HttpPost("upload")]
    [RequestSizeLimit(100_000_000)] // 100MB
    public async Task<ActionResult> UploadArquivos([FromForm] List<IFormFile> arquivos)
    {
        if (arquivos == null || arquivos.Count == 0)
            return BadRequest(new { message = "Nenhum arquivo enviado" });
        
        var pastaUploads = Path.Combine(_env.ContentRootPath, "uploads", DateTime.Now.ToString("yyyyMMdd_HHmmss"));
        Directory.CreateDirectory(pastaUploads);
        
        var arquivosSalvos = new List<string>();
        var erros = new List<string>();
        
        foreach (var arquivo in arquivos)
        {
            try
            {
                // Aceitar .zip, .051 e .xml
                var extensao = Path.GetExtension(arquivo.FileName).ToLowerInvariant();
                if (extensao != ".zip" && extensao != ".051" && extensao != ".xml")
                {
                    erros.Add($"{arquivo.FileName}: tipo não suportado (use .zip, .051 ou .xml)");
                    continue;
                }
                
                var caminhoDestino = Path.Combine(pastaUploads, arquivo.FileName);
                using var stream = new FileStream(caminhoDestino, FileMode.Create);
                await arquivo.CopyToAsync(stream);
                
                arquivosSalvos.Add(arquivo.FileName);
                _logger.LogInformation("Upload: {Arquivo} ({Size} bytes)", arquivo.FileName, arquivo.Length);
            }
            catch (Exception ex)
            {
                erros.Add($"{arquivo.FileName}: {ex.Message}");
            }
        }
        
        return Ok(new
        {
            sucesso = arquivosSalvos.Count > 0,
            totalArquivos = arquivosSalvos.Count,
            arquivos = arquivosSalvos,
            erros = erros,
            pastaUpload = pastaUploads
        });
    }
    
    /// <summary>
    /// Processa um lote de arquivos já uploadeados
    /// </summary>
    [HttpPost("processar/{execucaoId}")]
    public async Task<ActionResult<ValidationResult>> ProcessarLote(int execucaoId)
    {
        // Buscar execução
        var execucao = await _context.Execucoes.FindAsync(execucaoId);
        if (execucao == null)
            return NotFound(new { message = "Execução não encontrada" });
        
        // Determinar pasta de uploads
        var pastaUploads = Path.Combine(_env.ContentRootPath, "uploads");
        
        // Buscar pasta do lote (pelo pattern do loteId)
        var pastasLote = Directory.GetDirectories(pastaUploads, "*", SearchOption.TopDirectoryOnly);
        
        if (pastasLote.Length == 0)
            return BadRequest(new { message = "Nenhuma pasta de lote encontrada" });
        
        // Pegar a pasta mais recente
        var pastaLote = pastasLote
            .OrderByDescending(d => Directory.GetCreationTime(d))
            .First();
        
        _logger.LogInformation("Processando lote em: {Pasta}", pastaLote);
        
        // Processar
        var resultado = await _validationService.ProcessarLoteAsync(execucaoId, pastaLote);
        
        // Atualizar execução
        execucao.Status = resultado.Sucesso ? "CONCLUIDO" : "ERRO";
        execucao.ArquivosSucesso = resultado.ArquivosModificados;
        execucao.ArquivosErro = resultado.Erros.Count;
        execucao.TotalCorrecoes = resultado.TotalCorrecoes;
        execucao.DataFim = DateTime.UtcNow;
        
        await _context.SaveChangesAsync();
        
        return Ok(resultado);
    }
    
    /// <summary>
    /// Preview das correções que seriam aplicadas (sem salvar)
    /// </summary>
    [HttpGet("preview/{execucaoId}")]
    public async Task<ActionResult<PreviewResult>> PreviewCorrecoes(int execucaoId)
    {
        var arquivos = await _context.ArquivosXml
            .Where(a => a.ExecucaoId == execucaoId)
            .ToListAsync();
        
        var correcoes = await _context.Correcoes
            .Where(c => arquivos.Select(a => a.Id).Contains(c.ArquivoXmlId))
            .Include(c => c.ValidationRule)
            .ToListAsync();
        
        var preview = new PreviewResult
        {
            ExecucaoId = execucaoId,
            TotalArquivos = arquivos.Count,
            TotalCorrecoes = correcoes.Count,
            Arquivos = arquivos.Select(a => new ArquivoPreview
            {
                Id = a.Id,
                Nome = a.NomeArquivo,
                Status = a.Status,
                RegrasAplicadas = a.RegrasAplicadas,
                Correcoes = correcoes
                    .Where(c => c.ArquivoXmlId == a.Id)
                    .Select(c => new CorrecaoPreview
                    {
                        Regra = c.CodigoRegra,
                        Elemento = c.ElementoAfetado,
                        Antes = c.ValorAnterior ?? "",
                        Depois = c.ValorNovo ?? "",
                        Acao = c.TipoAcao
                    })
                    .ToList()
            }).ToList()
        };
        
        return Ok(preview);
    }
    
    /// <summary>
    /// Lista regras de validação ativas
    /// </summary>
    [HttpGet("regras")]
    public async Task<ActionResult<IEnumerable<object>>> GetRegras()
    {
        var regras = await _context.ValidationRules
            .Where(r => r.Ativo)
            .OrderBy(r => r.Grupo)
            .ThenBy(r => r.Prioridade)
            .Select(r => new
            {
                r.Id,
                r.Codigo,
                r.Descricao,
                r.Grupo,
                r.Categoria,
                r.Impacto,
                r.Prioridade,
                r.TotalAplicacoes,
                r.Ativo
            })
            .ToListAsync();
        
        return Ok(regras);
    }
    
    /// <summary>
    /// Estatísticas de validação
    /// </summary>
    [HttpGet("stats")]
    public async Task<ActionResult<object>> GetStats()
    {
        var totalRegras = await _context.ValidationRules.CountAsync();
        var regrasAtivas = await _context.ValidationRules.CountAsync(r => r.Ativo);
        var totalCorrecoes = await _context.Correcoes.CountAsync();
        var arquivosProcessados = await _context.ArquivosXml.CountAsync();
        
        var topRegras = await _context.ValidationRules
            .OrderByDescending(r => r.TotalAplicacoes)
            .Take(5)
            .Select(r => new { r.Codigo, r.TotalAplicacoes })
            .ToListAsync();
        
        return Ok(new
        {
            totalRegras,
            regrasAtivas,
            totalCorrecoes,
            arquivosProcessados,
            topRegras
        });
    }
    
    /// <summary>
    /// Aplica as correções definitivamente aos arquivos XML.
    /// Faz backup dos originais antes de aplicar.
    /// </summary>
    [HttpPost("aplicar/{execucaoId}")]
    public async Task<ActionResult<AplicarResult>> AplicarCorrecoes(int execucaoId)
    {
        var execucao = await _context.Execucoes.FindAsync(execucaoId);
        if (execucao == null)
            return NotFound(new { message = "Execução não encontrada" });
        
        // Buscar arquivos da execução
        var arquivos = await _context.ArquivosXml
            .Where(a => a.ExecucaoId == execucaoId)
            .ToListAsync();
        
        if (!arquivos.Any())
            return BadRequest(new { message = "Nenhum arquivo encontrado para esta execução" });
        
        // Definir pastas
        var pastaUploads = Path.Combine(_env.ContentRootPath, "uploads");
        var pastaBackup = Path.Combine(_env.ContentRootPath, "backups", $"exec_{execucaoId}_{DateTime.Now:yyyyMMdd_HHmmss}");
        var pastaCorrigidos = Path.Combine(_env.ContentRootPath, "corrigidos", $"exec_{execucaoId}");
        
        // Criar pastas
        Directory.CreateDirectory(pastaBackup);
        Directory.CreateDirectory(pastaCorrigidos);
        
        int arquivosAplicados = 0;
        var erros = new List<string>();
        
        foreach (var arquivo in arquivos)
        {
            try
            {
                // Buscar arquivo original
                var caminhoOriginal = Path.Combine(pastaUploads, arquivo.CaminhoArquivo ?? arquivo.NomeArquivo);
                
                if (!System.IO.File.Exists(caminhoOriginal))
                {
                    erros.Add($"{arquivo.NomeArquivo}: Arquivo original não encontrado");
                    continue;
                }
                
                // Fazer backup
                var caminhoBackup = Path.Combine(pastaBackup, arquivo.NomeArquivo);
                System.IO.File.Copy(caminhoOriginal, caminhoBackup, true);
                
                // Buscar correções pendentes
                var correcoes = await _context.Correcoes
                    .Where(c => c.ArquivoXmlId == arquivo.Id && !c.Aplicada)
                    .ToListAsync();
                
                if (!correcoes.Any())
                {
                    _logger.LogInformation("Arquivo {Nome} não tem correções pendentes", arquivo.NomeArquivo);
                    continue;
                }
                
                // Aplicar correções ao XML
                var xmlContent = await System.IO.File.ReadAllTextAsync(caminhoOriginal);
                var doc = System.Xml.Linq.XDocument.Parse(xmlContent);
                
                foreach (var correcao in correcoes)
                {
                    // Localizar elemento e aplicar correção
                    var elementos = doc.Descendants()
                        .Where(e => e.Name.LocalName == correcao.ElementoAfetado)
                        .ToList();
                    
                    foreach (var elem in elementos)
                    {
                        if (correcao.TipoAcao == "SUBSTITUIR" && elem.Value == correcao.ValorAnterior)
                        {
                            elem.Value = correcao.ValorNovo ?? "";
                        }
                    }
                    
                    // Marcar correção como aplicada
                    correcao.Aplicada = true;
                    correcao.DataAplicacao = DateTime.UtcNow;
                }
                
                // Salvar XML corrigido
                var caminhoCorrigido = Path.Combine(pastaCorrigidos, arquivo.NomeArquivo);
                await System.IO.File.WriteAllTextAsync(caminhoCorrigido, doc.ToString());
                
                // Atualizar status do arquivo
                arquivo.Status = "CORRIGIDO";
                arquivo.CaminhoCorrigido = caminhoCorrigido;
                
                arquivosAplicados++;
                _logger.LogInformation("Arquivo {Nome} corrigido com {Total} correções", arquivo.NomeArquivo, correcoes.Count);
            }
            catch (Exception ex)
            {
                erros.Add($"{arquivo.NomeArquivo}: {ex.Message}");
                _logger.LogError(ex, "Erro ao aplicar correções em {Nome}", arquivo.NomeArquivo);
            }
        }
        
        // Atualizar execução
        execucao.Status = erros.Any() ? "PARCIAL" : "APLICADO";
        execucao.DataFim = DateTime.UtcNow;
        
        await _context.SaveChangesAsync();
        
        return Ok(new AplicarResult
        {
            ExecucaoId = execucaoId,
            ArquivosAplicados = arquivosAplicados,
            TotalArquivos = arquivos.Count,
            PastaBackup = pastaBackup,
            PastaCorrigidos = pastaCorrigidos,
            Erros = erros,
            Sucesso = !erros.Any()
        });
    }
    
    /// <summary>
    /// Exporta os XMLs corrigidos em um arquivo ZIP.
    /// </summary>
    [HttpGet("export/{execucaoId}")]
    public async Task<IActionResult> ExportarZip(int execucaoId)
    {
        var pastaCorrigidos = Path.Combine(_env.ContentRootPath, "corrigidos", $"exec_{execucaoId}");
        
        if (!Directory.Exists(pastaCorrigidos))
            return NotFound(new { message = "Nenhum arquivo corrigido encontrado. Execute 'aplicar' primeiro." });
        
        var arquivos = Directory.GetFiles(pastaCorrigidos, "*.xml");
        
        if (arquivos.Length == 0)
            return NotFound(new { message = "Pasta de corrigidos está vazia" });
        
        // Criar ZIP em memória
        using var memoryStream = new MemoryStream();
        using (var archive = new System.IO.Compression.ZipArchive(memoryStream, System.IO.Compression.ZipArchiveMode.Create, true))
        {
            foreach (var arquivo in arquivos)
            {
                var nomeArquivo = Path.GetFileName(arquivo);
                var entry = archive.CreateEntry(nomeArquivo, System.IO.Compression.CompressionLevel.Optimal);
                
                using var entryStream = entry.Open();
                using var fileStream = System.IO.File.OpenRead(arquivo);
                await fileStream.CopyToAsync(entryStream);
            }
        }
        
        memoryStream.Position = 0;
        
        var nomeZip = $"xmls_corrigidos_exec_{execucaoId}_{DateTime.Now:yyyyMMdd_HHmmss}.zip";
        
        _logger.LogInformation("Exportando {Count} arquivos para {Nome}", arquivos.Length, nomeZip);
        
        return File(memoryStream.ToArray(), "application/zip", nomeZip);
    }
    
    /// <summary>
    /// Exporta os XMLs corrigidos em formato PTU (cada XML em seu próprio ZIP).
    /// Estrutura: Validacao_CMB/arquivo1.zip, arquivo2.zip, ...
    /// Cada ZIP interno contém apenas 1 arquivo XML com extensão .051
    /// </summary>
    [HttpGet("export-ptu/{execucaoId}")]
    public async Task<IActionResult> ExportarZipPtu(int execucaoId)
    {
        var pastaCorrigidos = Path.Combine(_env.ContentRootPath, "corrigidos", $"exec_{execucaoId}");
        
        if (!Directory.Exists(pastaCorrigidos))
            return NotFound(new { message = "Nenhum arquivo corrigido encontrado. Execute 'aplicar' primeiro." });
        
        var arquivos = Directory.GetFiles(pastaCorrigidos, "*.xml");
        
        if (arquivos.Length == 0)
            return NotFound(new { message = "Pasta de corrigidos está vazia" });
        
        // Criar ZIP mestre em memória
        using var memoryStream = new MemoryStream();
        using (var masterArchive = new System.IO.Compression.ZipArchive(memoryStream, System.IO.Compression.ZipArchiveMode.Create, true))
        {
            foreach (var arquivo in arquivos)
            {
                var nomeArquivo = Path.GetFileNameWithoutExtension(arquivo);
                var nomeZipInterno = $"Validacao_CMB/{nomeArquivo}.zip";
                
                // Criar ZIP interno para cada arquivo
                using var zipInternoStream = new MemoryStream();
                using (var zipInterno = new System.IO.Compression.ZipArchive(zipInternoStream, System.IO.Compression.ZipArchiveMode.Create, true))
                {
                    // Adicionar XML com extensão .051 (padrão PTU)
                    var nome051 = nomeArquivo + ".051";
                    var entryInterno = zipInterno.CreateEntry(nome051, System.IO.Compression.CompressionLevel.Optimal);
                    
                    using var entryStream = entryInterno.Open();
                    using var fileStream = System.IO.File.OpenRead(arquivo);
                    await fileStream.CopyToAsync(entryStream);
                }
                
                // Adicionar ZIP interno ao ZIP mestre
                zipInternoStream.Position = 0;
                var entryMestre = masterArchive.CreateEntry(nomeZipInterno, System.IO.Compression.CompressionLevel.NoCompression);
                using var mestreEntryStream = entryMestre.Open();
                await zipInternoStream.CopyToAsync(mestreEntryStream);
            }
        }
        
        memoryStream.Position = 0;
        
        var nomeZip = $"Validacao_CMB_exec_{execucaoId}_{DateTime.Now:yyyyMMdd_HHmmss}.zip";
        
        _logger.LogInformation("Exportando {Count} arquivos PTU para {Nome}", arquivos.Length, nomeZip);
        
        return File(memoryStream.ToArray(), "application/zip", nomeZip);
    }
    
    /// <summary>
    /// Recalcula o hash MD5 dos XMLs corrigidos (lógica PTU).
    /// Atualiza a tag <hash> dentro de <GuiaCobrancaUtilizacao>.
    /// </summary>
    [HttpPost("hash/{execucaoId}")]
    public async Task<ActionResult<HashResult>> RecalcularHash(int execucaoId)
    {
        var execucao = await _context.Execucoes.FindAsync(execucaoId);
        if (execucao == null)
            return NotFound($"Execução {execucaoId} não encontrada");
        
        // Buscar arquivos corrigidos
        var arquivos = await _context.ArquivosXml
            .Where(a => a.ExecucaoId == execucaoId && a.CaminhoCorrigido != null)
            .ToListAsync();
        
        if (!arquivos.Any())
            return BadRequest("Nenhum arquivo corrigido encontrado para recalcular hash");
        
        var resultado = new HashResult
        {
            ExecucaoId = execucaoId,
            TotalArquivos = arquivos.Count
        };
        
        foreach (var arquivo in arquivos)
        {
            try
            {
                if (!System.IO.File.Exists(arquivo.CaminhoCorrigido))
                {
                    resultado.Erros.Add($"{arquivo.NomeArquivo}: arquivo corrigido não encontrado");
                    continue;
                }
                
                // Ler conteúdo do XML corrigido
                var xmlContent = await System.IO.File.ReadAllTextAsync(arquivo.CaminhoCorrigido!);
                
                // Calcular e atualizar hash
                var (xmlAtualizado, novoHash) = _hashService.CalcularEAtualizarHash(xmlContent);
                
                if (novoHash == null)
                {
                    resultado.Erros.Add($"{arquivo.NomeArquivo}: erro ao calcular hash");
                    continue;
                }
                
                // Salvar XML com hash atualizado
                await System.IO.File.WriteAllTextAsync(arquivo.CaminhoCorrigido!, xmlAtualizado);
                
                resultado.ArquivosProcessados++;
                resultado.Hashes.Add(new HashInfo
                {
                    Arquivo = arquivo.NomeArquivo,
                    Hash = novoHash
                });
                
                _logger.LogInformation("Hash atualizado: {Arquivo} -> {Hash}", arquivo.NomeArquivo, novoHash);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Erro ao processar hash de {Arquivo}", arquivo.NomeArquivo);
                resultado.Erros.Add($"{arquivo.NomeArquivo}: {ex.Message}");
            }
        }
        
        resultado.Sucesso = resultado.ArquivosProcessados == resultado.TotalArquivos;
        
        return Ok(resultado);
    }
}

// DTOs
public record PreviewResult
{
    public int ExecucaoId { get; set; }
    public int TotalArquivos { get; set; }
    public int TotalCorrecoes { get; set; }
    public List<ArquivoPreview> Arquivos { get; set; } = new();
}

public record ArquivoPreview
{
    public int Id { get; set; }
    public string Nome { get; set; } = string.Empty;
    public string Status { get; set; } = string.Empty;
    public int RegrasAplicadas { get; set; }
    public List<CorrecaoPreview> Correcoes { get; set; } = new();
}

public record CorrecaoPreview
{
    public string Regra { get; set; } = string.Empty;
    public string Elemento { get; set; } = string.Empty;
    public string Antes { get; set; } = string.Empty;
    public string Depois { get; set; } = string.Empty;
    public string Acao { get; set; } = string.Empty;
}

public record AplicarResult
{
    public int ExecucaoId { get; set; }
    public int ArquivosAplicados { get; set; }
    public int TotalArquivos { get; set; }
    public string PastaBackup { get; set; } = string.Empty;
    public string PastaCorrigidos { get; set; } = string.Empty;
    public List<string> Erros { get; set; } = new();
    public bool Sucesso { get; set; }
}

public record HashResult
{
    public int ExecucaoId { get; set; }
    public int ArquivosProcessados { get; set; }
    public int TotalArquivos { get; set; }
    public List<HashInfo> Hashes { get; set; } = new();
    public List<string> Erros { get; set; } = new();
    public bool Sucesso { get; set; }
}

public record HashInfo
{
    public string Arquivo { get; set; } = string.Empty;
    public string Hash { get; set; } = string.Empty;
}
