using System.Security.Cryptography;
using System.Text;
using AuditPlus.Application.Interfaces;

namespace AuditPlus.Application.Services;

/// <summary>
/// Implementação SHA256+MD5 — Para migração Oracle/ODA.
/// Formato: SALT:MD5(SHA256(salt+password))
/// 
/// Aparência: 32 chars hex (compatível com formato MD5 institucional).
/// Segurança: SHA-256 interno impede rainbow tables de MD5 puro.
/// Salt: 16 bytes aleatórios por senha, impede ataques de dicionário.
/// </summary>
public class Sha256Md5PasswordHasher : IPasswordHasher
{
    private const int SaltSize = 16;
    
    public string HashPassword(string password)
    {
        // Gerar salt aleatório
        var saltBytes = RandomNumberGenerator.GetBytes(SaltSize);
        var salt = Convert.ToHexString(saltBytes).ToLowerInvariant();
        
        // SHA-256(salt + password) → MD5 do resultado
        var md5Hash = ComputeHash(salt, password);
        
        // Formato: SALT:HASH (salt é armazenado junto)
        return $"{salt}:{md5Hash}";
    }
    
    public bool VerifyPassword(string password, string storedHash)
    {
        // Extrair salt e hash armazenado
        var parts = storedHash.Split(':');
        if (parts.Length != 2) return false;
        
        var salt = parts[0];
        var expectedHash = parts[1];
        
        // Recalcular com o mesmo salt
        var computedHash = ComputeHash(salt, password);
        
        // Comparação segura contra timing attacks
        return CryptographicOperations.FixedTimeEquals(
            Encoding.UTF8.GetBytes(expectedHash),
            Encoding.UTF8.GetBytes(computedHash));
    }
    
    /// <summary>
    /// Camada dupla: SHA-256 interno (segurança) → MD5 externo (formato institucional).
    /// </summary>
    private static string ComputeHash(string salt, string password)
    {
        // Passo 1: SHA-256(salt + password)
        var sha256Input = Encoding.UTF8.GetBytes(salt + password);
        var sha256Hash = SHA256.HashData(sha256Input);
        var sha256Hex = Convert.ToHexString(sha256Hash).ToLowerInvariant();
        
        // Passo 2: MD5(sha256_result) — formato 32 chars hex
        var md5Input = Encoding.UTF8.GetBytes(sha256Hex);
        var md5Hash = MD5.HashData(md5Input);
        return Convert.ToHexString(md5Hash).ToLowerInvariant();
    }
}
