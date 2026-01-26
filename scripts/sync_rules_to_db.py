"""
Script de Sincronização: JSON -> SQLite

Este script sincroniza as regras definidas nos arquivos JSON com o banco de dados SQLite.
Útil para garantir que alterações nos JSONs sejam refletidas no banco.

Uso:
    python scripts/sync_rules_to_db.py [--dry-run]
"""

import sys
import os
import json
import argparse

# Setup paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from src.database.rule_repository import RuleRepository
from src.database.db_manager import get_session
from src.database.models_rules import AuditRule

def load_json_rules(config_dir):
    """Carrega todas as regras dos arquivos JSON"""
    rules_config_path = os.path.join(config_dir, "rules_config.json")
    
    if not os.path.exists(rules_config_path):
        print(f"ERRO: Arquivo não encontrado: {rules_config_path}")
        return []
    
    with open(rules_config_path, 'r', encoding='utf-8') as f:
        rules_config = json.load(f)
    
    all_rules = []
    grupos = rules_config.get("grupos_para_carregar", [])
    
    for grupo in grupos:
        if not grupo.get("ativo", True):
            continue
            
        arquivo = grupo.get("arquivo_regras")
        grupo_nome = grupo.get("nome_grupo", "OUTROS")
        
        arquivo_path = os.path.join(config_dir, arquivo)
        if not os.path.exists(arquivo_path):
            print(f"AVISO: Arquivo não encontrado: {arquivo_path}")
            continue
        
        try:
            with open(arquivo_path, 'r', encoding='utf-8') as f:
                regras = json.load(f)
            
            if isinstance(regras, list):
                for regra in regras:
                    regra['_grupo_arquivo'] = grupo_nome
                    all_rules.append(regra)
                print(f"   Carregado: {arquivo} ({len(regras)} regras)")
        except Exception as e:
            print(f"ERRO ao carregar {arquivo}: {e}")
    
    return all_rules


def sync_rule_to_db(rule_data, dry_run=False):
    """Sincroniza uma regra com o banco de dados"""
    rule_id = rule_data.get('id')
    if not rule_id:
        return None, "sem_id"
    
    # Verificar se existe
    existing = RuleRepository.get_rule_by_id(rule_id)
    
    if existing:
        # Atualizar regra existente
        if dry_run:
            return existing, "atualizar_dry"
        
        updates = {
            'descricao': rule_data.get('descricao', ''),
            'ativo': rule_data.get('ativo', True),
            'condicoes': rule_data.get('condicoes', {}),
            'acao': rule_data.get('acao', {}),
            'log_sucesso': rule_data.get('log_sucesso', '')
        }
        
        # Verificar se mudou
        import json
        existing_cond = json.loads(existing.condicoes) if existing.condicoes else {}
        existing_acao = json.loads(existing.acao) if existing.acao else {}
        
        new_cond = rule_data.get('condicoes', {})
        new_acao = rule_data.get('acao', {})
        
        if (existing_cond == new_cond and 
            existing_acao == new_acao and
            existing.descricao == rule_data.get('descricao', '') and
            existing.ativo == rule_data.get('ativo', True)):
            return existing, "sem_mudanca"
        
        updated = RuleRepository.update_rule(
            rule_id, 
            updates, 
            atualizado_por="sync_script",
            motivo="Sincronização com JSON"
        )
        return updated, "atualizado"
    else:
        # Criar nova regra
        if dry_run:
            return None, "criar_dry"
        
        # Preparar dados para criação
        create_data = {
            'id': rule_id,
            'codigo': rule_id[:50],
            'categoria': rule_data.get('metadata_glosa', {}).get('categoria', 'VALIDACAO'),
            'grupo': rule_data.get('_grupo_arquivo', 'OUTROS'),
            'nome': rule_data.get('descricao', '')[:200],
            'descricao': rule_data.get('descricao', ''),
            'ativo': rule_data.get('ativo', True),
            'prioridade': rule_data.get('prioridade', 100),
            'condicoes': rule_data.get('condicoes', {}),
            'acao': rule_data.get('acao', {}),
            'log_sucesso': rule_data.get('log_sucesso', ''),
            'impacto': rule_data.get('metadata_glosa', {}).get('impacto', 'MEDIO'),
            'contabilizar': True
        }
        
        try:
            new_rule = RuleRepository.create_rule(create_data, criado_por="sync_script")
            return new_rule, "criado"
        except Exception as e:
            return None, f"erro:{e}"


def main():
    parser = argparse.ArgumentParser(description='Sincroniza regras JSON com banco de dados SQLite')
    parser.add_argument('--dry-run', action='store_true', help='Simular sem aplicar mudanças')
    args = parser.parse_args()
    
    print("=" * 60)
    print("SINCRONIZAÇÃO DE REGRAS: JSON -> SQLite")
    print("=" * 60)
    
    if args.dry_run:
        print("\n[DRY-RUN] Modo simulação ativado - nenhuma alteração será feita\n")
    
    config_dir = os.path.join(project_root, "src", "config")
    print(f"Config dir: {config_dir}")
    
    # Carregar regras do JSON
    print("\n1. Carregando regras do JSON...")
    json_rules = load_json_rules(config_dir)
    print(f"   Total de regras nos JSONs: {len(json_rules)}")
    
    # Verificar regras no banco
    print("\n2. Verificando regras no banco...")
    db_rules = RuleRepository.get_rules_as_dicts(only_active=False)
    print(f"   Total de regras no banco: {len(db_rules)}")
    
    # Sincronizar
    print("\n3. Sincronizando...")
    stats = {
        'criado': 0,
        'atualizado': 0,
        'sem_mudanca': 0,
        'erro': 0
    }
    
    for rule_data in json_rules:
        result, status = sync_rule_to_db(rule_data, dry_run=args.dry_run)
        
        if 'dry' in status:
            base_status = status.replace('_dry', '')
            stats[base_status] = stats.get(base_status, 0) + 1
        elif status.startswith('erro'):
            stats['erro'] += 1
            print(f"   ERRO: {rule_data.get('id')} - {status}")
        else:
            stats[status] = stats.get(status, 0) + 1
            if status in ['criado', 'atualizado']:
                print(f"   {status.upper()}: {rule_data.get('id')}")
    
    # Relatório final
    print("\n" + "=" * 60)
    print("RESULTADO DA SINCRONIZAÇÃO")
    print("=" * 60)
    print(f"   Criadas:       {stats.get('criado', 0)}")
    print(f"   Atualizadas:   {stats.get('atualizado', 0)}")
    print(f"   Sem mudança:   {stats.get('sem_mudanca', 0)}")
    print(f"   Erros:         {stats.get('erro', 0)}")
    print("=" * 60)
    
    if not args.dry_run:
        # Invalidar cache
        RuleRepository.invalidate_cache()
        print("\n✅ Cache de regras invalidado.")
    
    return stats


if __name__ == "__main__":
    main()
