using Microsoft.EntityFrameworkCore;
using AuditPlus.Domain.Entities;

namespace AuditPlus.Infrastructure.Data;

/// <summary>
/// DbContext principal da aplicação.
/// Configura o mapeamento das entidades para o banco de dados.
/// </summary>
public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options)
    {
    }
    
    /// <summary>
    /// Tabela de usuários
    /// </summary>
    public DbSet<User> Users { get; set; }
    
    /// <summary>
    /// Tabela de regras de auditoria
    /// </summary>
    public DbSet<Regra> Regras { get; set; }
    
    /// <summary>
    /// Tabela de execuções/logs
    /// </summary>
    public DbSet<Execucao> Execucoes { get; set; }
    
    /// <summary>
    /// Tabela de faturas
    /// </summary>
    public DbSet<Fatura> Faturas { get; set; }
    
    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);
        
        // User configuration
        modelBuilder.Entity<User>(entity =>
        {
            entity.HasIndex(e => e.Username).IsUnique();
            entity.HasIndex(e => e.Email).IsUnique();
            entity.Property(e => e.Role).HasConversion<string>();
        });
        
        // Regra configuration
        modelBuilder.Entity<Regra>(entity =>
        {
            entity.HasIndex(e => e.Codigo).IsUnique();
            entity.Property(e => e.Categoria).HasConversion<string>();
            entity.Property(e => e.Grupo).HasConversion<string>();
        });
        
        // Fatura configuration
        modelBuilder.Entity<Fatura>(entity =>
        {
            entity.HasIndex(e => e.NumeroFatura).IsUnique();
        });
        
        // Execucao configuration
        modelBuilder.Entity<Execucao>(entity =>
        {
            entity.HasOne(e => e.User)
                  .WithMany()
                  .HasForeignKey(e => e.UserId)
                  .OnDelete(DeleteBehavior.SetNull);
        });
    }
    
    /// <summary>
    /// Override para atualizar campos de auditoria automaticamente
    /// </summary>
    public override Task<int> SaveChangesAsync(CancellationToken cancellationToken = default)
    {
        var entries = ChangeTracker.Entries<BaseEntity>();
        
        foreach (var entry in entries)
        {
            if (entry.State == EntityState.Modified)
            {
                entry.Entity.UpdatedAt = DateTime.UtcNow;
            }
        }
        
        return base.SaveChangesAsync(cancellationToken);
    }
}
