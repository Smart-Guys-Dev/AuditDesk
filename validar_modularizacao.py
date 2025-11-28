#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de teste simplificado - verifica se os JSONs foram criados corretamente
"""
import json
import os

pasta_regras = 'src/config/regras'
config_file = 'src/config/rules_config.json'

print("🧪 Validando regras modularizadas...\n")

# 1. Verifica se a pasta existe
if not os.path.exists(pasta_regras):
    print(f"❌ Pasta {pasta_regras} não encontrada!")
    exit(1)

print(f"✓ Pasta {pasta_regras} encontrada")

# 2. Lista arquivos JSON
arquivos = [f for f in os.listdir(pasta_regras) if f.endswith('.json')]
print(f"✓ {len(arquivos)} arquivo(s) JSON encontrado(s)\n")

# 3. Valida cada arquivo
total_regras = 0
print("📊 Resumo por arquivo:")
print("-" * 70)

for arquivo in sorted(arquivos):
    caminho = os.path.join(pasta_regras, arquivo)
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            regras = json.load(f)
        
        regras_ativas = sum(1 for r in regras if r.get('ativo', False))
        total_regras += len(regras)
        
        print(f"  {arquivo:35} {len(regras):3} total | {regras_ativas:3} ativas")
    except Exception as e:
        print(f"  ❌ {arquivo}: ERRO - {e}")

print("-" * 70)
print(f"\n✅ Total: {total_regras} regras distribuídas em {len(arquivos)} arquivos!")

# 4. Valida rules_config.json
print(f"\n🔧 Validando {config_file}...")
try:
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    grupos = config.get('grupos_para_carregar', [])
    grupos_ativos = sum(1 for g in grupos if g.get('ativo', False))
    
    print(f"✓ {len(grupos)} grupo(s) configurado(s)")
    print(f"✓ {grupos_ativos} grupo(s) ativo(s)")
    
    print("\n✅ Configuração válida!")
except Exception as e:
    print(f"❌ Erro ao validar configuração: {e}")
    exit(1)

print("\n🎉 Sistema modularizado com sucesso!")
print(f"\n💡 Agora você pode:")
print(f"   - Editar regras específicas em src/config/regras/")
print(f"   - Ativar/desativar grupos em rules_config.json")
print(f"   - Adicionar novos arquivos de regras facilmente")
