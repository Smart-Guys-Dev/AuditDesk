#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para adicionar condição de exclusão de guiaHonorarios 
na regra SADT/INTERNAÇÃO
"""
import json

# Carrega o JSON
with open('src/config/regras_grupo_1200.json', 'r', encoding='utf-8') as f:
    regras = json.load(f)

# Encontra a regra SADT/INTERNAÇÃO
for regra in regras:
    if regra.get('id') == 'REGRA_ORDEM_EQUIPE_PARA_SADT_E_INTERNACAO':
        print(f"✓ Regra encontrada: {regra['id']}")
        
        # Verifica se já tem a condição
        sub_condicoes = regra['condicoes']['condicao_multipla']['sub_condicoes']
        
        ja_tem = False
        for cond in sub_condicoes:
            if 'guiaHonorarios' in str(cond):
                ja_tem = True
                break
        
        if ja_tem:
            print("⚠ Condição já existe! Nada a fazer.")
        else:
            # Adiciona a nova condição
            nova_condicao = {
                "condicao_tag_valor": {
                    "xpath": "ancestor::ptu:guiaHonorarios",
                    "tipo_comparacao": "nao_existe"
                }
            }
            sub_condicoes.append(nova_condicao)
            print("✓ Nova condição adicionada!")
        
        break

# Salva o JSON
with open('src/config/regras_grupo_1200.json', 'w', encoding='utf-8') as f:
    json.dump(regras, f, ensure_ascii=False, indent=2)

print("\n✅ Arquivo salvo com sucesso!")
print("Agora a regra SADT/INTERNAÇÃO NÃO será aplicada em guias de Honorários.")
