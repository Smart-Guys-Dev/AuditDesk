using System.IO.Compression;
using System.Text.Json;
using System.Xml.Linq;
using AuditPlus.Domain.Entities;
using AuditPlus.Infrastructure.Data;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;

namespace AuditPlus.Application.Services;

/// <summary>
/// Serviço de validação e correção de arquivos XML.
/// Implementa o motor de regras do AuditPlus.
/// </summary>
public class XmlValidationService
{
    private readonly AppDbContext _context;
    private readonly ILogger<XmlValidationService> _logger;
    
    // Namespace PTU usado nos XMLs TISS
    private static readonly XNamespace PtuNs = "http://www.ans.gov.br/padroes/tiss/schemas";
    
    public XmlValidationService(AppDbContext context, ILogger<XmlValidationService> logger)
    {
        _context = context;
        _logger = logger;
    }
    
    /// <summary>
    /// Processa um lote de arquivos XML, aplicando as regras ativas.
    /// </summary>
    public async Task<ValidationResult> ProcessarLoteAsync(int execucaoId, string pastaArquivos)
    {
        var resultado = new ValidationResult
        {
            ExecucaoId = execucaoId,
            TotalArquivos = 0,
            ArquivosModificados = 0,
            TotalCorrecoes = 0
        };
        
        try
        {
            // Buscar regras ativas
            var regras = await _context.ValidationRules
                .Where(r => r.Ativo)
                .OrderBy(r => r.Prioridade)
                .ToListAsync();
            
            if (regras.Count == 0)
            {
                _logger.LogWarning("Nenhuma regra ativa encontrada");
                resultado.Mensagem = "Nenhuma regra ativa configurada";
                return resultado;
            }
            
            _logger.LogInformation("Carregadas {Count} regras ativas", regras.Count);
            
            // Primeiro: extrair .051 de arquivos ZIP (igual ao desktop)
            var arquivosZip = Directory.GetFiles(pastaArquivos, "*.zip", SearchOption.TopDirectoryOnly);
            if (arquivosZip.Length > 0)
            {
                _logger.LogInformation("Encontrados {Count} arquivos ZIP, extraindo...", arquivosZip.Length);
                foreach (var zipPath in arquivosZip)
                {
                    ExtrairXmlDeZip(zipPath, pastaArquivos);
                }
            }
            
            // Buscar arquivos .051 na pasta (originais + extraídos)
            var arquivosXml = Directory.GetFiles(pastaArquivos, "*.051", SearchOption.TopDirectoryOnly);
            resultado.TotalArquivos = arquivosXml.Length;
            
            if (arquivosXml.Length == 0)
            {
                // Tentar também arquivos .xml
                arquivosXml = Directory.GetFiles(pastaArquivos, "*.xml", SearchOption.TopDirectoryOnly);
                resultado.TotalArquivos = arquivosXml.Length;
            }
            
            if (arquivosXml.Length == 0)
            {
                resultado.Mensagem = "Nenhum arquivo .051 ou .xml encontrado (verifique se os ZIPs contêm arquivos .051)";
                return resultado;
            }
            
            // Processar cada arquivo
            foreach (var caminhoArquivo in arquivosXml)
            {
                var nomeArquivo = Path.GetFileName(caminhoArquivo);
                _logger.LogInformation("Processando: {Arquivo}", nomeArquivo);
                
                try
                {
                    var correcoesArquivo = await ProcessarArquivoAsync(
                        caminhoArquivo, 
                        regras, 
                        execucaoId
                    );
                    
                    if (correcoesArquivo > 0)
                    {
                        resultado.ArquivosModificados++;
                        resultado.TotalCorrecoes += correcoesArquivo;
                    }
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, "Erro ao processar {Arquivo}", nomeArquivo);
                    resultado.Erros.Add($"{nomeArquivo}: {ex.Message}");
                }
            }
            
            resultado.Sucesso = true;
            resultado.Mensagem = $"Processados {resultado.TotalArquivos} arquivos, " +
                                $"{resultado.ArquivosModificados} modificados, " +
                                $"{resultado.TotalCorrecoes} correções aplicadas";
            
            return resultado;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Erro no processamento do lote");
            resultado.Mensagem = $"Erro: {ex.Message}";
            return resultado;
        }
    }
    
    /// <summary>
    /// Processa um único arquivo XML aplicando as regras.
    /// </summary>
    private async Task<int> ProcessarArquivoAsync(
        string caminhoArquivo, 
        List<ValidationRule> regras,
        int execucaoId)
    {
        var correcoesAplicadas = 0;
        var nomeArquivo = Path.GetFileName(caminhoArquivo);
        
        // Carregar XML
        var doc = XDocument.Load(caminhoArquivo);
        var raiz = doc.Root;
        
        if (raiz == null)
        {
            throw new InvalidOperationException("XML inválido - raiz não encontrada");
        }
        
        // Registrar arquivo
        var arquivoXml = new ArquivoXml
        {
            ExecucaoId = execucaoId,
            NomeArquivo = nomeArquivo,
            CaminhoArquivo = caminhoArquivo,
            HashOriginal = CalcularHash(caminhoArquivo),
            TamanhoBytes = new FileInfo(caminhoArquivo).Length,
            Status = "PROCESSANDO",
            CreatedAt = DateTime.UtcNow
        };
        
        _context.ArquivosXml.Add(arquivoXml);
        await _context.SaveChangesAsync();
        
        var logs = new List<string>();
        var modificado = false;
        
        // Aplicar cada regra
        foreach (var regra in regras)
        {
            try
            {
                var (aplicada, correcoes) = AplicarRegra(doc, regra, arquivoXml.Id);
                
                if (aplicada)
                {
                    correcoesAplicadas += correcoes.Count;
                    modificado = true;
                    logs.Add($"[OK] {regra.Codigo}: {regra.LogSucesso}");
                    
                    // Salvar correções
                    foreach (var correcao in correcoes)
                    {
                        _context.Correcoes.Add(correcao);
                    }
                    
                    // Atualizar contador da regra
                    regra.TotalAplicacoes++;
                }
            }
            catch (Exception ex)
            {
                logs.Add($"[ERRO] {regra.Codigo}: {ex.Message}");
            }
        }
        
        // Salvar arquivo modificado
        if (modificado)
        {
            doc.Save(caminhoArquivo);
            arquivoXml.Status = "CORRIGIDO";
            arquivoXml.HashCorrigido = CalcularHash(caminhoArquivo);
        }
        else
        {
            arquivoXml.Status = "VALIDADO";
        }
        
        arquivoXml.RegrasAplicadas = correcoesAplicadas;
        arquivoXml.LogProcessamento = string.Join("\n", logs);
        await _context.SaveChangesAsync();
        
        return correcoesAplicadas;
    }
    
    /// <summary>
    /// Aplica uma regra específica ao documento XML.
    /// </summary>
    private (bool Aplicada, List<Correcao> Correcoes) AplicarRegra(
        XDocument doc, 
        ValidationRule regra,
        int arquivoXmlId)
    {
        var correcoes = new List<Correcao>();
        var aplicada = false;
        
        // Parse condições e ações do JSON
        var condicoes = JsonSerializer.Deserialize<JsonElement>(regra.CondicoesJson);
        var acoes = JsonSerializer.Deserialize<JsonElement>(regra.AcoesJson);
        
        // Buscar tipo de elemento alvo
        var tipoElemento = regra.TipoElemento;
        if (string.IsNullOrEmpty(tipoElemento))
        {
            if (condicoes.TryGetProperty("tipo_elemento", out var te))
            {
                tipoElemento = te.GetString() ?? "";
            }
        }
        
        // Encontrar elementos que correspondem ao tipo
        var elementos = doc.Descendants(PtuNs + tipoElemento).ToList();
        
        foreach (var elemento in elementos)
        {
            // Avaliar condições
            if (AvaliarCondicoes(elemento, condicoes))
            {
                // Aplicar ações
                var correcao = AplicarAcoes(elemento, acoes, regra, arquivoXmlId);
                if (correcao != null)
                {
                    correcoes.Add(correcao);
                    aplicada = true;
                }
            }
        }
        
        return (aplicada, correcoes);
    }
    
    /// <summary>
    /// Avalia se um elemento atende às condições da regra.
    /// </summary>
    private bool AvaliarCondicoes(XElement elemento, JsonElement condicoes)
    {
        // Condição múltipla (AND/OR)
        if (condicoes.TryGetProperty("condicao_multipla", out var condMultipla))
        {
            var tipo = condMultipla.GetProperty("tipo").GetString();
            var subCondicoes = condMultipla.GetProperty("sub_condicoes").EnumerateArray();
            
            if (tipo == "AND")
            {
                return subCondicoes.All(sc => AvaliarSubCondicao(elemento, sc));
            }
            else // OR
            {
                return subCondicoes.Any(sc => AvaliarSubCondicao(elemento, sc));
            }
        }
        
        // Condição simples de tag/valor
        if (condicoes.TryGetProperty("condicao_tag_valor", out var condTag))
        {
            return AvaliarCondicaoTagValor(elemento, condTag);
        }
        
        return true; // Sem condições = sempre aplica
    }
    
    private bool AvaliarSubCondicao(XElement elemento, JsonElement subCondicao)
    {
        if (subCondicao.TryGetProperty("condicao_tag_valor", out var condTag))
        {
            return AvaliarCondicaoTagValor(elemento, condTag);
        }
        return true;
    }
    
    private bool AvaliarCondicaoTagValor(XElement elemento, JsonElement condicao)
    {
        var xpath = condicao.GetProperty("xpath").GetString() ?? "";
        
        // Converter XPath simplificado para busca de elementos
        var tagPath = xpath.Replace("./ptu:", "").Split('/');
        var atual = elemento;
        
        foreach (var tag in tagPath)
        {
            if (string.IsNullOrEmpty(tag)) continue;
            atual = atual.Element(PtuNs + tag);
            if (atual == null) break;
        }
        
        // Verificar tipo de comparação
        if (condicao.TryGetProperty("tipo_comparacao", out var tipoComp))
        {
            var tipo = tipoComp.GetString();
            if (tipo == "nao_existe")
                return atual == null;
            if (tipo == "existe")
                return atual != null;
        }
        
        // Verificar valor permitido
        if (condicao.TryGetProperty("valor_permitido", out var valoresPermitidos))
        {
            if (atual == null) return false;
            var valorAtual = atual.Value;
            return valoresPermitidos.EnumerateArray()
                .Any(v => v.GetString() == valorAtual);
        }
        
        return atual != null;
    }
    
    /// <summary>
    /// Aplica as ações definidas na regra ao elemento.
    /// </summary>
    private Correcao? AplicarAcoes(
        XElement elemento, 
        JsonElement acoes,
        ValidationRule regra,
        int arquivoXmlId)
    {
        var tipoAcao = acoes.TryGetProperty("tipo_acao", out var ta) 
            ? ta.GetString() ?? "" 
            : "";
        
        var valorAnterior = "";
        var valorNovo = "";
        var elementoAfetado = "";
        
        switch (tipoAcao)
        {
            case "substituir_valor":
                (valorAnterior, valorNovo, elementoAfetado) = 
                    AplicarSubstituirValor(elemento, acoes);
                break;
                
            case "garantir_tag_com_conteudo":
                (valorAnterior, valorNovo, elementoAfetado) = 
                    AplicarGarantirTag(elemento, acoes);
                break;
                
            case "multiplas_acoes":
                if (acoes.TryGetProperty("sub_acoes", out var subAcoes))
                {
                    foreach (var subAcao in subAcoes.EnumerateArray())
                    {
                        AplicarAcoes(elemento, subAcao, regra, arquivoXmlId);
                    }
                }
                break;
                
            case "reordenar_elementos_filhos":
                (valorAnterior, valorNovo, elementoAfetado) = 
                    AplicarReordenar(elemento, acoes);
                break;
        }
        
        if (string.IsNullOrEmpty(elementoAfetado))
            return null;
            
        return new Correcao
        {
            ArquivoXmlId = arquivoXmlId,
            ValidationRuleId = regra.Id,
            CodigoRegra = regra.Codigo,
            ElementoAfetado = elementoAfetado,
            ValorAnterior = valorAnterior,
            ValorNovo = valorNovo,
            TipoAcao = tipoAcao,
            Status = "APLICADO",
            CreatedAt = DateTime.UtcNow
        };
    }
    
    private (string anterior, string novo, string elemento) AplicarSubstituirValor(
        XElement elemento, JsonElement acao)
    {
        var xpath = acao.TryGetProperty("tag_alvo", out var ta) ? ta.GetString() ?? "" : "";
        var novoValor = acao.TryGetProperty("novo_valor", out var nv) ? nv.GetString() ?? "" : "";
        
        var tagPath = xpath.Replace("./ptu:", "").Split('/');
        var atual = elemento;
        
        foreach (var tag in tagPath)
        {
            if (string.IsNullOrEmpty(tag)) continue;
            atual = atual.Element(PtuNs + tag);
            if (atual == null) break;
        }
        
        if (atual != null)
        {
            var valorAnterior = atual.Value;
            atual.Value = novoValor;
            return (valorAnterior, novoValor, xpath);
        }
        
        return ("", "", "");
    }
    
    private (string anterior, string novo, string elemento) AplicarGarantirTag(
        XElement elemento, JsonElement acao)
    {
        var xpath = acao.TryGetProperty("tag_alvo", out var ta) ? ta.GetString() ?? "" : "";
        var novoConteudo = acao.TryGetProperty("novo_conteudo", out var nc) ? nc.GetString() ?? "" : "";
        
        var tagPath = xpath.Replace("./ptu:", "").Split('/');
        var atual = elemento;
        
        foreach (var tag in tagPath)
        {
            if (string.IsNullOrEmpty(tag)) continue;
            var filho = atual.Element(PtuNs + tag);
            if (filho == null)
            {
                filho = new XElement(PtuNs + tag);
                atual.Add(filho);
            }
            atual = filho;
        }
        
        var valorAnterior = atual.Value;
        if (!string.IsNullOrEmpty(novoConteudo))
        {
            atual.Value = novoConteudo;
        }
        
        return (valorAnterior, novoConteudo, xpath);
    }
    
    private (string anterior, string novo, string elemento) AplicarReordenar(
        XElement elemento, JsonElement acao)
    {
        var xpath = acao.TryGetProperty("tag_alvo", out var ta) ? ta.GetString() ?? "" : "";
        
        if (!acao.TryGetProperty("ordem_correta", out var ordemCorreta))
            return ("", "", "");
        
        var tagPath = xpath.Replace("./ptu:", "").Split('/');
        var atual = elemento;
        
        foreach (var tag in tagPath)
        {
            if (string.IsNullOrEmpty(tag)) continue;
            atual = atual.Element(PtuNs + tag);
            if (atual == null) break;
        }
        
        if (atual == null) return ("", "", "");
        
        var ordem = ordemCorreta.EnumerateArray()
            .Select(o => o.GetString() ?? "")
            .Where(o => !string.IsNullOrEmpty(o))
            .ToList();
        
        var filhosOrdenados = new List<XElement>();
        var filhosRestantes = atual.Elements().ToList();
        
        foreach (var nomeTag in ordem)
        {
            var filho = filhosRestantes.FirstOrDefault(f => f.Name.LocalName == nomeTag);
            if (filho != null)
            {
                filhosOrdenados.Add(filho);
                filhosRestantes.Remove(filho);
            }
        }
        
        // Adicionar restantes no final
        filhosOrdenados.AddRange(filhosRestantes);
        
        // Reordenar
        atual.RemoveNodes();
        foreach (var filho in filhosOrdenados)
        {
            atual.Add(filho);
        }
        
        return ("reordenado", string.Join(",", ordem), xpath);
    }
    
    private string CalcularHash(string caminhoArquivo)
    {
        using var md5 = System.Security.Cryptography.MD5.Create();
        using var stream = File.OpenRead(caminhoArquivo);
        var hash = md5.ComputeHash(stream);
        return BitConverter.ToString(hash).Replace("-", "").ToLowerInvariant();
    }
    
    /// <summary>
    /// Extrai arquivos .051 de um arquivo ZIP (igual ao desktop file_manager.py)
    /// </summary>
    private void ExtrairXmlDeZip(string caminhoZip, string pastaDestino)
    {
        try
        {
            using var archive = System.IO.Compression.ZipFile.OpenRead(caminhoZip);
            foreach (var entry in archive.Entries)
            {
                if (entry.FullName.EndsWith(".051", StringComparison.OrdinalIgnoreCase))
                {
                    var destinoArquivo = Path.Combine(pastaDestino, entry.Name);
                    if (!File.Exists(destinoArquivo))
                    {
                        entry.ExtractToFile(destinoArquivo);
                        _logger.LogInformation("Extraído: {Arquivo} de {Zip}", entry.Name, Path.GetFileName(caminhoZip));
                    }
                }
            }
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Erro ao extrair ZIP: {Zip}", Path.GetFileName(caminhoZip));
        }
    }
}

/// <summary>
/// Resultado de uma validação de lote
/// </summary>
public class ValidationResult
{
    public int ExecucaoId { get; set; }
    public bool Sucesso { get; set; }
    public string Mensagem { get; set; } = string.Empty;
    public int TotalArquivos { get; set; }
    public int ArquivosModificados { get; set; }
    public int TotalCorrecoes { get; set; }
    public List<string> Erros { get; set; } = new();
}
