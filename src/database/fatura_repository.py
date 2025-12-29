"""
AuditPlus v2.0 - Repositório de Faturas

Funções para consulta e gerenciamento de faturas importadas.
"""

from typing import Optional, List, Dict
from datetime import datetime
from sqlalchemy import func
from .db_manager import get_session
from .models_fatura import Fatura, FaturaHistorico


def buscar_fatura(nro_fatura: str) -> Optional[Dict]:
    """
    Busca uma fatura pelo número.
    
    Args:
        nro_fatura: Número da fatura (pode ser parcial)
    
    Returns:
        Dicionário com dados da fatura ou None
    """
    session = get_session()
    try:
        # Busca exata primeiro
        fatura = session.query(Fatura).filter(
            Fatura.nro_fatura == nro_fatura
        ).first()
        
        # Se não encontrou, tenta busca parcial
        if not fatura:
            fatura = session.query(Fatura).filter(
                Fatura.nro_fatura.contains(nro_fatura)
            ).first()
        
        if fatura:
            resultado = fatura.to_dict()
            resultado['historico'] = [h.to_dict() for h in fatura.historico[:10]]
            return resultado
        
        return None
    except Exception as e:
        print(f"Erro ao buscar fatura: {e}")
        return None
    finally:
        session.close()


def criar_ou_atualizar_fatura(dados: Dict) -> bool:
    """
    Cria ou atualiza uma fatura (upsert).
    Se já existir pelo nro_fatura, atualiza os dados.
    
    Args:
        dados: Dicionário com dados da fatura
    
    Returns:
        True se sucesso
    """
    session = get_session()
    try:
        nro_fatura = dados.get('nro_fatura')
        if not nro_fatura:
            return False
        
        # Verificar se já existe
        fatura = session.query(Fatura).filter(
            Fatura.nro_fatura == nro_fatura
        ).first()
        
        if fatura:
            # Atualizar campos
            for key, value in dados.items():
                if hasattr(fatura, key) and key != 'id':
                    setattr(fatura, key, value)
        else:
            # Criar nova
            fatura = Fatura(**dados)
            session.add(fatura)
        
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f"Erro ao salvar fatura: {e}")
        return False
    finally:
        session.close()


def adicionar_historico(nro_fatura: str, acao: str, origem: str = None, detalhes: str = None) -> bool:
    """
    Adiciona um evento ao histórico da fatura.
    
    Args:
        nro_fatura: Número da fatura
        acao: Descrição da ação (ex: "Enviada para NCMB")
        origem: Sistema de origem (SGU, NCMB, AuditPlus)
        detalhes: Informações adicionais
    """
    session = get_session()
    try:
        fatura = session.query(Fatura).filter(
            Fatura.nro_fatura == nro_fatura
        ).first()
        
        if not fatura:
            return False
        
        historico = FaturaHistorico(
            fatura_id=fatura.id,
            acao=acao,
            origem=origem,
            detalhes=detalhes
        )
        session.add(historico)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f"Erro ao adicionar histórico: {e}")
        return False
    finally:
        session.close()


def get_estatisticas_faturas() -> Dict:
    """
    Retorna estatísticas gerais das faturas importadas.
    """
    session = get_session()
    try:
        total = session.query(func.count(Fatura.id)).scalar() or 0
        
        por_status = {}
        for status in ['PENDENTE', 'ENVIADA', 'CANCELADA', 'GLOSADA']:
            count = session.query(func.count(Fatura.id)).filter(
                Fatura.status == status
            ).scalar() or 0
            por_status[status] = count
        
        valor_total = session.query(func.sum(Fatura.valor)).scalar() or 0
        
        corrigidas_auditplus = session.query(func.count(Fatura.id)).filter(
            Fatura.corrigida_auditplus == True
        ).scalar() or 0
        
        return {
            'total': total,
            'por_status': por_status,
            'valor_total': valor_total,
            'corrigidas_auditplus': corrigidas_auditplus,
            'taxa_correcao': (corrigidas_auditplus / total * 100) if total > 0 else 0
        }
    except Exception as e:
        print(f"Erro ao obter estatísticas: {e}")
        return {'total': 0, 'por_status': {}, 'valor_total': 0}
    finally:
        session.close()


def importar_lote(faturas: List[Dict], origem: str = "Excel") -> Dict:
    """
    Importa um lote de faturas de uma vez.
    
    Args:
        faturas: Lista de dicionários com dados das faturas
        origem: Nome do arquivo/sistema de origem
    
    Returns:
        Estatísticas da importação
    """
    session = get_session()
    stats = {'criadas': 0, 'atualizadas': 0, 'erros': 0}
    
    try:
        for dados in faturas:
            nro_fatura = dados.get('nro_fatura')
            if not nro_fatura:
                stats['erros'] += 1
                continue
            
            # Verificar se já existe
            fatura = session.query(Fatura).filter(
                Fatura.nro_fatura == nro_fatura
            ).first()
            
            if fatura:
                # Atualizar
                for key, value in dados.items():
                    if hasattr(fatura, key) and key not in ['id', 'nro_fatura']:
                        setattr(fatura, key, value)
                stats['atualizadas'] += 1
                acao = "Dados atualizados"
            else:
                # Criar
                dados['arquivo_origem'] = origem
                fatura = Fatura(**dados)
                session.add(fatura)
                session.flush()  # Obter ID
                stats['criadas'] += 1
                acao = f"Importada de {origem}"
            
            # Adicionar histórico
            historico = FaturaHistorico(
                fatura_id=fatura.id,
                acao=acao,
                origem=origem
            )
            session.add(historico)
        
        session.commit()
        return stats
    except Exception as e:
        session.rollback()
        print(f"Erro na importação em lote: {e}")
        stats['erros'] += 1
        return stats
    finally:
        session.close()


def get_faturas_por_auditor() -> List[Dict]:
    """
    Retorna contagem de faturas agrupadas por auditor/responsável.
    
    Returns:
        Lista de dicionários: [{'auditor': 'Nome', 'total': 100, 'valor': 50000.0}]
    """
    session = get_session()
    try:
        resultados = session.query(
            Fatura.responsavel,
            func.count(Fatura.id).label('total'),
            func.sum(Fatura.valor).label('valor_total')
        ).filter(
            Fatura.responsavel != None,
            Fatura.responsavel != ''
        ).group_by(
            Fatura.responsavel
        ).order_by(
            func.count(Fatura.id).desc()
        ).all()
        
        return [
            {
                'auditor': r.responsavel or 'Não atribuído',
                'total': r.total or 0,
                'valor': r.valor_total or 0.0
            }
            for r in resultados
        ]
    except Exception as e:
        print(f"Erro ao obter faturas por auditor: {e}")
        return []
    finally:
        session.close()
