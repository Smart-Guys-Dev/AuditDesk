using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;
using System.Xml.Linq;
using Microsoft.Extensions.Logging;

namespace AuditPlus.Application.Services;

/// <summary>
/// Serviço de cálculo de hash para XMLs PTU.
/// Porta direta da lógica de src/business/processing/hash_calculator.py
/// </summary>
public class HashCalculatorService
{
    private readonly ILogger<HashCalculatorService> _logger;

    public HashCalculatorService(ILogger<HashCalculatorService> logger)
    {
        _logger = logger;
    }

    /// <summary>
    /// Calcula o hash MD5 focando APENAS no conteúdo do bloco GuiaCobrancaUtilizacao,
    /// seguindo a lógica validada e aceita pela CMB (versão desktop).
    /// </summary>
    /// <param name="xmlContent">Conteúdo XML completo como string</param>
    /// <returns>Hash MD5 hexadecimal de 32 caracteres, ou null se erro</returns>
    public string? CalcularHashBlocoGuiaCobranca(string xmlContent)
    {
        if (string.IsNullOrWhiteSpace(xmlContent))
        {
            _logger.LogError("O conteúdo XML fornecido é nulo ou vazio. Não é possível calcular o hash.");
            return null;
        }

        try
        {
            // Parse do XML
            var doc = XDocument.Parse(xmlContent);
            
            // Localizar bloco <GuiaCobrancaUtilizacao> usando XPath equivalente
            // XPath original: //*[local-name()='GuiaCobrancaUtilizacao']
            var guiaNode = doc.Descendants()
                .FirstOrDefault(e => e.Name.LocalName == "GuiaCobrancaUtilizacao");
            
            if (guiaNode == null)
            {
                _logger.LogError("Bloco <GuiaCobrancaUtilizacao> não encontrado no XML para cálculo do hash.");
                return null;
            }

            // Converter o bloco para string (equivalente a etree.tostring)
            var blocoGuiaStr = guiaNode.ToString(SaveOptions.DisableFormatting);
            
            // Remover tag <hash> existente para evitar hash circular
            // Regex original: <(\w+:)?hash>.*?</(\w+:)?hash>
            var blocoGuiaSemHashInterno = Regex.Replace(
                blocoGuiaStr, 
                @"<(\w+:)?hash>.*?</(\w+:)?hash>", 
                "", 
                RegexOptions.IgnoreCase | RegexOptions.Singleline
            );

            // Extrair conteúdo puro do bloco (sem tags XML)
            var conteudoPuroDoBloco = ExtrairConteudoPuroDeBloco(blocoGuiaSemHashInterno);

            // Calcular MD5 com encoding ISO-8859-1 (Latin-1)
            var encoding = Encoding.GetEncoding("ISO-8859-1");
            var bytes = encoding.GetBytes(conteudoPuroDoBloco);
            
            using var md5 = MD5.Create();
            var hashBytes = md5.ComputeHash(bytes);
            var novoHash = BitConverter.ToString(hashBytes).Replace("-", "").ToLowerInvariant();

            _logger.LogInformation("Hash do bloco GuiaCobrancaUtilizacao calculado com sucesso: {Hash}", novoHash);
            return novoHash;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Erro inesperado durante o cálculo do hash do bloco GuiaCobrancaUtilizacao");
            return null;
        }
    }

    /// <summary>
    /// Função auxiliar que replica a lógica de limpeza do script Python validado.
    /// Remove quebras de linha, espaços entre tags e todas as tags XML,
    /// deixando apenas o conteúdo textual puro e concatenado.
    /// </summary>
    private string ExtrairConteudoPuroDeBloco(string blocoXmlStr)
    {
        // Remove quebras de linha (equivalente a replace('\n', '').replace('\r', ''))
        var textoSemQuebras = blocoXmlStr.Replace("\n", "").Replace("\r", "");
        
        // Remove espaços entre tags (equivalente a re.sub(r'>\s+<', '><', ...))
        var textoSemEspacos = Regex.Replace(textoSemQuebras, @">\s+<", "><");
        
        // Remove todas as tags XML (equivalente a re.sub(r'<[^>]+>', '', ...))
        var conteudoPuro = Regex.Replace(textoSemEspacos, @"<[^>]+>", "");
        
        return conteudoPuro.Trim();
    }

    /// <summary>
    /// Atualiza a tag <hash> no XML com o novo valor calculado.
    /// </summary>
    /// <param name="xmlContent">Conteúdo XML original</param>
    /// <param name="novoHash">Novo hash calculado</param>
    /// <returns>XML com hash atualizado</returns>
    public string AtualizarHashNoXml(string xmlContent, string novoHash)
    {
        try
        {
            var doc = XDocument.Parse(xmlContent);
            
            // Localizar tag <hash> dentro de GuiaCobrancaUtilizacao
            var guiaNode = doc.Descendants()
                .FirstOrDefault(e => e.Name.LocalName == "GuiaCobrancaUtilizacao");
            
            if (guiaNode == null)
            {
                _logger.LogError("Bloco <GuiaCobrancaUtilizacao> não encontrado para atualizar hash.");
                return xmlContent;
            }

            var hashNode = guiaNode.Descendants()
                .FirstOrDefault(e => e.Name.LocalName == "hash");
            
            if (hashNode != null)
            {
                var hashAntigo = hashNode.Value;
                hashNode.Value = novoHash;
                _logger.LogInformation("Hash atualizado: {Antigo} -> {Novo}", hashAntigo, novoHash);
            }
            else
            {
                // Se não existir, criar a tag hash antes de carimboCMB (se existir) ou no final
                var carimboCMBNode = guiaNode.Descendants()
                    .FirstOrDefault(e => e.Name.LocalName == "carimboCMB");
                
                var ns = guiaNode.Name.Namespace;
                var newHashNode = new XElement(ns + "hash", novoHash);
                
                if (carimboCMBNode != null)
                {
                    carimboCMBNode.AddBeforeSelf(newHashNode);
                }
                else
                {
                    guiaNode.Add(newHashNode);
                }
                
                _logger.LogInformation("Tag <hash> criada com valor: {Hash}", novoHash);
            }

            // Manter encoding original (ISO-8859-1)
            return "<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?>\n" + doc.Root?.ToString(SaveOptions.DisableFormatting);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Erro ao atualizar hash no XML");
            return xmlContent;
        }
    }

    /// <summary>
    /// Calcula e atualiza o hash no XML em uma única operação.
    /// </summary>
    /// <param name="xmlContent">Conteúdo XML original</param>
    /// <returns>Tupla com (XML atualizado, hash calculado) ou (original, null) se erro</returns>
    public (string XmlAtualizado, string? Hash) CalcularEAtualizarHash(string xmlContent)
    {
        var novoHash = CalcularHashBlocoGuiaCobranca(xmlContent);
        
        if (novoHash == null)
        {
            return (xmlContent, null);
        }

        var xmlAtualizado = AtualizarHashNoXml(xmlContent, novoHash);
        return (xmlAtualizado, novoHash);
    }
}
