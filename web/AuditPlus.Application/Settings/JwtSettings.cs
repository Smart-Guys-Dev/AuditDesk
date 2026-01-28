namespace AuditPlus.Application.Settings;

/// <summary>
/// Configurações do JWT Token.
/// Mapeado do appsettings.json
/// </summary>
public class JwtSettings
{
    public const string SectionName = "JwtSettings";
    
    /// <summary>
    /// Chave secreta para assinatura do token
    /// </summary>
    public string SecretKey { get; set; } = string.Empty;
    
    /// <summary>
    /// Issuer (emissor) do token
    /// </summary>
    public string Issuer { get; set; } = "AuditPlus";
    
    /// <summary>
    /// Audience (destinatário) do token
    /// </summary>
    public string Audience { get; set; } = "AuditPlusWeb";
    
    /// <summary>
    /// Tempo de expiração em horas
    /// </summary>
    public int ExpirationHours { get; set; } = 8;
}
