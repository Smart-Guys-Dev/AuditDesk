"""
AuditPlus v2.0 - Script de Migração de Regras

Migra regras de arquivos JSON para o banco SQLite.
Mantém compatibilidade com estrutura antiga.

Uso:
    python scripts/migrate_rules_to_db.py [--dry-run] [--verbose]
"""

import sys
import os
import json
import argparse
from datetime import datetime

# Adicionar path do projeto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.db_manager import get_session, init_db
from src.database.models_rules import (
    AuditRule, AuditRuleHistory, AuditRuleList,
    RuleCategory, RuleGroup, LEGACY_GROUP_MAPPING
)


# Mapeamento de arquivo para grupo
FILE_TO_GROUP = {
    "regras_grupo_1200.json": "LAYOUT",
    "regras_grupo_1201.json": "TERAPIAS",
    "regras_tp_participacao.json": "PARTICIPACAO",
    "equipe_profissional.json": "EQUIPE_PROF",
    "cpf_prestadores.json": "EQUIPE_PROF",
    "cnes.json": "CNES",
    "conselho.json": "EQUIPE_PROF",
    "auditoria.json": "AUDITORIA",
    "internacao.json": "INTERNACAO",
    "procedimentos.json": "PROCEDIMENTOS",
    "pj_para_pf.json": "CONVERSAO",
    "outros.json": "OUTROS",
}

# Mapeamento de listas
LIST_FILES = {
    "codigos_equipe_obrigatoria.json": "EQUIPE_OBRIGATORIA",
    "codigos_terapias_seriadas.json": "TERAPIAS_SERIADAS",
    "codigos_cbo_medicos.json": "CBO_MEDICOS",
    "ignore_00.json": "IGNORE_00",
}


def detect_category(rule: dict) -> str:
    """Detecta categoria da regra baseado em metadados ou tipo de ação"""
    # Verificar metadados existentes
    metadata = rule.get('metadata_glosa', {})
    if metadata:
        cat = metadata.get('categoria', '')
        if cat in ['GLOSA_GUIA', 'GLOSA_ITEM', 'VALIDACAO', 'OTIMIZACAO']:
            return cat
    
    # Inferir pela ação
    acao = rule.get('acao', {})
    tipo_acao = acao.get('tipo_acao', '')
    
    if 'remover' in tipo_acao.lower():
        return 'VALIDACAO'
    elif 'garantir' in tipo_acao.lower():
        return 'GLOSA_ITEM'
    elif 'reordenar' in tipo_acao.lower():
        return 'LAYOUT' if 'LAYOUT' in RuleCategory.__members__ else 'VALIDACAO'
    
    return 'VALIDACAO'


def migrate_rules(config_path: str, dry_run: bool = False, verbose: bool = False):
    """
    Migra regras de arquivos JSON para SQLite.
    
    Args:
        config_path: Caminho da pasta de configurações
        dry_run: Se True, não salva no banco
        verbose: Se True, mostra detalhes
    """
    
    stats = {
        'rules_migrated': 0,
        'rules_skipped': 0,
        'lists_migrated': 0,
        'errors': []
    }
    
    print("=" * 60)
    print("🚀 MIGRAÇÃO DE REGRAS PARA SQLITE")
    print("=" * 60)
    print(f"📁 Pasta: {config_path}")
    print(f"🔧 Dry Run: {dry_run}")
    print()
    
    # 1. Migrar arquivos de regras
    print("📋 MIGRANDO REGRAS...")
    print("-" * 40)
    
    # Pasta principal
    for filename in os.listdir(config_path):
        if filename.endswith('.json') and filename.startswith('regras'):
            filepath = os.path.join(config_path, filename)
            grupo = FILE_TO_GROUP.get(filename, "OUTROS")
            _migrate_rule_file_safe(filepath, grupo, stats, dry_run, verbose)
    
    # Subpasta regras/
    regras_folder = os.path.join(config_path, 'regras')
    if os.path.exists(regras_folder):
        for filename in os.listdir(regras_folder):
            if filename.endswith('.json'):
                filepath = os.path.join(regras_folder, filename)
                grupo = FILE_TO_GROUP.get(filename, "OUTROS")
                _migrate_rule_file_safe(filepath, grupo, stats, dry_run, verbose)
    
    # 2. Migrar listas de códigos
    print()
    print("📋 MIGRANDO LISTAS DE CÓDIGOS...")
    print("-" * 40)
    
    for filename, list_id in LIST_FILES.items():
        filepath = os.path.join(config_path, filename)
        if os.path.exists(filepath):
            _migrate_list_file_safe(filepath, list_id, stats, dry_run, verbose)
    
    # Resumo
    print()
    print("=" * 60)
    print("📊 RESUMO DA MIGRAÇÃO")
    print("=" * 60)
    print(f"✅ Regras migradas:  {stats['rules_migrated']}")
    print(f"⏭️  Regras ignoradas: {stats['rules_skipped']}")
    print(f"✅ Listas migradas:  {stats['lists_migrated']}")
    print(f"❌ Erros:            {len(stats['errors'])}")
    
    if stats['errors']:
        print()
        print("Erros encontrados:")
        for err in stats['errors'][:5]:
            print(f"  - {err[:100]}")
    
    return stats


