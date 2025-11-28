#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Gerador de Relatório de Classificação de Regras
"""
import json
import os
from collections import defaultdict

pasta = 'src/config/regras'

# Estrutura para armazenar dados
relatorio = {
    'VALIDACAO': [],
    'GLOSA_GUIA': [],
    'GLOSA_ITEM': [],
    'SEM_METADATA': []
}

total_regras = 0

print("="*80)
print("RELATÓRIO DE CLASSIFICAÇÃO DE GLOSAS - Audit+ v2.0")
print("="*80)
print()

for arquivo in sorted(os.listdir(pasta)):
    if not arquivo.endswith('.json'):
        continue
    
    caminho = os.path.join(pasta, arquivo)
    
    with open(caminho, 'r', encoding='utf-8') as f:
        regras = json.load(f)
    
    print(f"📁 {arquivo}")
    print("-" * 80)
    
    for regra in regras:
        total_regras += 1
        regra_id = regra.get('id', 'SEM_ID')
        descricao = regra.get('descricao', '')
        metadata = regra.get('metadata_glosa', {})
        
        if metadata:
            categoria = metadata.get('categoria', 'INDEFINIDO')
            impacto = metadata.get('impacto', 'N/A')
            razao = metadata.get('razao', 'N/A')
            
            relatorio[categoria].append({
                'arquivo': arquivo,
                'id': regra_id,
                'descricao': descricao,
                'impacto': impacto,
                'razao': razao
            })
            
            # Indicador visual
            simbolo = "🔒" if categoria == "VALIDACAO" else ("🚫" if categoria == "GLOSA_GUIA" else "⚠️")
            
            print(f"  {simbolo} {regra_id}")
            print(f"     Categoria: {categoria} | Impacto: {impacto}")
            print(f"     Razão: {razao[:70]}...")
        else:
            relatorio['SEM_METADATA'].append({
                'arquivo': arquivo,
                'id': regra_id,
                'descricao': descricao
            })
            print(f"  ❌ {regra_id} - SEM METADADOS!")
        
        print()
    
print()
print("="*80)
print("RESUMO GERAL")
print("="*80)
print()

for categoria in ['VALIDACAO', 'GLOSA_GUIA', 'GLOSA_ITEM', 'SEM_METADATA']:
    count = len(relatorio[categoria])
    if count > 0:
        porcentagem = (count / total_regras) * 100
        print(f"{categoria:20} {count:3} regra(s) ({porcentagem:5.1f}%)")

print()
print(f"{'TOTAL':20} {total_regras:3} regra(s)")
print()

# Análise de consistência
print("="*80)
print("ANÁLISE DE CONSISTÊNCIA")
print("="*80)
print()

# Verifica se todas têm metadados
if relatorio['SEM_METADATA']:
    print("⚠️  ATENÇÃO: Regras sem metadados encontradas!")
    for regra in relatorio['SEM_METADATA']:
        print(f"   - {regra['id']} ({regra['arquivo']})")
else:
    print("✅ Todas as regras possuem metadados")

print()

# Verifica distribuição lógica
validacao_count = len(relatorio['VALIDACAO'])
glosa_guia_count = len(relatorio['GLOSA_GUIA'])
glosa_item_count = len(relatorio['GLOSA_ITEM'])

print("📊 Distribuição:")
print(f"   - Regras de VALIDACAO: {validacao_count} (esperado: CNES, CPF, Reordenação)")
print(f"   - Regras de GLOSA_GUIA: {glosa_guia_count} (esperado: Auditoria, Internação)")
print(f"   - Regras de GLOSA_ITEM: {glosa_item_count} (esperado: Equipe, Conselho, Procedimentos)")

print()
print("="*80)

# Salvar relatório em arquivo
with open('relatorio_classificacao_glosas.txt', 'w', encoding='utf-8') as f:
    f.write("RELATÓRIO DE CLASSIFICAÇÃO DE GLOSAS - Audit+ v2.0\n")
    f.write("="*80 + "\n\n")
    
    for categoria in ['VALIDACAO', 'GLOSA_GUIA', 'GLOSA_ITEM']:
        if relatorio[categoria]:
            f.write(f"\n{categoria}\n")
            f.write("-"*80 + "\n")
            for regra in relatorio[categoria]:
                f.write(f"ID: {regra['id']}\n")
                f.write(f"Arquivo: {regra['arquivo']}\n")
                f.write(f"Impacto: {regra['impacto']}\n")
                f.write(f"Razão: {regra['razao']}\n")
                f.write(f"Descrição: {regra['descricao']}\n")
                f.write("\n")

print("\n✅ Relatório detalhado salvo em: relatorio_classificacao_glosas.txt")
