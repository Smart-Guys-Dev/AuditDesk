"""
AuditPlus v2.0 - Modelos de Faturas para Consulta

Tabelas:
- faturas: Dados principais das faturas importadas
- fatura_historico: Histórico de eventos de cada fatura
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .models import Base


class Fatura(Base):
    """
    Tabela principal de faturas importadas.
    Permite consulta de status por número de fatura.
    """
    __tablename__ = 'faturas'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nro_fatura = Column(String(30), unique=True, nullable=False, index=True)
    
    # Status da fatura
    status = Column(String(20), default='PENDENTE')  # PENDENTE, ENVIADA, CANCELADA, GLOSADA
    
    # Dados da Unimed
    unimed_codigo = Column(String(10))
    unimed_nome = Column(String(150))
    
    # Valores
    valor = Column(Float, default=0.0)
    competencia = Column(String(10))  # MM/YYYY
    
    # Responsável/Auditor
    responsavel = Column(String(100))
    
    # Datas importantes
    data_envio = Column(DateTime)
    data_importacao = Column(DateTime, default=datetime.utcnow)
    
    # Tracking do AuditPlus
    corrigida_auditplus = Column(Boolean, default=False)
    arquivo_origem = Column(String(200))
    
    # Relacionamentos
    historico = relationship("FaturaHistorico", back_populates="fatura", 
                            cascade="all, delete-orphan", order_by="desc(FaturaHistorico.data_hora)")
    
    def __repr__(self):
        return f"<Fatura(nro={self.nro_fatura}, status={self.status})>"
    
    def get_status_emoji(self):
        """Retorna emoji baseado no status"""
        emojis = {
            'PENDENTE': '⏳',
            'ENVIADA': '✅',
            'CANCELADA': '❌',
            'GLOSADA': '⚠️'
        }
        return emojis.get(self.status, '❓')
    
    def to_dict(self):
        """Converte para dicionário para exibição"""
        return {
            'nro_fatura': self.nro_fatura,
            'status': self.status,
            'status_emoji': self.get_status_emoji(),
            'unimed': f"{self.unimed_codigo} - {self.unimed_nome}" if self.unimed_codigo else "",
            'valor': self.valor or 0,
            'competencia': self.competencia or "",
            'responsavel': self.responsavel or "",
            'data_envio': self.data_envio.strftime("%d/%m/%Y %H:%M") if self.data_envio else None,
            'corrigida_auditplus': self.corrigida_auditplus
        }


class FaturaHistorico(Base):
    """
    Histórico de eventos de uma fatura.
    Registra cada mudança de status ou ação.
    """
    __tablename__ = 'fatura_historico'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    fatura_id = Column(Integer, ForeignKey('faturas.id'), nullable=False)
    
    data_hora = Column(DateTime, default=datetime.utcnow)
    acao = Column(String(100), nullable=False)  # "Importada do SGU", "Enviada para NCMB", etc.
    origem = Column(String(50))  # SGU, NCMB, AuditPlus, Manual
    detalhes = Column(Text)  # Informações adicionais
    
    # Relacionamento
    fatura = relationship("Fatura", back_populates="historico")
    
    def __repr__(self):
        return f"<FaturaHistorico(fatura_id={self.fatura_id}, acao={self.acao})>"
    
    def to_dict(self):
        return {
            'data_hora': self.data_hora.strftime("%d/%m/%Y %H:%M") if self.data_hora else "",
            'acao': self.acao,
            'origem': self.origem or ""
        }
