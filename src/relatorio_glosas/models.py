"""
Models para tracking de glosas evitadas

Três categorias:
1. GlosaGuia: Guia INTEIRA salva (valor total)
2. GlosaItem: Item individual corrigido (valor do item)
3. Otimizacao: Melhorias sem impacto financeiro
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class GlosaGuia(Base):
    """
    Tracking de guias INTEIRAS salvas
    
    Quando uma regra GLOSA_GUIA é aplicada (ex: CNES, Médico Auditor),
    a guia INTEIRA seria rejeitada. Salvamos o valor total.
    """
    __tablename__ = 'glosas_evitadas_guias'
    
    id = Column(Integer, primary_key=True)
    execution_id = Column(Integer, nullable=False, index=True)
    file_name = Column(String(500), nullable=False)
    guia_id = Column(String(100), nullable=False)  # nr_GuiaPrestador
    
    # Valor REAL do XML
    valor_total_guia = Column(Float, nullable=False)
    qtd_itens = Column(Integer, default=0)
    
    # Categoria
    categoria = Column(String(50), default='GLOSA_GUIA')
    
    # Regras aplicadas (JSON array)
    regras_aplicadas = Column(Text, nullable=False)  # ["REGRA_1", "REGRA_2"]
    
    # Timestamp
    timestamp = Column(DateTime, default=datetime.now)
    
    # Índice único: uma guia só pode ser salva UMA VEZ por execução
    __table_args__ = (
        UniqueConstraint('execution_id', 'guia_id', name='uq_guia_execution'),
    )


class GlosaItem(Base):
    """
    Tracking de itens individuais corrigidos
    
    Quando uma regra GLOSA_ITEM é aplicada (ex: tp_Participacao, CBO),
    apenas o item seria rejeitado. Salvamos o valor do item.
    
    IMPORTANTE: Se a guia já foi salva (GLOSA_GUIA), NÃO contamos itens!
    """
    __tablename__ = 'glosas_evitadas_items'
    
    id = Column(Integer, primary_key=True)
    execution_id = Column(Integer, nullable=False, index=True)
    file_name = Column(String(500), nullable=False)
    guia_id = Column(String(100), nullable=False)
    seq_item = Column(Integer, nullable=False)
    cd_servico = Column(String(20))
    
    # Valores REAIS do XML
    valor_servico = Column(Float, default=0.0)      # vl_ServCobrado
    valor_taxa = Column(Float, default=0.0)         # tx_AdmServico
    valor_total_item = Column(Float, nullable=False)  # soma
    
    # Categoria
    categoria = Column(String(50), default='GLOSA_ITEM')
    
    # Regras aplicadas (JSON array)
    # Múltiplas regras podem corrigir o MESMO item, mas contamos valor 1x só!
    regras_aplicadas = Column(Text, nullable=False)
    
    # Timestamp
    timestamp = Column(DateTime, default=datetime.now)
    
    # Índice único: um item só pode ser contado UMA VEZ por execução
    # Mesmo que múltiplas regras sejam aplicadas, o valor é único!
    __table_args__ = (
        UniqueConstraint('execution_id', 'guia_id', 'seq_item', name='uq_item_execution'),
    )


class Otimizacao(Base):
    """
    Tracking de otimizações (NÃO contabilizar)
    
    Registra melhorias que NÃO evitam glosa:
    - Reordenação de tags (XSD validation)
    - Remoção de blocos opcionais (quando já estavam corretos)
    - Etc.
    """
    __tablename__ = 'otimizacoes'
    
    id = Column(Integer, primary_key=True)
    execution_id = Column(Integer, nullable=False, index=True)
    file_name = Column(String(500), nullable=False)
    guia_id = Column(String(100))
    regra_id = Column(String(200), nullable=False)
    descricao = Column(Text)
    timestamp = Column(DateTime, default=datetime.now)
