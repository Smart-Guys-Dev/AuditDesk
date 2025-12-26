#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para adicionar suporte a ROI Potencial em get_roi_stats()
"""

# Ler arquivo
with open('src/database/db_manager.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Substituir função get_roi_stats
old_function = '''def get_roi_stats():
    """
    Retorna estatísticas consolidadas de ROI.
    """
    session = get_session()
    stats = {
        'total_saved': 0.0,
        'total_corrections': 0,
        'top_rules': []
    }
    try:
        metrics = session.query(ROIMetrics).all()
        stats['total_corrections'] = len(metrics)
        stats['total_saved'] = sum(m.financial_impact for m in metrics)
        
        # Top regras
        from sqlalchemy import func
        top_rules_query = session.query(
            ROIMetrics.rule_id,
            ROIMetrics.rule_description,
            func.count(ROIMetrics.id).label('count'),
            func.sum(ROIMetrics.financial_impact).label('total_impact')
        ).group_by(ROIMetrics.rule_id).order_by(func.sum(ROIMetrics.financial_impact).desc()).limit(5).all()
        
        for r in top_rules_query:
            stats['top_rules'].append({
                'rule_id': r.rule_id,
                'description': r.rule_description,
                'count': r.count,
                'total_impact': r.total_impact
            })
            
    except Exception as e:
        print(f"Erro ao buscar estatísticas de ROI: {e}")
    finally:
        session.close()
        
    return stats'''

new_function = '''def get_roi_stats():
    """
    Retorna estatísticas consolidadas de ROI (Realizado + Potencial).
    """
    session = get_session()
    stats = {
        'total_saved': 0.0,  # ROI Realizado (correções)
        'total_corrections': 0,
        'roi_potencial': 0.0,  # ROI Potencial (alertas)
        'total_alertas': 0,
        'roi_total': 0.0,  # Soma total
        'top_rules': []
    }
    try:
        from sqlalchemy import func
        from .models import AlertMetrics
        
        # ROI REALIZADO (Correções automáticas)
        metrics = session.query(ROIMetrics).all()
        stats['total_corrections'] = len(metrics)
        stats['total_saved'] = sum(m.financial_impact for m in metrics)
        
        # ROI POTENCIAL (Alertas pendentes)
        alertas = session.query(AlertMetrics).filter_by(status='POTENCIAL').all()
        stats['total_alertas'] = len(alertas)
        stats['roi_potencial'] = sum(a.financial_impact for a in alertas)
        
        # ROI TOTAL
        stats['roi_total'] = stats['total_saved'] + stats['roi_potencial']
        
        # Top regras (mantém lógica existente)
        top_rules_query = session.query(
            ROIMetrics.rule_id,
            ROIMetrics.rule_description,
            func.count(ROIMetrics.id).label('count'),
            func.sum(ROIMetrics.financial_impact).label('total_impact')
        ).group_by(ROIMetrics.rule_id).order_by(func.sum(ROIMetrics.financial_impact).desc()).limit(5).all()
        
        for r in top_rules_query:
            stats['top_rules'].append({
                'rule_id': r.rule_id,
                'description': r.rule_description,
                'count': r.count,
                'total_impact': r.total_impact
            })
            
    except Exception as e:
        print(f"Erro ao buscar estatísticas de ROI: {e}")
    finally:
        session.close()
        
    return stats'''

# Substituir
content = content.replace(old_function, new_function)

# Salvar
with open('src/database/db_manager.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ get_roi_stats() atualizado com ROI Potencial!")
