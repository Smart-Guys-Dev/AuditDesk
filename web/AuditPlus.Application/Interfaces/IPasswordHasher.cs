namespace AuditPlus.Application.Interfaces;

/// <summary>
/// Interface para estratégia de hashing de senhas.
/// Permite trocar o algoritmo (BCrypt → SHA256+MD5) sem alterar o AuthService.
/// </summary>
public interface IPasswordHasher
{
    /// <summary>
    /// Gera o hash de uma senha em texto plano
    /// </summary>
    string HashPassword(string password);
    
    /// <summary>
    /// Verifica se uma senha em texto plano corresponde ao hash armazenado
    /// </summary>
    bool VerifyPassword(string password, string storedHash);
}
