using System.IO.Compression;

namespace AuditPlus.Tests;

public class ZipPtuStructureTests
{
    /// <summary>
    /// Simula a criação de um ZIP PTU e valida sua estrutura.
    /// Estrutura esperada:
    /// - Validacao_CMB/
    ///   - arquivo1.zip (contém arquivo1.051)
    ///   - arquivo2.zip (contém arquivo2.051)
    /// </summary>
    [Fact]
    public void ExportarZipPtu_DeveGerarEstruturaPtuCorreta()
    {
        // Arrange - Criar XMLs de teste
        var tempDir = Path.Combine(Path.GetTempPath(), $"ptu_test_{Guid.NewGuid()}");
        Directory.CreateDirectory(tempDir);
        
        var xml1 = Path.Combine(tempDir, "fatura001.xml");
        var xml2 = Path.Combine(tempDir, "fatura002.xml");
        
        File.WriteAllText(xml1, "<xml>conteudo1</xml>");
        File.WriteAllText(xml2, "<xml>conteudo2</xml>");
        
        var outputZipPath = Path.Combine(tempDir, "output.zip");
        
        try
        {
            // Act - Criar ZIP com estrutura PTU (simula endpoint)
            using (var memoryStream = new MemoryStream())
            {
                using (var masterArchive = new ZipArchive(memoryStream, ZipArchiveMode.Create, true))
                {
                    foreach (var arquivo in new[] { xml1, xml2 })
                    {
                        var nomeArquivo = Path.GetFileNameWithoutExtension(arquivo);
                        var nomeZipInterno = $"Validacao_CMB/{nomeArquivo}.zip";
                        
                        using var zipInternoStream = new MemoryStream();
                        using (var zipInterno = new ZipArchive(zipInternoStream, ZipArchiveMode.Create, true))
                        {
                            var nome051 = nomeArquivo + ".051";
                            var entryInterno = zipInterno.CreateEntry(nome051, CompressionLevel.Optimal);
                            
                            using var entryStream = entryInterno.Open();
                            using var fileStream = File.OpenRead(arquivo);
                            fileStream.CopyTo(entryStream);
                        }
                        
                        zipInternoStream.Position = 0;
                        var entryMestre = masterArchive.CreateEntry(nomeZipInterno, CompressionLevel.NoCompression);
                        using var mestreEntryStream = entryMestre.Open();
                        zipInternoStream.CopyTo(mestreEntryStream);
                    }
                }
                
                File.WriteAllBytes(outputZipPath, memoryStream.ToArray());
            }
            
            // Assert - Verificar estrutura do ZIP
            Assert.True(File.Exists(outputZipPath), "ZIP de saída deve existir");
            
            using var resultZip = ZipFile.OpenRead(outputZipPath);
            
            // Verificar que existem 2 entries na pasta Validacao_CMB
            var entries = resultZip.Entries.ToList();
            Assert.Equal(2, entries.Count);
            
            // Verificar nomes dos arquivos
            Assert.Contains(entries, e => e.FullName == "Validacao_CMB/fatura001.zip");
            Assert.Contains(entries, e => e.FullName == "Validacao_CMB/fatura002.zip");
            
            // Verificar conteúdo de cada ZIP interno
            foreach (var entry in entries)
            {
                using var entryStream = entry.Open();
                using var ms = new MemoryStream();
                entryStream.CopyTo(ms);
                ms.Position = 0;
                
                using var innerZip = new ZipArchive(ms, ZipArchiveMode.Read);
                Assert.Single(innerZip.Entries);
                
                var innerEntry = innerZip.Entries[0];
                Assert.EndsWith(".051", innerEntry.Name);
            }
        }
        finally
        {
            // Cleanup
            if (Directory.Exists(tempDir))
                Directory.Delete(tempDir, true);
        }
    }
}
