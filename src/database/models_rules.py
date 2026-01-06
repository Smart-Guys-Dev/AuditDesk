"""
Glox - Modelos de Regras (SQLite)

Nomenclatura Padrão:
- Tabela: audit_rules (regras principais)
- Tabela: audit_rule_history (histórico de versões)
- Tabela: audit_rule_lists (listas de códigos)

Categorias de Regras (RuleCategory):
- GLOSA_GUIA: Correções que evitam glosa da guia inteira
- GLOSA_ITEM: Correções que evitam glosa de item/procedimento
- VALIDACAO: Validações de formato/estrutura
- OTIMIZACAO: Otimizações sem impacto em glosa

Grupos de Regras (RuleGroup):
- EQUIPE_PROF: Equipe Profissional (CPF, CBO, Conselho)
- PARTICIPACAO: Tipo de Participação (tp_Participacao)
- INTERNACAO: Regras de Internação
- PROCEDIMENTOS: Procedimentos e Serviços
- AUDITORIA: Dados de Auditoria
- CNES: CNES de Prestadores
- LAYOUT: Ordem/estrutura de XML
- CONVERSAO: Conversão PJ para PF
- OUTROS: Outras regras
"""

from sqlalchemy import Column, String, Boolean, Integer, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .models import Base


class RuleCategory(enum.Enum):
    """Categorias de impacto das regras"""
    GLOSA_GUIA = "GLOSA_GUIA"       # Evita glosa da guia inteira
    GLOSA_ITEM = "GLOSA_ITEM"       # Evita glosa de item
    VALIDACAO = "VALIDACAO"         # Validação de formato
    OTIMIZACAO = "OTIMIZACAO"       # Otimização sem impacto


class RuleGroup(enum.Enum):
    """Grupos funcionais de regras"""
    EQUIPE_PROF = "EQUIPE_PROF"     # Equipe Profissional
    PARTICIPACAO = "PARTICIPACAO"   # Tipo de Participação
    INTERNACAO = "INTERNACAO"       # Internações
    PROCEDIMENTOS = "PROCEDIMENTOS" # Procedimentos
    AUDITORIA = "AUDITORIA"         # Dados de Auditoria
    CNES = "CNES"                   # CNES Prestadores
    LAYOUT = "LAYOUT"               # Ordem/estrutura XML
    CONVERSAO = "CONVERSAO"         # Conversão PJ->PF
    TERAPIAS = "TERAPIAS"           # Terapias Seriadas
    OUTROS = "OUTROS"               # Outras


class AuditRule(Base):
    """
    Tabela principal de regras.
    Armazena todas as regras de validação/correção de XML.
    """
    __tablename__ = 'audit_rules'
    
    # Identificação
    id = Column(String(100), primary_key=True)  # Ex: REGRA_CPF_PRESTADOR_9134
    codigo = Column(String(50))                  # Código curto opcional
    
    # Classificação
    categoria = Column(String(20), nullable=False)  # RuleCategory
    grupo = Column(String(20), nullable=False)      # RuleGroup
    
    # Descrição
    nome = Column(String(200), nullable=False)
    descricao = Column(Text)
    
    # Status
    ativo = Column(Boolean, default=True)
    prioridade = Column(Integer, default=100)  # Menor = maior prioridade
    
    # Lógica da Regra (JSON)
    condicoes = Column(Text, nullable=False)   # JSON com condições
    acao = Column(Text, nullable=False)        # JSON com ação
    log_sucesso = Column(String(500))
    
    # Metadados de Glosa
    impacto_financeiro = Column(String(10), default="MEDIO")  # BAIXO, MEDIO, ALTO
    contabilizar_roi = Column(Boolean, default=True)
    
    # Versionamento
    versao = Column(Integer, default=1)
    
    # Auditoria
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    criado_por = Column(String(100))
    atualizado_por = Column(String(100))
    
    # Relacionamentos
    historico = relationship("AuditRuleHistory", back_populates="regra", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<AuditRule(id='{self.id}', ativo={self.ativo})>"
    
    def to_dict(self):
        """Converte para dicionário compatível com rule_engine"""
        import json
        return {
            "id": self.id,
            "descricao": self.descricao,
            "ativo": self.ativo,
            "condicoes": json.loads(self.condicoes) if self.condicoes else {},
            "acao": json.loads(self.acao) if self.acao else {},
            "log_sucesso": self.log_sucesso,
            "metadata_glosa": {
                "categoria": self.categoria,
                "impacto": self.impacto_financeiro,
                "contabilizar": self.contabilizar_roi
            }
        }


class AuditRuleHistory(Base):
    """
    Histórico de alterações de regras.
    Mantém versões anteriores para auditoria e rollback.
    """
    __tablename__ = 'audit_rule_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    rule_id = Column(String(100), ForeignKey('audit_rules.id'), nullable=False)
    versao = Column(Integer, nullable=False)
    
    # Snapshot da regra antes da alteração
    dados_anteriores = Column(Text, nullable=False)  # JSON completo
    
    # Auditoria
    tipo_alteracao = Column(String(20))  # CREATE, UPDATE, DELETE, TOGGLE
    alterado_em = Column(DateTime, default=datetime.utcnow)
    alterado_por = Column(String(100))
    motivo = Column(String(500))
    
    # Relacionamento
    regra = relationship("AuditRule", back_populates="historico")
    
    def __repr__(self):
        return f"<AuditRuleHistory(rule_id='{self.rule_id}', versao={self.versao})>"


class AuditRuleList(Base):
    """
    Listas de códigos usadas pelas regras.
    Ex: codigos_equipe_obrigatoria, codigos_terapias_seriadas
    """
    __tablename__ = 'audit_rule_lists'
    
    # Identificação
    id = Column(String(50), primary_key=True)  # Ex: EQUIPE_OBRIGATORIA
    nome = Column(String(100), nullable=False)  # Nome legível
    descricao = Column(Text)
    
    # Dados
    valores = Column(Text, nullable=False)  # JSON array de códigos
    quantidade = Column(Integer, default=0)  # Cache da quantidade
    
    # Auditoria
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    atualizado_por = Column(String(100))
    
    def __repr__(self):
        return f"<AuditRuleList(id='{self.id}', qtd={self.quantidade})>"
    
    def get_valores_list(self):
        """Retorna lista de valores"""
        import json
        return json.loads(self.valores) if self.valores else []


# Mapping antigo -> novo grupo
LEGACY_GROUP_MAPPING = {
    "regras_grupo_1200.json": RuleGroup.LAYOUT,
    "regras_grupo_1201.json": RuleGroup.TERAPIAS,
    "regras_tp_participacao.json": RuleGroup.PARTICIPACAO,
    "equipe_profissional.json": RuleGroup.EQUIPE_PROF,
    "cpf_prestadores.json": RuleGroup.EQUIPE_PROF,
    "cnes.json": RuleGroup.CNES,
    "conselho.json": RuleGroup.EQUIPE_PROF,
    "auditoria.json": RuleGroup.AUDITORIA,
    "internacao.json": RuleGroup.INTERNACAO,
    "procedimentos.json": RuleGroup.PROCEDIMENTOS,
    "pj_para_pf.json": RuleGroup.CONVERSAO,
    "outros.json": RuleGroup.OUTROS,
}
