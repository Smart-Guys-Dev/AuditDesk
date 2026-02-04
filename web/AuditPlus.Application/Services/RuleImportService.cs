using System.Text.Json;
using AuditPlus.Domain.Entities;
using AuditPlus.Infrastructure.Data;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;

namespace AuditPlus.Application.Services;

/// <summary>
/// Serviço para importar regras JSON do desktop para o banco de dados.
/// </summary>
public class RuleImportService
{
    private readonly AppDbContext _context;
    private readonly ILogger<RuleImportService> _logger;
    
    public RuleImportService(AppDbContext context, ILogger<RuleImportService> logger)
    {
        _context = context;
        _logger = logger;
    }
    
    /// <summary>
    /// Importa regras de uma pasta contendo arquivos JSON.
    /// </summary>
    public async Task<ImportResult> ImportarRegrasAsync(string pastaRegras)
    {
        var resultado = new ImportResult();
        
        if (!Directory.Exists(pastaRegras))
        {
            resultado.Mensagem = $"Pasta não encontrada: {pastaRegras}";
            return resultado;
        }
        
        // Primeiro, carregar rules_config.json para saber a ordem
        var configPath = Path.Combine(pastaRegras, "rules_config.json");
        var gruposParaCarregar = new List<GrupoConfig>();
        
        if (File.Exists(configPath))
        {
            var configJson = await File.ReadAllTextAsync(configPath);
            var config = JsonSerializer.Deserialize<RulesConfig>(configJson);
            
            if (config?.grupos_para_carregar != null)
            {
                gruposParaCarregar = config.grupos_para_carregar
                    .Where(g => g.ativo)
                    .ToList();
            }
        }
        
        if (gruposParaCarregar.Count == 0)
        {
            // Fallback: carregar todos os JSONs da pasta regras/
            var pastaRegrasSub = Path.Combine(pastaRegras, "regras");
            if (Directory.Exists(pastaRegrasSub))
            {
                var arquivos = Directory.GetFiles(pastaRegrasSub, "*.json");
                foreach (var arq in arquivos)
                {
                    gruposParaCarregar.Add(new GrupoConfig
                    {
                        nome_grupo = Path.GetFileNameWithoutExtension(arq),
                        arquivo_regras = $"regras/{Path.GetFileName(arq)}",
                        ativo = true
                    });
                }
            }
        }
        
        _logger.LogInformation("Encontrados {Count} grupos de regras para importar", 
            gruposParaCarregar.Count);
        
        var prioridade = 1;
        
        foreach (var grupo in gruposParaCarregar)
        {
            var caminhoArquivo = Path.Combine(pastaRegras, grupo.arquivo_regras);
            
            if (!File.Exists(caminhoArquivo))
            {
                _logger.LogWarning("Arquivo não encontrado: {Arquivo}", caminhoArquivo);
                continue;
            }
            
            try
            {
                var json = await File.ReadAllTextAsync(caminhoArquivo);
                var regrasJson = JsonSerializer.Deserialize<List<JsonElement>>(json);
                
                if (regrasJson == null) continue;
                
                foreach (var regraJson in regrasJson)
                {
                    var codigo = regraJson.TryGetProperty("id", out var id) 
                        ? id.GetString() ?? "" 
                        : "";
                    
                    if (string.IsNullOrEmpty(codigo)) continue;
                    
                    // Verificar se já existe
                    var existente = await _context.ValidationRules
                        .FirstOrDefaultAsync(r => r.Codigo == codigo);
                    
                    if (existente != null)
                    {
                        resultado.Atualizadas++;
                        // Atualizar
                        existente.Descricao = regraJson.TryGetProperty("descricao", out var desc) 
                            ? desc.GetString() ?? "" 
                            : "";
                        existente.Ativo = regraJson.TryGetProperty("ativo", out var ativo) 
                            && ativo.GetBoolean();
                        existente.CondicoesJson = regraJson.TryGetProperty("condicoes", out var cond) 
                            ? cond.GetRawText() 
                            : "{}";
                        existente.AcoesJson = regraJson.TryGetProperty("acao", out var acao) 
                            ? acao.GetRawText() 
                            : "{}";
                        existente.LogSucesso = regraJson.TryGetProperty("log_sucesso", out var log) 
                            ? log.GetString() ?? "" 
                            : "";
                        existente.UpdatedAt = DateTime.UtcNow;
                    }
                    else
                    {
                        resultado.Importadas++;
                        
                        // Extrair tipo_elemento das condições
                        var tipoElemento = "";
                        if (regraJson.TryGetProperty("condicoes", out var condicoes))
                        {
                            if (condicoes.TryGetProperty("tipo_elemento", out var te))
                            {
                                tipoElemento = te.GetString() ?? "";
                            }
                        }
                        
                        // Extrair categoria e impacto de metadata_glosa
                        var categoria = "VALIDACAO";
                        var impacto = "MEDIO";
                        if (regraJson.TryGetProperty("metadata_glosa", out var metadata))
                        {
                            if (metadata.TryGetProperty("categoria", out var cat))
                                categoria = cat.GetString() ?? "VALIDACAO";
                            if (metadata.TryGetProperty("impacto", out var imp))
                                impacto = imp.GetString() ?? "MEDIO";
                        }
                        
                        var novaRegra = new ValidationRule
                        {
                            Codigo = codigo,
                            Descricao = regraJson.TryGetProperty("descricao", out var desc2) 
                                ? desc2.GetString() ?? "" 
                                : "",
                            Grupo = grupo.nome_grupo,
                            TipoElemento = tipoElemento,
                            CondicoesJson = regraJson.TryGetProperty("condicoes", out var cond2) 
                                ? cond2.GetRawText() 
                                : "{}",
                            AcoesJson = regraJson.TryGetProperty("acao", out var acao2) 
                                ? acao2.GetRawText() 
                                : "{}",
                            LogSucesso = regraJson.TryGetProperty("log_sucesso", out var log2) 
                                ? log2.GetString() ?? "" 
                                : "",
                            Categoria = categoria,
                            Impacto = impacto,
                            Ativo = regraJson.TryGetProperty("ativo", out var ativo2) 
                                && ativo2.GetBoolean(),
                            Prioridade = prioridade++,
                            CreatedAt = DateTime.UtcNow
                        };
                        
                        _context.ValidationRules.Add(novaRegra);
                    }
                }
                
                await _context.SaveChangesAsync();
                resultado.GruposProcessados++;
                _logger.LogInformation("Grupo '{Grupo}' processado: {Count} regras", 
                    grupo.nome_grupo, regrasJson.Count);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Erro ao processar {Arquivo}", caminhoArquivo);
                resultado.Erros.Add($"{grupo.arquivo_regras}: {ex.Message}");
            }
        }
        
        resultado.Sucesso = resultado.Erros.Count == 0;
        resultado.Mensagem = $"Importadas {resultado.Importadas}, atualizadas {resultado.Atualizadas} regras de {resultado.GruposProcessados} grupos";
        
        return resultado;
    }
}

public class ImportResult
{
    public bool Sucesso { get; set; }
    public string Mensagem { get; set; } = string.Empty;
    public int GruposProcessados { get; set; }
    public int Importadas { get; set; }
    public int Atualizadas { get; set; }
    public List<string> Erros { get; set; } = new();
}

// Classes para deserializar rules_config.json
public class RulesConfig
{
    public List<GrupoConfig>? grupos_para_carregar { get; set; }
}

public class GrupoConfig
{
    public string nome_grupo { get; set; } = string.Empty;
    public string arquivo_regras { get; set; } = string.Empty;
    public bool ativo { get; set; }
}