def _migrate_rule_file_safe(filepath: str, grupo: str, stats: dict, 
                            dry_run: bool, verbose: bool):
    """Migra um arquivo de regras com sessão isolada"""
    filename = os.path.basename(filepath)
    session = get_session()
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            rules = json.load(f)
        
        if not isinstance(rules, list):
            rules = [rules]
        
        migrated = 0
        for rule_data in rules:
            if not rule_data.get('id'):
                continue
            
            # Verificar se já existe
            existing = session.query(AuditRule).filter(
                AuditRule.id == rule_data['id']
            ).first()
            
            if existing:
                stats['rules_skipped'] += 1
                continue
            
            # Criar regra
            categoria = detect_category(rule_data)
            
            rule = AuditRule(
                id=rule_data['id'],
                codigo=rule_data['id'][:50],
                categoria=categoria,
                grupo=grupo,
                nome=rule_data.get('descricao', rule_data['id'])[:200],
                descricao=rule_data.get('descricao', ''),
                ativo=rule_data.get('ativo', True),
                prioridade=rule_data.get('prioridade', 100),
                condicoes=json.dumps(rule_data.get('condicoes', {})),
                acao=json.dumps(rule_data.get('acao', {})),
                log_sucesso=rule_data.get('log_sucesso', ''),
                impacto_financeiro=rule_data.get('metadata_glosa', {}).get('impacto', 'MEDIO'),
                contabilizar_roi=rule_data.get('metadata_glosa', {}).get('contabilizar', True),
                versao=1,
                criado_por='migration',
                atualizado_por='migration'
            )
            
            if not dry_run:
                session.add(rule)
            
            migrated += 1
            stats['rules_migrated'] += 1
            
            if verbose:
                print(f"  + {rule_data['id']}")
        
        if not dry_run and migrated > 0:
            session.commit()
        
        print(f"  📄 {filename}: {migrated} regras")
        
    except Exception as e:
        session.rollback()
        print(f"  ❌ {filename}: ERRO - {str(e)[:80]}")
        stats['errors'].append(f"{filename}: {e}")
    finally:
        session.close()


def _migrate_list_file_safe(filepath: str, list_id: str, stats: dict,
                            dry_run: bool, verbose: bool):
    """Migra um arquivo de lista de códigos com sessão isolada"""
    filename = os.path.basename(filepath)
    session = get_session()
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extrair lista de valores
        if isinstance(data, list):
            valores = data
        elif isinstance(data, dict):
            valores = data.get('codigos', data.get('valores', list(data.values())[0] if data else []))
        else:
            valores = []
        
        # Verificar se já existe
        existing = session.query(AuditRuleList).filter(
            AuditRuleList.id == list_id
        ).first()
        
        if existing:
            if not dry_run:
                existing.valores = json.dumps(valores)
                existing.quantidade = len(valores)
                existing.atualizado_por = 'migration'
                session.commit()
            print(f"  📄 {filename}: {len(valores)} itens (atualizado)")
        else:
            rule_list = AuditRuleList(
                id=list_id,
                nome=filename.replace('.json', '').replace('_', ' ').title(),
                descricao=f"Migrado de {filename}",
                valores=json.dumps(valores),
                quantidade=len(valores),
                atualizado_por='migration'
            )
            
            if not dry_run:
                session.add(rule_list)
                session.commit()
            
            print(f"  📄 {filename}: {len(valores)} itens")
        
        stats['lists_migrated'] += 1
        
    except Exception as e:
        session.rollback()
        print(f"  ❌ {filename}: ERRO - {str(e)[:80]}")
        stats['errors'].append(f"{filename}: {e}")
    finally:
        session.close()


def main():
    parser = argparse.ArgumentParser(description='Migrar regras JSON para SQLite')
    parser.add_argument('--dry-run', action='store_true', 
                        help='Simular sem salvar no banco')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Mostrar detalhes')
    parser.add_argument('--config-path', default='src/config',
                        help='Caminho das configurações')
    
    args = parser.parse_args()
    
    # Inicializar banco
    print("🔧 Inicializando banco de dados...")
    init_db()
    
    # Criar tabelas de regras (se não existirem)
    from src.database.models import Base
    from src.database.db_manager import engine
    from src.database.models_rules import AuditRule, AuditRuleHistory, AuditRuleList
    Base.metadata.create_all(engine)
    print("✅ Tabelas criadas/verificadas")
    print()
    
    # Migrar
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), args.config_path)
    migrate_rules(config_path, args.dry_run, args.verbose)


if __name__ == '__main__':
    main()
