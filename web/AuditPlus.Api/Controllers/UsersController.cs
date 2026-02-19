using System.Security.Claims;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using AuditPlus.Application.DTOs;
using AuditPlus.Application.Interfaces;
using AuditPlus.Domain.Interfaces;

namespace AuditPlus.Api.Controllers;

/// <summary>
/// Controller para gerenciamento de usuários (admin only).
/// CRUD completo de usuários do sistema.
/// </summary>
[ApiController]
[Route("api/[controller]")]
[Authorize(Roles = "Admin")]
public class UsersController : ControllerBase
{
    private readonly IUserRepository _userRepository;
    private readonly IAuthService _authService;
    private readonly ILogger<UsersController> _logger;

    public UsersController(
        IUserRepository userRepository,
        IAuthService authService,
        ILogger<UsersController> logger)
    {
        _userRepository = userRepository;
        _authService = authService;
        _logger = logger;
    }

    /// <summary>
    /// Lista todos os usuários
    /// </summary>
    [HttpGet]
    public async Task<ActionResult<IEnumerable<UserResponse>>> GetAll()
    {
        var users = await _userRepository.GetAllAsync();
        var response = users.Select(u => new UserResponse(
            Id: u.Id,
            Username: u.Username,
            FullName: u.FullName,
            Email: u.Email,
            Role: u.Role.ToString(),
            LastLoginAt: u.LastLoginAt
        ));
        return Ok(response);
    }

    /// <summary>
    /// Obtém um usuário por ID
    /// </summary>
    [HttpGet("{id}")]
    public async Task<ActionResult<UserResponse>> GetById(int id)
    {
        var user = await _authService.GetUserByIdAsync(id);
        if (user == null)
            return NotFound();
        return Ok(user);
    }

    /// <summary>
    /// Cria um novo usuário
    /// </summary>
    [HttpPost]
    public async Task<ActionResult<UserResponse>> Create([FromBody] RegisterRequest request)
    {
        try
        {
            var user = await _authService.RegisterAsync(request);
            if (user == null)
                return Conflict(new { message = "Username já existe" });

            var adminUsername = User.FindFirst(ClaimTypes.Name)?.Value ?? "system";
            _logger.LogInformation("SECURITY: Usuário {NewUser} criado por {Admin}", 
                request.Username, adminUsername);

            return CreatedAtAction(nameof(GetById), new { id = user.Id }, user);
        }
        catch (ArgumentException ex)
        {
            return BadRequest(new { message = ex.Message });
        }
    }

    /// <summary>
    /// Atualiza dados de um usuário (nome, email, role)
    /// </summary>
    [HttpPut("{id}")]
    public async Task<IActionResult> Update(int id, [FromBody] UpdateUserRequest request)
    {
        var user = await _userRepository.GetByIdAsync(id);
        if (user == null)
            return NotFound();

        user.FullName = request.FullName;
        user.Email = request.Email;
        user.Role = Enum.Parse<Domain.Enums.UserRole>(request.Role, ignoreCase: true);

        await _userRepository.UpdateAsync(user);

        var adminUsername = User.FindFirst(ClaimTypes.Name)?.Value ?? "system";
        _logger.LogInformation("SECURITY: Usuário {UserId} atualizado por {Admin}", id, adminUsername);

        return NoContent();
    }

    /// <summary>
    /// Ativa/Desativa um usuário
    /// </summary>
    [HttpPatch("{id}/toggle")]
    public async Task<IActionResult> Toggle(int id)
    {
        var user = await _userRepository.GetByIdAsync(id);
        if (user == null)
            return NotFound();

        // Não permitir desativar o próprio usuário
        var currentUserId = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        if (currentUserId == id.ToString())
            return BadRequest(new { message = "Você não pode desativar seu próprio usuário" });

        user.IsActive = !user.IsActive;
        await _userRepository.UpdateAsync(user);

        var adminUsername = User.FindFirst(ClaimTypes.Name)?.Value ?? "system";
        _logger.LogInformation("SECURITY: Usuário {UserId} {Action} por {Admin}", 
            id, user.IsActive ? "ativado" : "desativado", adminUsername);

        return Ok(new { isActive = user.IsActive });
    }

    /// <summary>
    /// Desbloqueia uma conta bloqueada
    /// </summary>
    [HttpPatch("{id}/unlock")]
    public async Task<IActionResult> Unlock(int id)
    {
        var user = await _userRepository.GetByIdAsync(id);
        if (user == null)
            return NotFound();

        user.FailedLoginAttempts = 0;
        user.LockedUntil = null;
        await _userRepository.UpdateAsync(user);

        var adminUsername = User.FindFirst(ClaimTypes.Name)?.Value ?? "system";
        _logger.LogInformation("SECURITY: Conta {UserId} desbloqueada por {Admin}", id, adminUsername);

        return Ok(new { message = "Conta desbloqueada" });
    }
}

/// <summary>
/// DTO para atualização de usuário
/// </summary>
public record UpdateUserRequest(
    string FullName,
    string Email,
    string Role
);
