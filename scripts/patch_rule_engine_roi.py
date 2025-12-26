#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para adicionar tracking de ROI Realizado no rule_engine.py
"""

# Ler arquivo
with open('src/rule_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Adicionar import do db_manager no topo (após outros imports)
old_imports = '''from .xml_reader import XMLReader, NAMESPACES
from .file_handler import FileHandler'''

new_imports = '''from .xml_reader import XMLReader, NAMESPACES
from .file_handler import FileHandler
from .database import db_manager'''

content = content.replace(old_imports, new_imports)

# 2. Modificar assinatura do apply_rules_to_xml para aceitar execution_id e file_name
old_signature = '''    def apply_rules_to_xml(self, xml_tree):
        """
        Aplica todo o conjunto de regras carregadas a uma árvore XML.

        Args:
            xml_tree (lxml.etree._ElementTree): A árvore XML a ser modificada.

        Returns:
            bool: True se alguma alteração foi feita, False caso contrário.
        """'''

new_signature = '''    def apply_rules_to_xml(self, xml_tree, execution_id=-1, file_name=""):
        """
        Aplica todo o conjunto de regras carregadas a uma árvore XML.

        Args:
            xml_tree (lxml.etree._ElementTree): A árvore XML a ser modificada.
            execution_id (int): ID da execução para tracking de ROI
            file_name (str): Nome do arquivo sendo processado

        Returns:
            bool: True se alguma alteração foi feita, False caso contrário.
        """'''

content = content.replace(old_signature, new_signature)

# 3. Adicionar log_roi_metric após regra aplicada (linha 280)
old_log = '''                    if self._evaluate_condition(element, conditions):
                        if self._apply_action(element, rule.get("acao", {})):
                            logger.info(f"Regra '{rule.get('id')}' aplicada com sucesso.")
                            alterations_made = True'''

new_log = '''                    if self._evaluate_condition(element, conditions):
                        if self._apply_action(element, rule.get("acao", {})):
                            logger.info(f"Regra '{rule.get('id')}' aplicada com sucesso.")
                            alterations_made = True
                            
                            # Tracking de ROI Realizado
                            if execution_id != -1:
                                try:
                                    # Obter metadados da regra
                                    metadados = rule.get("metadados_glosa", {})
                                    categoria = metadados.get("categoria_glosa", "VALIDACAO")
                                    
                                    # Calcular impacto financeiro
                                    if categoria == "GLOSA_GUIA":
                                        # Valor médio de uma guia: R$ 5000
                                        financial_impact = 5000.0
                                    elif categoria == "GLOSA_ITEM":
                                        # Valor médio de um item/procedimento: R$ 300
                                        financial_impact = 300.0
                                    else:
                                        # Validação: impacto indireto (evita retrabalho)
                                        financial_impact = 100.0
                                    
                                    # Salvar no banco
                                    db_manager.log_roi_metric(
                                        execution_id=execution_id,
                                        file_name=file_name,
                                        rule_id=rule.get('id', 'UNKNOWN'),
                                        rule_description=rule.get('descricao', ''),
                                        correction_type=categoria,
                                        financial_impact=financial_impact
                                    )
                                except Exception as roi_error:
                                    logger.warning(f"Erro ao logar ROI: {roi_error}")'''

content = content.replace(old_log, new_log)

# Salvar
with open('src/rule_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ rule_engine.py atualizado com tracking de ROI!")
print("  - Adicionado import db_manager")
print("  - Modificada assinatura apply_rules_to_xml()")
print("  - Adicionado log_roi_metric() após cada regra aplicada")
print("  - Cálculo de financial_impact baseado em categoria de glosa")
