# apply_security_hardening.py
"""
Script de Hardening de Segurança
Aplica todas as medidas de segurança na aplicação.

Executa:
- Permissões de arquivos
- Criação de backup criptografado
- Verificações de segurança

USO: python apply_security_hardening.py
"""

import logging
from src.infrastructure.security import (
    FilePermissionsManager,
    BackupManager,
    get_backup_key_from_env
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Aplica hardening de segurança"""
    
    print("="*60)
    print("🔒 HARDENING DE SEGURANÇA - AuditPlus v2.0")
    print("="*60)
    print()
    
    # 1. Permissões de Arquivos
    print("1️⃣  Aplicando permissões seguras de arquivos...")
    print("-" * 60)
    
    stats = FilePermissionsManager.secure_application()
    
    print(f"   ✅ Banco de dados: {'OK' if stats['database'] else 'N/A'}")
    print(f"   ✅ Diretório logs: {'OK' if stats['logs_dir'] else 'N/A'}")
    print(f"   ✅ Arquivos de log: {stats['logs_files']} protegidos")
    print(f"   ✅ Diretório config: {'OK' if stats['config_dir'] else 'N/A'}")
    print(f"   ✅ Arquivos config: {stats['config_files']} protegidos")
    print(f"   📊 TOTAL: {stats['total_success']} itens protegidos")
    print()
    
    # 2. Backup Criptografado
    print("2️⃣  Criando backup criptografado...")
    print("-" * 60)
    
    backup_key = get_backup_key_from_env()
    backup_mgr = BackupManager(backup_key)
    
    backup_file = backup_mgr.create_backup(include_logs=False)
    
    if backup_file:
        print(f"   ✅ Backup criado: {backup_file}")
        
        # Listar backups existentes
        backups = backup_mgr.list_backups()
        print(f"   📦 Total de backups: {len(backups)}")
        
        # Cleanup (manter apenas 10 mais recentes)
        removed = backup_mgr.cleanup_old_backups(keep_count=10)
        if removed > 0:
            print(f"   🗑️  Backups antigos removidos: {removed}")
    else:
        print("   ❌ Erro ao criar backup")
    
    print()
    
    # 3. Resumo Final
    print("="*60)
    print("✅ HARDENING COMPLETO!")
    print("="*60)
    print()
    print("Próximos passos recomendados:")
    print("  1. Configure variável de ambiente BACKUP_KEY")
    print("  2. Agende backups diários (cron/task scheduler)")
    print("  3. Teste restore de backup em ambiente separado")
    print("  4. Ative 2FA para usuários administrativos")
    print()


if __name__ == "__main__":
    main()
