#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para integrar tracker no rule_engine.py
Adiciona chamada a tracker.processar_correcao() após cada regra aplicada
"""

# Ler arquivo
with open('src/rule_engine.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Código a inserir
code_to_insert = """                            
                            # Tracking de glosas evitadas (valores REAIS do XML)
                            if execution_id != -1 and tracker is not None:
                                try:
                                    tracker.processar_correcao(
                                        execution_id=execution_id,
                                        file_name=file_name,
                                        xml_tree=xml_tree,
                                        rule=rule,
                                        elemento_afetado=element
                                    )
                                except Exception as tracking_error:
                                    logger.warning(f"Erro ao tracking glosa: {tracking_error}")
"""

# Encontrar linha onde inserir (após "alterations_made = True")
inserted = False
new_lines = []

for i, line in enumerate(lines):
    new_lines.append(line)
    
    # Procurar pela linha específica
    if not inserted and 'alterations_made = True' in line and i > 280:
        # Inserir código após esta linha
        new_lines.append(code_to_insert)
        inserted = True
        print(f"✅ Código inserido após linha {i+1}")

if not inserted:
    print("❌ Não encontrou local para inserir!")
    exit(1)

# Salvar
with open('src/rule_engine.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✅ Integração concluída!")
