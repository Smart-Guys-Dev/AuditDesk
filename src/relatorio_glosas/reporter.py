"""
Reporter - Gerador de Relatórios de Glosas Evitadas

Gera relatórios individuais por execução mostrando:
- Guias salvas (valor total)
- Itens corrigidos (valor por item)
- Otimizações (não contabilizadas)
- Resumo financeiro total
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json
from datetime import datetime
from .models import GlosaGuia, GlosaItem, Otimizacao

engine = create_engine('sqlite:///audit_plus.db')
Session = sessionmaker(bind=engine)


def gerar_relatorio_individual(execution_id):
    """
    Gera relatório detalhado para uma execução específica
    
    Args:
        execution_id: ID da execução
        
    Returns:
        dict: Relatório completo com resumo e detalhes
    """
    session = Session()
    
    try:
        # Buscar dados
        guias = session.query(GlosaGuia).filter_by(execution_id=execution_id).all()
        itens = session.query(GlosaItem).filter_by(execution_id=execution_id).all()
        otims = session.query(Otimizacao).filter_by(execution_id=execution_id).all()
        
        # Calcular totais
        total_guias = sum(g.valor_total_guia for g in guias)
        total_itens = sum(i.valor_total_item for i in itens)
        total_protegido = total_guias + total_itens
        
        # Montar relatório
        relatorio = {
            'execution_id': execution_id,
            'data_geracao': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            
            'resumo': {
                'total_guias_salvas': len(guias),
                'valor_guias': total_guias,
                'total_itens_corrigidos': len(itens),
                'valor_itens': total_itens,
                'total_protegido': total_protegido,
                'total_otimizacoes': len(otims)
            },
            
            'guias_salvas': [
                {
                    'guia_id': g.guia_id,
                    'file_name': g.file_name,
                    'valor_total': g.valor_total_guia,
                    'qtd_itens': g.qtd_itens,
                    'regras': json.loads(g.regras_aplicadas)
                }
                for g in guias
            ],
            
            'itens_corrigidos': [
                {
                    'guia_id': i.guia_id,
                    'seq_item': i.seq_item,
                    'cd_servico': i.cd_servico,
                    'file_name': i.file_name,
                    'valor_servico': i.valor_servico,
                    'valor_taxa': i.valor_taxa,
                    'valor_total': i.valor_total_item,
                    'regras': json.loads(i.regras_aplicadas)
                }
                for i in itens
            ],
            
            'otimizacoes': [
                {
                    'regra_id': o.regra_id,
                    'descricao': o.descricao,
                    'guia_id': o.guia_id
                }
                for o in otims
            ]
        }
        
        return relatorio
        
    finally:
        session.close()


def formatar_relatorio_texto(relatorio):
    """
    Formata relatório como texto legível
    
    Args:
        relatorio: Dict retornado por gerar_relatorio_individual
        
    Returns:
        str: Relatório formatado em texto
    """
    resumo = relatorio['resumo']
    
    texto = f"""
{'='*70}
  RELATÓRIO DE GLOSAS EVITADAS - EXECUÇÃO #{relatorio['execution_id']}
{'='*70}

Data: {relatorio['data_geracao']}

{'─'*70}
RESUMO GERAL
{'─'*70}

Guias Salvas (Glosa Total): {resumo['total_guias_salvas']}
  Valor Protegido: R$ {resumo['valor_guias']:,.2f}

Itens Corrigidos (Glosa Parcial): {resumo['total_itens_corrigidos']}
  Valor Protegido: R$ {resumo['valor_itens']:,.2f}

TOTAL VALOR PROTEGIDO: R$ {resumo['total_protegido']:,.2f}

Otimizações Realizadas: {resumo['total_otimizacoes']}

"""

    # Guias salvas
    if relatorio['guias_salvas']:
        texto += f"\n{'─'*70}\n"
        texto += "GUIAS SALVAS (Glosa Total da Guia)\n"
        texto += f"{'─'*70}\n\n"
        
        for g in relatorio['guias_salvas']:
            texto += f"Guia: {g['guia_id']} | Arquivo: {g['file_name']}\n"
            texto += f"  Valor Total: R$ {g['valor_total']:,.2f}\n"
            texto += f"  Procedimentos: {g['qtd_itens']}\n"
            texto += f"  Regras: {', '.join(g['regras'])}\n\n"
    
    # Itens corrigidos
    if relatorio['itens_corrigidos']:
        texto += f"\n{'─'*70}\n"
        texto += "ITENS CORRIGIDOS (Glosa de Item Individual)\n"
        texto += f"{'─'*70}\n\n"
        
        # Agrupar por guia
        por_guia = {}
        for i in relatorio['itens_corrigidos']:
            guia = i['guia_id']
            if guia not in por_guia:
                por_guia[guia] = []
            por_guia[guia].append(i)
        
        for guia_id, itens in por_guia.items():
            texto += f"Guia: {guia_id}\n"
            for i in itens:
                texto += f"  Item {i['seq_item']}: {i['cd_servico']} - R$ {i['valor_total']:,.2f}\n"
                texto += f"    (R$ {i['valor_servico']:,.2f} + R$ {i['valor_taxa']:,.2f})\n"
                texto += f"    Regras: {', '.join(i['regras'])}\n"
            texto += "\n"
    
    # Otimizações
    if relatorio['otimizacoes']:
        texto += f"\n{'─'*70}\n"
        texto += "OTIMIZAÇÕES (Não Contabilizadas)\n"
        texto += f"{'─'*70}\n\n"
        texto += f"  Total: {len(relatorio['otimizacoes'])} melhorias aplicadas\n\n"
    
    texto += f"{'='*70}\n"
    
    return texto


def exportar_para_arquivo(relatorio, nome_arquivo):
    """
    Exporta relatório para arquivo de texto
    
    Args:
        relatorio: Dict do relatório
        nome_arquivo: Nome do arquivo (sem extensão)
    """
    texto = formatar_relatorio_texto(relatorio)
    
    with open(f"{nome_arquivo}.txt", 'w', encoding='utf-8') as f:
        f.write(texto)
    
    print(f"✅ Relatório salvo: {nome_arquivo}.txt")


def exportar_para_json(relatorio, nome_arquivo):
    """
    Exporta relatório como JSON
    
    Args:
        relatorio: Dict do relatório
        nome_arquivo: Nome do arquivo (sem extensão)
    """
    with open(f"{nome_arquivo}.json", 'w', encoding='utf-8') as f:
        json.dump(relatorio, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Relatório JSON salvo: {nome_arquivo}.json")
