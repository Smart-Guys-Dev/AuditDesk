using AuditPlus.Application.Interfaces;

namespace AuditPlus.Application.Services;

/// <summary>
/// Implementação BCrypt — Recomendada para desenvolvimento e standalone.
/// Cost factor 10 (padrão): ~100ms por hash, resistente a brute-force.
/// </summary>
public class BcryptPasswordHasher : IPasswordHasher
{
    private const int WorkFactor = 10;
    
    public string HashPassword(string password)
    {
        return BCrypt.Net.BCrypt.HashPassword(password, WorkFactor);
    }
    
    public bool VerifyPassword(string password, string storedHash)
    {
        return BCrypt.Net.BCrypt.Verify(password, storedHash);
    }
}
