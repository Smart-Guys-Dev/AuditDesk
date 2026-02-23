import os
import json
import logging
from src.database.db_manager import get_session
from src.database.models_rules import (
    AuditRule, AuditRuleList, RuleCategory, RuleGroup
)

logger = logging.getLogger(__name__)

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

def run_migration(config_path: str = None):
    """
    Executa a migração de regras e listas do JSON para o banco de dados.
    """
    if config_path is None:
        # Tentar inferir caminho relativo ao projeto
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        config_path = os.path.join(base_dir, "src", "config")

    if not os.path.exists(config_path):
        logger.error(f"Diretório de configuração não encontrado: {config_path}")
        return

    logger.debug(f"Iniciando migração de regras a partir de: {config_path}")
    
    stats = {
        'rules_migrated': 0,
        'rules_skipped': 0,
        'lists_migrated': 0,
        'errors': []
    }

    # 1. Migrar Arquivos de Regras
    # Pasta raiz config
    _scan_and_migrate(config_path, stats)
    
    # Subpasta regras
    regras_folder = os.path.join(config_path, 'regras')
    if os.path.exists(regras_folder):
        _scan_and_migrate(regras_folder, stats)

    # 2. Migrar Listas
    for filename, list_id in LIST_FILES.items():
        filepath = os.path.join(config_path, filename)
        if os.path.exists(filepath):
            _migrate_list_file_safe(filepath, list_id, stats)
            
    total_r = stats['rules_migrated'] + stats['rules_skipped']
    total_l = stats['lists_migrated']
    if stats['rules_migrated'] > 0 or stats['errors']:
        logger.info(f"Regras sincronizadas ({total_r} regras, {total_l} listas)")
    else:
        logger.debug(f"Regras sincronizadas ({total_r} regras, {total_l} listas) — nenhuma alteração.")
    return stats

def _scan_and_migrate(folder, stats):
    for filename in os.listdir(folder):
        if filename.endswith('.json'):
            # Verificar se é arquivo de regra conhecido ou genérico
            if filename in FILE_TO_GROUP or filename.startswith('regras'):
                filepath = os.path.join(folder, filename)
                grupo = FILE_TO_GROUP.get(filename, "OUTROS")
                _migrate_rule_file_safe(filepath, grupo, stats)

def _migrate_rule_file_safe(filepath, grupo, stats):
    session = get_session()
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            rules = json.load(f)
        
        if not isinstance(rules, list):
            rules = [rules]
            
        migrated_count = 0
        
        for rule_data in rules:
            if not rule_data.get('id'): continue
            
            # Verificar existência
            existing = session.query(AuditRule).filter(
                AuditRule.id == rule_data['id']
            ).first()
            
            # Se não existe, cria. Se existe, PODEMOS atualizar (opcional, aqui vamos manter se não existir)
            # Para "auto-update" real, deveríamos atualizar se o JSON for mais novo ou diferente.
            # Por segurança e simplicidade inicial, vamos apenas inserir novas.
            
            if existing:
                stats['rules_skipped'] += 1
                continue
                
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
                criado_por='auto_migration',
                atualizado_por='auto_migration'
            )
            
            session.add(rule)
            migrated_count += 1
            stats['rules_migrated'] += 1
            
        if migrated_count > 0:
            session.commit()
            logger.debug(f"Arquivo {os.path.basename(filepath)}: {migrated_count} novas regras migradas.")
            
    except Exception as e:
        session.rollback()
        logger.error(f"Erro ao migrar arquivo {os.path.basename(filepath)}: {e}")
        stats['errors'].append(str(e))
    finally:
        session.close()

def _migrate_list_file_safe(filepath, list_id, stats):
    session = get_session()
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        if isinstance(data, list):
            valores = data
        elif isinstance(data, dict):
            valores = data.get('codigos', data.get('valores', list(data.values())[0] if data else []))
        else:
            valores = []
            
        existing = session.query(AuditRuleList).filter(AuditRuleList.id == list_id).first()
        
        if existing:
            # Atualiza lista existente
            existing.valores = json.dumps(valores)
            existing.quantidade = len(valores)
            existing.atualizado_por = 'auto_migration'
        else:
            rule_list = AuditRuleList(
                id=list_id,
                nome=os.path.basename(filepath).replace('.json', '').replace('_', ' ').title(),
                valores=json.dumps(valores),
                quantidade=len(valores),
                atualizado_por='auto_migration'
            )
            session.add(rule_list)
            
        session.commit()
        stats['lists_migrated'] += 1
        
    except Exception as e:
        session.rollback()
        logger.error(f"Erro ao migrar lista {os.path.basename(filepath)}: {e}")
        stats['errors'].append(str(e))
    finally:
        session.close()
