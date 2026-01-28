using System.Security.Claims;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using AuditPlus.Application.DTOs;
using AuditPlus.Application.Interfaces;

namespace AuditPlus.Api.Controllers;

/// <summary>
/// Controller de autenticação.
/// Gerencia login, registro e informações do usuário.
/// </summary>
[ApiController]
[Route("api/[controller]")]
public class AuthController : ControllerBase
{
    private readonly IAuthService _authService;
    private readonly ILogger<AuthController> _logger;
    
    public AuthController(IAuthService authService, ILogger<AuthController> logger)
    {
        _authService = authService;
        _logger = logger;
    }
    
    /// <summary>
    /// Realiza login e retorna token JWT
    /// </summary>
    [HttpPost("login")]
    [AllowAnonymous]
    public async Task<ActionResult<LoginResponse>> Login([FromBody] LoginRequest request)
    {
        var result = await _authService.LoginAsync(request);
        
        if (result == null)
        {
            _logger.LogWarning("Tentativa de login falha para usuário: {Username}", request.Username);
            return Unauthorized(new { message = "Usuário ou senha inválidos" });
        }
        
        _logger.LogInformation("Login bem-sucedido: {Username}", request.Username);
        return Ok(result);
    }
    
    /// <summary>
    /// Registra um novo usuário (apenas ADMIN)
    /// </summary>
    [HttpPost("register")]
    [Authorize(Roles = "ADMIN")]
    public async Task<ActionResult<UserResponse>> Register([FromBody] RegisterRequest request)
    {
        var result = await _authService.RegisterAsync(request);
        
        if (result == null)
        {
            return BadRequest(new { message = "Username já existe" });
        }
        
        _logger.LogInformation("Novo usuário registrado: {Username} por {Admin}", 
            request.Username, User.Identity?.Name);
        return CreatedAtAction(nameof(GetCurrentUser), result);
    }
    
    /// <summary>
    /// Obtém dados do usuário autenticado
    /// </summary>
    [HttpGet("me")]
    [Authorize]
    public async Task<ActionResult<UserResponse>> GetCurrentUser()
    {
        var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        if (string.IsNullOrEmpty(userIdClaim) || !int.TryParse(userIdClaim, out var userId))
        {
            return Unauthorized();
        }
        
        var user = await _authService.GetUserByIdAsync(userId);
        if (user == null)
        {
            return NotFound();
        }
        
        return Ok(user);
    }
    
    /// <summary>
    /// Altera a senha do usuário autenticado
    /// </summary>
    [HttpPost("change-password")]
    [Authorize]
    public async Task<IActionResult> ChangePassword([FromBody] ChangePasswordRequest request)
    {
        var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        if (string.IsNullOrEmpty(userIdClaim) || !int.TryParse(userIdClaim, out var userId))
        {
            return Unauthorized();
        }
        
        var result = await _authService.ChangePasswordAsync(userId, request);
        
        if (!result)
        {
            return BadRequest(new { message = "Senha atual incorreta" });
        }
        
        _logger.LogInformation("Senha alterada para usuário ID: {UserId}", userId);
        return Ok(new { message = "Senha alterada com sucesso" });
    }
    
    /// <summary>
    /// Valida se um token é válido (para refresh/verificação)
    /// </summary>
    [HttpGet("validate")]
    [Authorize]
    public IActionResult ValidateToken()
    {
        return Ok(new { valid = true, user = User.Identity?.Name });
    }
}
