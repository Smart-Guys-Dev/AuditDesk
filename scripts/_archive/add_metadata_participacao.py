#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para adicionar metadata nas regras de tp_Participacao

Adiciona:
  categoria: GLOSA_ITEM
  impacto: MEDIO
  razao: Participação incorreta causa glosa do item
  contabilizar: true
"""
import json

def adicionar_metadata_participacao():
    """Adiciona metadata em TODAS regras de participação"""
    
    arquivo = 'src/config/regras_tp_participacao.json'
    
    print(f"📝 Lendo {arquivo}...")
    
    # Ler
    with open(arquivo, 'r', encoding='utf-8') as f:
        regras = json.load(f)
    
    print(f"   Total de regras: {len(regras)}")
    
    # Contadores
    adicionadas = 0
    ja_tinham = 0
    
    # Processar cada regra
    for regra in regras:
        rule_id = regra.get('id', 'UNKNOWN')
        
        # Já tem metadata?
        if 'metadata_glosa' in regra:
            ja_tinham += 1
            # Verificar se está correto
            metadata = regra['metadata_glosa']
            if metadata.get('categoria') != 'GLOSA_ITEM':
                print(f"   ⚠️  {rule_id}: Categoria diferente ({metadata.get('categoria')}), corrigindo...")
                metadata['categoria'] = 'GLOSA_ITEM'
                metadata['contabilizar'] = True
        else:
            # Adicionar metadata
            regra['metadata_glosa'] = {
                'categoria': 'GLOSA_ITEM',
                'impacto': 'MEDIO',
                'razao': 'Participação incorreta causa glosa do item pela operadora',
                'contabilizar': True
            }
            adicionadas += 1
            
            if adicionadas % 50 == 0:
                print(f"   ✅ {adicionadas} regras processadas...")
    
    # Salvar
    print(f"\n💾 Salvando alterações...")
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(regras, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Concluído!")
    print(f"   Metadata adicionada: {adicionadas}")
    print(f"   Já tinham metadata: {ja_tinham}")
    print(f"   Total: {adicionadas + ja_tinham}")

if __name__ == '__main__':
    adicionar_metadata_participacao()
