#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para atualizar workflow_controller.py para passar execution_id ao rule_engine
"""

# Ler arquivo
with open('src/workflow_controller.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Substituir chamada ao apply_rules_to_xml para incluir execution_id e file_name
old_call = '''                if engine.apply_rules_to_xml(xml_tree):
                    engine.file_handler.save_xml_tree(xml_tree, xml_file)
                    log(f"INFO: Arquivo modificado e salvo.")
                    modificados += 1'''

new_call = '''                if engine.apply_rules_to_xml(xml_tree, self.current_execution_id, nome_arquivo):
                    engine.file_handler.save_xml_tree(xml_tree, xml_file)
                    log(f"INFO: Arquivo modificado e salvo.")
                    modificados += 1'''

content = content.replace(old_call, new_call)

# Salvar
with open('src/workflow_controller.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ workflow_controller.py atualizado!")
print("  - Passando execution_id e file_name para rule_engine")
print("  - ROI será registrado automaticamente durante validação")
