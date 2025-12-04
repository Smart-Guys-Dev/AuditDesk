"""
Tracker de Glosas Evitadas

Sistema central de tracking com:
- Anti-duplicação (UNIQUE constraints)
- Hierarquia GUIA > ITEM  
- Valores REAIS do XML
"""
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import GlosaGuia, GlosaItem, Otimizacao
from . import extractor

# Engine e Session
engine = create_engine('sqlite:///audit_plus.db')
Session = sessionmaker(bind=engine)


def processar_correcao(execution_id, file_name, xml_tree, rule, elemento_afetado):
    """
    Processa uma correção e decide se/como contabilizar
    
    Args:
        execution_id: ID da execução
        file_name: Nome do arquivo XML
        xml_tree: Árvore XML completa
        rule: Dict da regra aplicada
        elemento_afetado: Elemento XML que foi modificado
    """
    # Obter metadata da regra
    metadata = rule.get('metadata_glosa', {})
    categoria = metadata.get('categoria', 'OTIMIZACAO')
    contabilizar = metadata.get('contabilizar', False)
    
    # Se não contabiliza, apenas logar como otimização
    if not contabilizar or categoria == 'OTIMIZACAO':
        log_otimizacao(execution_id, file_name, rule['id'], elemento_afetado)
        return
    
    # GLOSA_GUIA ou GLOSA_ITEM?
    if categoria == 'GLOSA_GUIA':
        processar_glosa_guia(execution_id, file_name, rule, elemento_afetado)
    elif categoria == 'GLOSA_ITEM':
        processar_glosa_item(execution_id, file_name, rule, elemento_afetado)


def processar_glosa_guia(execution_id, file_name, rule, elemento):
    """
    Processa uma glosa de GUIA (guia inteira salva)
    
    Extrai valor TOTAL da guia e registra.
    Se guia já foi registrada, apenas adiciona regra à lista.
    """
    session = Session()
    
    try:
        # Extrair identificador da guia
        guia_id = extractor.extrair_nr_guia_prestador(elemento)
        if not guia_id:
            return
        
        # Verificar se guia JÁ foi registrada
        existing = session.query(GlosaGuia).filter_by(
            execution_id=execution_id,
            guia_id=guia_id
        ).first()
        
        if existing:
            # Adicionar regra à lista (NÃO duplicar)
            regras = json.loads(existing.regras_aplicadas)
            if rule['id'] not in regras:
                regras.append(rule['id'])
                existing.regras_aplicadas = json.dumps(regras)
                session.commit()
        else:
            # Primeira vez: extrair valor total
            valor_total = extractor.extrair_valor_total_guia(elemento)
            qtd_itens = extractor.contar_procedimentos_guia(elemento)
            
            nova_guia = GlosaGuia(
                execution_id=execution_id,
                file_name=file_name,
                guia_id=guia_id,
                valor_total_guia=valor_total,
                qtd_itens=qtd_itens,
                categoria='GLOSA_GUIA',
                regras_aplicadas=json.dumps([rule['id']])
            )
            session.add(nova_guia)
            session.commit()
            
    except Exception as e:
        print(f"Erro ao processar glosa de guia: {e}")
        session.rollback()
    finally:
        session.close()


def processar_glosa_item(execution_id, file_name, rule, elemento):
    """
    Processa uma glosa de ITEM (item individual corrigido)
    
    IMPORTANTE: Verifica se guia já tem GLOSA_GUIA.
    Se sim, NÃO conta o item (hierarquia).
    """
    session = Session()
    
    try:
        # Extrair identificador da guia
        guia_id = extractor.extrair_nr_guia_prestador(elemento)
        if not guia_id:
            return
        
        # HIERARQUIA: Verificar se guia JÁ tem GLOSA_GUIA
        tem_glosa_guia = session.query(GlosaGuia).filter_by(
            execution_id=execution_id,
            guia_id=guia_id
        ).first()
        
        if tem_glosa_guia:
            # Guia INTEIRA foi salva → NÃO contar item
            log_otimizacao(
                execution_id, file_name, rule['id'], elemento,
                f"Item não contado - guia {guia_id} já salva"
            )
            return
        
        # Extrair seq_item
        # Tentar encontrar elemento procedimentosExecutados
        proc_element = elemento
        if elemento.tag.split('}')[-1] != 'procedimentosExecutados':
            # Elemento não é procedimento, tentar encontrar ancestor
            from lxml import etree
            NAMESPACES = {'ptu': 'http://www.ans.gov.br/padraoTissProducaoTerceirosPrestadorUnico'}
            proc_ancestor = elemento.xpath('ancestor::ptu:procedimentosExecutados', namespaces=NAMESPACES)
            if proc_ancestor:
                proc_element = proc_ancestor[0]
            else:
                # Não conseguiu identificar procedimento
                return
        
        seq_item = extractor.extrair_seq_item(proc_element)
        if seq_item == 0:
            return
        
        # Verificar se item JÁ foi registrado
        existing = session.query(GlosaItem).filter_by(
            execution_id=execution_id,
            guia_id=guia_id,
            seq_item=seq_item
        ).first()
        
        if existing:
            # Adicionar regra à lista (NÃO duplicar valor!)
            regras = json.loads(existing.regras_aplicadas)
            if rule['id'] not in regras:
                regras.append(rule['id'])
                existing.regras_aplicadas = json.dumps(regras)
                session.commit()
        else:
            # Primeira vez: extrair valores DO XML
            cd_servico = extractor.extrair_cd_servico(proc_element)
            valor_total = extractor.extrair_valor_procedimento(proc_element)
            
            # Separar valor serviço e taxa
            valores_element = proc_element.find('.//ptu:valores', namespaces={'ptu': 'http://www.ans.gov.br/padraoTissProducaoTerceirosPrestadorUnico'})
            vl_serv = 0.0
            tx_adm = 0.0
            
            if valores_element is not None:
                vl_tag = valores_element.find('.//ptu:vl_ServCobrado', namespaces={'ptu': 'http://www.ans.gov.br/padraoTissProducaoTerceirosPrestadorUnico'})
                tx_tag = valores_element.find('.//ptu:tx_AdmServico', namespaces={'ptu': 'http://www.ans.gov.br/padraoTissProducaoTerceirosPrestadorUnico'})
                
                if vl_tag is not None and vl_tag.text:
                    vl_serv = float(vl_tag.text)
                if tx_tag is not None and tx_tag.text:
                    tx_adm = float(tx_tag.text)
            
            novo_item = GlosaItem(
                execution_id=execution_id,
                file_name=file_name,
                guia_id=guia_id,
                seq_item=seq_item,
                cd_servico=cd_servico,
                valor_servico=vl_serv,
                valor_taxa=tx_adm,
                valor_total_item=valor_total,
                categoria='GLOSA_ITEM',
                regras_aplicadas=json.dumps([rule['id']])
            )
            session.add(novo_item)
            session.commit()
            
    except Exception as e:
        print(f"Erro ao processar glosa de item: {e}")
        session.rollback()
    finally:
        session.close()


def log_otimizacao(execution_id, file_name, regra_id, elemento, descricao=""):
    """
    Registra uma otimização (NÃO contabiliza)
    """
    session = Session()
    
    try:
        guia_id = extractor.extrair_nr_guia_prestador(elemento) if elemento is not None else None
        
        otim = Otimizacao(
            execution_id=execution_id,
            file_name=file_name,
            guia_id=guia_id,
            regra_id=regra_id,
            descricao=descricao
        )
        session.add(otim)
        session.commit()
    except Exception as e:
        print(f"Erro ao logar otimização: {e}")
        session.rollback()
    finally:
        session.close()
