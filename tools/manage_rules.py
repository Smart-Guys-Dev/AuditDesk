"""
Interface CLI para gerenciar regras em produção.

Permite habilitar/desabilitar regras, ver audit log, fazer rollback.
"""
import argparse
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.business.rules.rule_config_manager import RuleConfigManager


def cmd_disable(args):
    """Desabilita uma regra"""
    manager = RuleConfigManager()
    
    success = manager.disable_rule(
        rule_file=args.file,
        rule_id=args.rule_id,
        user=args.user,
        reason=args.reason
    )
    
    if success:
        print(f"✅ Regra {args.rule_id} desabilitada com sucesso!")
        print(f"   Arquivo: {args.file}")
        if args.reason:
            print(f"   Motivo: {args.reason}")
    else:
        print(f"❌ Erro ao desabilitar regra {args.rule_id}")
        sys.exit(1)


def cmd_enable(args):
    """Habilita uma regra"""
    manager = RuleConfigManager()
    
    success = manager.enable_rule(
        rule_file=args.file,
        rule_id=args.rule_id,
        user=args.user
    )
    
    if success:
        print(f"✅ Regra {args.rule_id} habilitada com sucesso!")
        print(f"   Arquivo: {args.file}")
    else:
        print(f"❌ Erro ao habilitar regra {args.rule_id}")
        sys.exit(1)


def cmd_status(args):
    """Verifica status de uma regra"""
    manager = RuleConfigManager()
    
    status = manager.get_rule_status(args.file, args.rule_id)
    
    if status is None:
        print(f"❓ Regra {args.rule_id} não encontrada em {args.file}")
        sys.exit(1)
    elif status:
        print(f"✅ Regra {args.rule_id} está HABILITADA")
    else:
        print(f"🚫 Regra {args.rule_id} está DESABILITADA")


def cmd_list_disabled(args):
    """Lista regras desabilitadas"""
    manager = RuleConfigManager()
    
    disabled = manager.list_disabled_rules(args.file)
    
    if not disabled:
        print("✅ Nenhuma regra desabilitada")
        return
    
    print(f"\n🚫 Regras Desabilitadas ({len(disabled)}):")
    print("="*70)
    
    for rule in disabled:
        print(f"  Arquivo: {rule['file']}")
        print(f"  ID: {rule['id']}")
        print(f"  Descrição: {rule['descricao']}")
        print("-"*70)


def cmd_audit_log(args):
    """Mostra audit log"""
    manager = RuleConfigManager()
    
    entries = manager.get_audit_log(limit=args.limit)
    
    if not entries:
        print("📋 Audit log vazio")
        return
    
    print(f"\n📋 Audit Log (últimas {len(entries)} entradas):")
    print("="*70)
    
    for entry in entries:
        print(f"  ⏰ {entry['timestamp']}")
        print(f"  👤 Usuário: {entry['user']}")
        print(f"  📁 Arquivo: {entry['file']}")
        print(f"  🔧 Ação: {entry['action']}")
        print(f"  📝 Detalhes: {entry['details']}")
        print("-"*70)


def cmd_versions(args):
    """Lista versões disponíveis"""
    manager = RuleConfigManager()
    
    versions = manager.list_versions(args.file)
    
    if not versions:
        print(f"📦 Nenhuma versão disponível para {args.file}")
        return
    
    print(f"\n📦 Versões Disponíveis de {args.file}:")
    print("="*70)
    
    for v in versions:
        print(f"  📅 Timestamp: {v['timestamp']}")
        print(f"  📁 Arquivo: {v['file']}")
        print(f"  💾 Tamanho: {v['size']} bytes")
        print("-"*70)


def cmd_rollback(args):
    """Faz rollback para versão anterior"""
    manager = RuleConfigManager()
    
    # Confirmar com usuário
    if not args.yes:
        print(f"⚠️  ATENÇÃO: Você está prestes a fazer rollback de:")
        print(f"   Arquivo: {args.file}")
        print(f"   Versão: {args.timestamp}")
        print()
        confirm = input("Tem certeza? (digite 'sim' para confirmar): ")
        
        if confirm.lower() != 'sim':
            print("❌ Rollback cancelado")
            return
    
    success = manager.rollback(
        rule_file=args.file,
        version_timestamp=args.timestamp,
        user=args.user
    )
    
    if success:
        print(f"✅ Rollback realizado com sucesso!")
        print(f"   {args.file} restaurado para versão {args.timestamp}")
    else:
        print(f"❌ Erro ao fazer rollback")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='CLI para gerenciar regras do AuditPlus v2.0'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponíveis')
    
    # Comando: disable
    parser_disable = subparsers.add_parser('disable', help='Desabilita uma regra')
    parser_disable.add_argument('--file', required=True, help='Arquivo de regras (ex: regras_grupo_1200.json)')
    parser_disable.add_argument('--rule-id', required=True, help='ID da regra')
    parser_disable.add_argument('--reason', default='', help='Motivo da desabilitação')
    parser_disable.add_argument('--user', default='admin', help='Usuário fazendo a mudança')
    parser_disable.set_defaults(func=cmd_disable)
    
    # Comando: enable
    parser_enable = subparsers.add_parser('enable', help='Habilita uma regra')
    parser_enable.add_argument('--file', required=True, help='Arquivo de regras')
    parser_enable.add_argument('--rule-id', required=True, help='ID da regra')
    parser_enable.add_argument('--user', default='admin', help='Usuário fazendo a mudança')
    parser_enable.set_defaults(func=cmd_enable)
    
    # Comando: status
    parser_status = subparsers.add_parser('status', help='Verifica status de uma regra')
    parser_status.add_argument('--file', required=True, help='Arquivo de regras')
    parser_status.add_argument('--rule-id', required=True, help='ID da regra')
    parser_status.set_defaults(func=cmd_status)
    
    # Comando: list-disabled
    parser_list = subparsers.add_parser('list-disabled', help='Lista regras desabilitadas')
    parser_list.add_argument('--file', help='Arquivo específico (opcional)')
    parser_list.set_defaults(func=cmd_list_disabled)
    
    # Comando: audit-log
    parser_audit = subparsers.add_parser('audit-log', help='Mostra audit log')
    parser_audit.add_argument('--limit', type=int, default=50, help='Número de entradas (padrão: 50)')
    parser_audit.set_defaults(func=cmd_audit_log)
    
    # Comando: versions
    parser_versions = subparsers.add_parser('versions', help='Lista versões disponíveis')
    parser_versions.add_argument('--file', required=True, help='Arquivo de regras')
    parser_versions.set_defaults(func=cmd_versions)
    
    # Comando: rollback
    parser_rollback = subparsers.add_parser('rollback', help='Faz rollback para versão anterior')
    parser_rollback.add_argument('--file', required=True, help='Arquivo de regras')
    parser_rollback.add_argument('--timestamp', required=True, help='Timestamp da versão (YYYYMMDD_HHMMSS)')
    parser_rollback.add_argument('--user', default='admin', help='Usuário fazendo rollback')
    parser_rollback.add_argument('--yes', '-y', action='store_true', help='Confirmar automaticamente')
    parser_rollback.set_defaults(func=cmd_rollback)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Executar comando
    args.func(args)


if __name__ == '__main__':
    main()
