using Microsoft.AspNetCore.Mvc;
using AuditPlus.Domain.Entities;
using AuditPlus.Domain.Interfaces;
using AuditPlus.Domain.Enums;

namespace AuditPlus.Api.Controllers;

/// <summary>
/// Controller para gerenciamento de Regras de Auditoria.
/// Fornece operações CRUD para as regras do sistema.
/// </summary>
[ApiController]
[Route("api/[controller]")]
public class RegrasController : ControllerBase
{
    private readonly IRegraRepository _regraRepository;
    private readonly ILogger<RegrasController> _logger;
    
    public RegrasController(IRegraRepository regraRepository, ILogger<RegrasController> logger)
    {
        _regraRepository = regraRepository;
        _logger = logger;
    }
    
    /// <summary>
    /// Obtém todas as regras
    /// </summary>
    [HttpGet]
    public async Task<ActionResult<IEnumerable<Regra>>> GetAll()
    {
        var regras = await _regraRepository.GetAllAsync();
        return Ok(regras);
    }
    
    /// <summary>
    /// Obtém regras ativas ordenadas por prioridade
    /// </summary>
    [HttpGet("ativas")]
    public async Task<ActionResult<IEnumerable<Regra>>> GetAtivas()
    {
        var regras = await _regraRepository.GetAtivasAsync();
        return Ok(regras);
    }
    
    /// <summary>
    /// Obtém uma regra por ID
    /// </summary>
    [HttpGet("{id}")]
    public async Task<ActionResult<Regra>> GetById(int id)
    {
        var regra = await _regraRepository.GetByIdAsync(id);
        if (regra == null)
            return NotFound();
        return Ok(regra);
    }
    
    /// <summary>
    /// Obtém uma regra por código
    /// </summary>
    [HttpGet("codigo/{codigo}")]
    public async Task<ActionResult<Regra>> GetByCodigo(string codigo)
    {
        var regra = await _regraRepository.GetByCodigoAsync(codigo);
        if (regra == null)
            return NotFound();
        return Ok(regra);
    }
    
    /// <summary>
    /// Obtém regras por categoria
    /// </summary>
    [HttpGet("categoria/{categoria}")]
    public async Task<ActionResult<IEnumerable<Regra>>> GetByCategoria(RuleCategory categoria)
    {
        var regras = await _regraRepository.GetByCategoriaAsync(categoria);
        return Ok(regras);
    }
    
    /// <summary>
    /// Obtém regras por grupo
    /// </summary>
    [HttpGet("grupo/{grupo}")]
    public async Task<ActionResult<IEnumerable<Regra>>> GetByGrupo(RuleGroup grupo)
    {
        var regras = await _regraRepository.GetByGrupoAsync(grupo);
        return Ok(regras);
    }
    
    /// <summary>
    /// Cria uma nova regra
    /// </summary>
    [HttpPost]
    public async Task<ActionResult<Regra>> Create([FromBody] Regra regra)
    {
        var created = await _regraRepository.AddAsync(regra);
        _logger.LogInformation("Regra criada: {Codigo}", regra.Codigo);
        return CreatedAtAction(nameof(GetById), new { id = created.Id }, created);
    }
    
    /// <summary>
    /// Atualiza uma regra existente
    /// </summary>
    [HttpPut("{id}")]
    public async Task<IActionResult> Update(int id, [FromBody] Regra regra)
    {
        if (id != regra.Id)
            return BadRequest();
            
        var exists = await _regraRepository.ExistsAsync(id);
        if (!exists)
            return NotFound();
            
        await _regraRepository.UpdateAsync(regra);
        _logger.LogInformation("Regra atualizada: {Codigo}", regra.Codigo);
        return NoContent();
    }
    
    /// <summary>
    /// Remove uma regra
    /// </summary>
    [HttpDelete("{id}")]
    public async Task<IActionResult> Delete(int id)
    {
        var exists = await _regraRepository.ExistsAsync(id);
        if (!exists)
            return NotFound();
            
        await _regraRepository.DeleteAsync(id);
        _logger.LogInformation("Regra removida: {Id}", id);
        return NoContent();
    }
    
    /// <summary>
    /// Ativa/Desativa uma regra
    /// </summary>
    [HttpPatch("{id}/toggle")]
    public async Task<IActionResult> Toggle(int id)
    {
        var regra = await _regraRepository.GetByIdAsync(id);
        if (regra == null)
            return NotFound();
            
        regra.Ativo = !regra.Ativo;
        await _regraRepository.UpdateAsync(regra);
        _logger.LogInformation("Regra {Codigo} alterada para Ativo={Ativo}", regra.Codigo, regra.Ativo);
        return Ok(new { ativo = regra.Ativo });
    }
}
