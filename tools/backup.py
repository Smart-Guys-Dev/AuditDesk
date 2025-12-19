"""
Sistema de backup automático para AuditPlus v2.0.

Realiza backup de:
- Configurações de regras
- Banco de dados
- Logs de audit
"""
import shutil
import os
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def create_backup(backup_dir: str = "backups"):
    """
    Cria backup completo do sistema.
    
    Args:
        backup_dir: Diretório raiz para backups
        
    Returns:
        Path do backup criado
    """
    # Timestamp para o backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = Path(backup_dir) / f"backup_{timestamp}"
    backup_path.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Criando backup em: {backup_path}")
    
    # 1. Backup de configurações de regras
    config_src = Path("config")
    if config_src.exists():
        config_dst = backup_path / "config"
        shutil.copytree(config_src, config_dst)
        logger.info("✅ Configurações de regras copiadas")
    
    # 2. Backup de banco de dados
    db_src = Path("database/auditplus.db")
    if db_src.exists():
        db_dst = backup_path / "database"
        db_dst.mkdir(exist_ok=True)
        shutil.copy2(db_src, db_dst / "auditplus.db")
        logger.info("✅ Banco de dados copiado")
    
    # 3. Backup de audit logs
    audit_log = Path("config/.audit_log.jsonl")
    if audit_log.exists():
        shutil.copy2(audit_log, backup_path / "audit_log.jsonl")
        logger.info("✅ Audit log copiado")
    
    # 4. Criar manifesto
    manifest = {
        'timestamp': timestamp,
        'date': datetime.now().isoformat(),
        'files_backed_up': len(list(backup_path.rglob("*"))),
        'size_mb': sum(f.stat().st_size for f in backup_path.rglob("*") if f.is_file()) / 1024 / 1024
    }
    
    import json
    with open(backup_path / "manifest.json", 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\n✅ Backup criado com sucesso!")
    print(f"   Local: {backup_path}")
    print(f"   Arquivos: {manifest['files_backed_up']}")
    print(f"   Tamanho: {manifest['size_mb']:.2f} MB")
    
    return backup_path


def restore_backup(backup_path: str, confirm: bool = False):
    """
    Restaura backup.
    
    Args:
        backup_path: Path do backup a restaurar
        confirm: Se True, não pede confirmação
    """
    backup_path = Path(backup_path)
    
    if not backup_path.exists():
        logger.error(f"Backup não encontrado: {backup_path}")
        return False
    
    # Confirmar
    if not confirm:
        print(f"⚠️  ATENÇÃO: Você está prestes a restaurar backup de:")
        print(f"   {backup_path}")
        print("\n⚠️  Isso irá SOBRESCREVER as configurações atuais!")
        response = input("\nDigite 'CONFIRMO' para continuar: ")
        
        if response != 'CONFIRMO':
            print("❌ Restore cancelado")
            return False
    
    # Backup do estado atual antes de restore
    print("📦 Criando backup de segurança do estado atual...")
    create_backup("backups/pre_restore")
    
    # Restaurar configurações
    config_src = backup_path / "config"
    if config_src.exists():
        shutil.rmtree("config", ignore_errors=True)
        shutil.copytree(config_src, "config")
        print("✅ Configurações restauradas")
    
    # Restaurar banco de dados
    db_src = backup_path / "database/auditplus.db"
    if db_src.exists():
        Path("database").mkdir(exist_ok=True)
        shutil.copy2(db_src, "database/auditplus.db")
        print("✅ Banco de dados restaurado")
    
    print(f"\n✅ Restore concluído com sucesso!")
    return True


def cleanup_old_backups(backup_dir: str = "backups", keep_days: int = 30):
    """
    Remove backups antigos.
    
    Args:
        backup_dir: Diretório de backups
        keep_days: Manter backups dos últimos N dias
    """
    from datetime import timedelta
    
    cutoff_date = datetime.now() - timedelta(days=keep_days)
    deleted = 0
    
    for backup_folder in Path(backup_dir).glob("backup_*"):
        # Extrair data do nome
        try:
            date_str = backup_folder.name.split("_")[1]
            backup_date = datetime.strptime(date_str, "%Y%m%d")
            
            if backup_date < cutoff_date:
                shutil.rmtree(backup_folder)
                deleted += 1
                logger.info(f"Backup antigo removido: {backup_folder}")
        except:
            pass
    
    print(f"🧹 {deleted} backups antigos removidos (> {keep_days} dias)")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Sistema de backup AuditPlus')
    parser.add_argument('--create', action='store_true', help='Criar backup')
    parser.add_argument('--restore', help='Restaurar backup (path)')
    parser.add_argument('--cleanup', action='store_true', help='Limpar backups antigos')
    parser.add_argument('--keep-days', type=int, default=30, help='Dias para manter backups')
    parser.add_argument('--yes', action='store_true', help='Confirmar automaticamente')
    
    args = parser.parse_args()
    
    if args.create:
        create_backup()
    elif args.restore:
        restore_backup(args.restore, confirm=args.yes)
    elif args.cleanup:
        cleanup_old_backups(keep_days=args.keep_days)
    else:
        parser.print_help()
