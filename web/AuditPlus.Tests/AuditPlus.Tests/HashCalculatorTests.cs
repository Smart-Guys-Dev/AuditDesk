using AuditPlus.Application.Services;
using Microsoft.Extensions.Logging.Abstractions;

namespace AuditPlus.Tests;

public class HashCalculatorTests
{
    /// <summary>
    /// Verifica se o hash C# é idêntico ao hash Python.
    /// Hash Python calculado via hash_calculator.py no arquivo N0000197_pre.051
    /// </summary>
    [Fact]
    public void CalcularHashBlocoGuiaCobranca_DeveRetornarHashIdenticoAoPython()
    {
        // Arrange
        var testFile = @"c:\Users\pedro.freitas\OneDrive - UNIMEDCG\AuditPlusv2.0\data\XML teste\N0000197_pre.051";
        var expectedPythonHash = "32e0f3ee9a33dcf430a6391346528581";
        
        var logger = NullLogger<HashCalculatorService>.Instance;
        var hashService = new HashCalculatorService(logger);
        
        // Act
        var xmlContent = File.ReadAllText(testFile);
        var hashCSharp = hashService.CalcularHashBlocoGuiaCobranca(xmlContent);
        
        // Assert
        Assert.NotNull(hashCSharp);
        Assert.Equal(32, hashCSharp.Length); // MD5 has 32 hex chars
        Assert.Equal(expectedPythonHash, hashCSharp);
    }
}
