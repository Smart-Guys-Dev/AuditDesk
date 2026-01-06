"""
Glox - Repositório de Regras

Gerencia operações CRUD para regras no banco SQLite.
Inclui versionamento automático e histórico de alterações.
"""

import json
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from .db_manager import get_session
from .models_rules import AuditRule, AuditRuleHistory, AuditRuleList, RuleCategory, RuleGroup

logger = logging.getLogger(__name__)


class RuleRepository:
    """
    Repositório para gerenciar regras no banco de dados.
    Implementa padrão Repository com versionamento automático.
    """
    
    # Cache em memória para performance
    _rules_cache: Optional[List[Dict]] = None
    _lists_cache: Dict[str, List[str]] = {}
    
    @classmethod
    def invalidate_cache(cls):
        """Invalida cache para forçar reload"""
        cls._rules_cache = None
        cls._lists_cache = {}
    
    # ==========================================
    # CRUD de Regras
    # ==========================================
    
    @staticmethod
    def get_all_rules(only_active: bool = True) -> List[AuditRule]:
        """Retorna todas as regras (ou apenas ativas)"""
        session = get_session()
        try:
            query = session.query(AuditRule)
            if only_active:
                query = query.filter(AuditRule.ativo == True)
            return query.order_by(AuditRule.prioridade, AuditRule.id).all()
        finally:
            session.close()
    
    @staticmethod
    def get_rules_as_dicts(only_active: bool = True) -> List[Dict]:
        """Retorna regras como lista de dicionários (formato rule_engine)"""
        if RuleRepository._rules_cache is not None and only_active:
            return RuleRepository._rules_cache
        
        rules = RuleRepository.get_all_rules(only_active)
        result = [rule.to_dict() for rule in rules]
        
        if only_active:
            RuleRepository._rules_cache = result
        
        return result
    
    @staticmethod
    def get_rule_by_id(rule_id: str) -> Optional[AuditRule]:
        """Busca regra por ID"""
        session = get_session()
        try:
            return session.query(AuditRule).filter(AuditRule.id == rule_id).first()
        finally:
            session.close()
    
    @staticmethod
    def get_rules_by_group(grupo: str) -> List[AuditRule]:
        """Retorna regras de um grupo específico"""
        session = get_session()
        try:
            return session.query(AuditRule).filter(
                AuditRule.grupo == grupo,
                AuditRule.ativo == True
            ).order_by(AuditRule.prioridade).all()
        finally:
            session.close()
    
    @staticmethod
    def get_rules_by_category(categoria: str) -> List[AuditRule]:
        """Retorna regras de uma categoria específica"""
        session = get_session()
        try:
            return session.query(AuditRule).filter(
                AuditRule.categoria == categoria,
                AuditRule.ativo == True
            ).order_by(AuditRule.prioridade).all()
        finally:
            session.close()
    
    @staticmethod
    def create_rule(rule_data: Dict, criado_por: str = "system") -> AuditRule:
        """
        Cria uma nova regra no banco.
        
        Args:
            rule_data: Dicionário com dados da regra
            criado_por: Username de quem criou
            
        Returns:
            AuditRule criada
        """
        session = get_session()
        try:
            rule = AuditRule(
                id=rule_data['id'],
                codigo=rule_data.get('codigo', rule_data['id'][:50]),
                categoria=rule_data.get('categoria', 'VALIDACAO'),
                grupo=rule_data.get('grupo', 'OUTROS'),
                nome=rule_data.get('nome', rule_data.get('descricao', '')[:200]),
                descricao=rule_data.get('descricao', ''),
                ativo=rule_data.get('ativo', True),
                prioridade=rule_data.get('prioridade', 100),
                condicoes=json.dumps(rule_data.get('condicoes', {})),
                acao=json.dumps(rule_data.get('acao', {})),
                log_sucesso=rule_data.get('log_sucesso', ''),
                impacto_financeiro=rule_data.get('impacto', 'MEDIO'),
                contabilizar_roi=rule_data.get('contabilizar', True),
                versao=1,
                criado_por=criado_por,
                atualizado_por=criado_por
            )
            
            session.add(rule)
            session.commit()
            
            # Registrar no histórico
            RuleRepository._log_history(session, rule, "CREATE", criado_por)
            
            RuleRepository.invalidate_cache()
            logger.info(f"Regra criada: {rule.id}")
            
            return rule
        except Exception as e:
            session.rollback()
            logger.error(f"Erro ao criar regra: {e}")
            raise
        finally:
            session.close()
    
    @staticmethod
    def update_rule(rule_id: str, updates: Dict, atualizado_por: str = "system", 
                    motivo: str = "") -> Optional[AuditRule]:
        """
        Atualiza uma regra existente com versionamento.
        
        Args:
            rule_id: ID da regra
            updates: Campos a atualizar
            atualizado_por: Username de quem atualizou
            motivo: Motivo da alteração
            
        Returns:
            AuditRule atualizada ou None se não encontrada
        """
        session = get_session()
        try:
            rule = session.query(AuditRule).filter(AuditRule.id == rule_id).first()
            if not rule:
                return None
            
            # Salvar snapshot antes da alteração
            RuleRepository._log_history(session, rule, "UPDATE", atualizado_por, motivo)
            
            # Aplicar atualizações
            for key, value in updates.items():
                if key in ['condicoes', 'acao'] and isinstance(value, dict):
                    value = json.dumps(value)
                if hasattr(rule, key):
                    setattr(rule, key, value)
            
            rule.versao += 1
            rule.atualizado_por = atualizado_por
            rule.atualizado_em = datetime.utcnow()
            
            session.commit()
            RuleRepository.invalidate_cache()
            logger.info(f"Regra atualizada: {rule_id} (v{rule.versao})")
            
            return rule
        except Exception as e:
            session.rollback()
            logger.error(f"Erro ao atualizar regra: {e}")
            raise
        finally:
            session.close()
    
    @staticmethod
    def toggle_rule(rule_id: str, ativo: bool, atualizado_por: str = "system") -> bool:
        """Ativa ou desativa uma regra"""
        result = RuleRepository.update_rule(
            rule_id, 
            {'ativo': ativo}, 
            atualizado_por,
            f"{'Ativada' if ativo else 'Desativada'}"
        )
        return result is not None
    
    @staticmethod
    def delete_rule(rule_id: str, deletado_por: str = "system") -> bool:
        """
        Remove uma regra (soft delete recomendado via toggle).
        Para exclusão permanente, use este método.
        """
        session = get_session()
        try:
            rule = session.query(AuditRule).filter(AuditRule.id == rule_id).first()
            if not rule:
                return False
            
            # Salvar snapshot antes de deletar
            RuleRepository._log_history(session, rule, "DELETE", deletado_por)
            
            session.delete(rule)
            session.commit()
            RuleRepository.invalidate_cache()
            logger.info(f"Regra deletada: {rule_id}")
            
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Erro ao deletar regra: {e}")
            return False
        finally:
            session.close()
    
    # ==========================================
    # Histórico
    # ==========================================
    
    @staticmethod
    def _log_history(session: Session, rule: AuditRule, tipo: str, 
                     usuario: str, motivo: str = ""):
        """Registra alteração no histórico"""
        history = AuditRuleHistory(
            rule_id=rule.id,
            versao=rule.versao,
            dados_anteriores=json.dumps({
                'ativo': rule.ativo,
                'condicoes': rule.condicoes,
                'acao': rule.acao,
                'prioridade': rule.prioridade
            }),
            tipo_alteracao=tipo,
            alterado_por=usuario,
            motivo=motivo
        )
        session.add(history)
    
    @staticmethod
    def get_rule_history(rule_id: str) -> List[AuditRuleHistory]:
        """Retorna histórico de alterações de uma regra"""
        session = get_session()
        try:
            return session.query(AuditRuleHistory).filter(
                AuditRuleHistory.rule_id == rule_id
            ).order_by(AuditRuleHistory.alterado_em.desc()).all()
        finally:
            session.close()
    
    # ==========================================
    # Listas de Códigos
    # ==========================================
    
    @staticmethod
    def get_list(list_id: str) -> List[str]:
        """Retorna valores de uma lista de códigos"""
        if list_id in RuleRepository._lists_cache:
            return RuleRepository._lists_cache[list_id]
        
        session = get_session()
        try:
            rule_list = session.query(AuditRuleList).filter(
                AuditRuleList.id == list_id
            ).first()
            
            if rule_list:
                valores = rule_list.get_valores_list()
                RuleRepository._lists_cache[list_id] = valores
                return valores
            return []
        finally:
            session.close()
    
    @staticmethod
    def update_list(list_id: str, valores: List[str], 
                    atualizado_por: str = "system") -> bool:
        """Atualiza uma lista de códigos"""
        session = get_session()
        try:
            rule_list = session.query(AuditRuleList).filter(
                AuditRuleList.id == list_id
            ).first()
            
            if not rule_list:
                rule_list = AuditRuleList(id=list_id, nome=list_id)
                session.add(rule_list)
            
            rule_list.valores = json.dumps(valores)
            rule_list.quantidade = len(valores)
            rule_list.atualizado_por = atualizado_por
            
            session.commit()
            RuleRepository._lists_cache.pop(list_id, None)
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Erro ao atualizar lista: {e}")
            return False
        finally:
            session.close()
    
    # ==========================================
    # Estatísticas
    # ==========================================
    
    @staticmethod
    def get_stats() -> Dict:
        """Retorna estatísticas das regras"""
        session = get_session()
        try:
            total = session.query(AuditRule).count()
            ativas = session.query(AuditRule).filter(AuditRule.ativo == True).count()
            
            por_grupo = {}
            for grupo in RuleGroup:
                count = session.query(AuditRule).filter(
                    AuditRule.grupo == grupo.value,
                    AuditRule.ativo == True
                ).count()
                if count > 0:
                    por_grupo[grupo.value] = count
            
            por_categoria = {}
            for cat in RuleCategory:
                count = session.query(AuditRule).filter(
                    AuditRule.categoria == cat.value,
                    AuditRule.ativo == True
                ).count()
                if count > 0:
                    por_categoria[cat.value] = count
            
            return {
                'total': total,
                'ativas': ativas,
                'inativas': total - ativas,
                'por_grupo': por_grupo,
                'por_categoria': por_categoria
            }
        finally:
            session.close()


# Funções de conveniência (API simplificada)
def get_active_rules() -> List[Dict]:
    """Retorna regras ativas como lista de dicionários"""
    return RuleRepository.get_rules_as_dicts(only_active=True)

def get_list_values(list_id: str) -> List[str]:
    """Retorna valores de uma lista de códigos"""
    return RuleRepository.get_list(list_id)
