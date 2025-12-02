#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para corrigir metadata das regras CNES:
VALIDACAO → GLOSA_GUIA

Justificativa: CNES incorreto causa glosa de TODA a guia
"""
import json
import os
from pathlib import Path

def corrigir_metadata_cnes():
    """Corrige metadata de TODAS regras CNES"""
    
    arquivo_cnes = 'src/config/regras/cnes.json'
    
    print(f"📝 Lendo {arquivo_cnes}...")
    
    # Ler arquivo
    with open(arquivo_cnes, 'r', encoding='utf-8') as f:
        regras = json.load(f)
    
    print(f"   Total de regras: {len(regras)}")
    
    # Contador
    corrigidas = 0
    ja_corretas = 0
    
    # Processar cada regra
    for regra in regras:
        rule_id = regra.get('id', 'UNKNOWN')
        
        # Verificar se tem metadata
        if 'metadata_glosa' in regra:
            metadata = regra['metadata_glosa']
            
            # Se já é GLOSA_GUIA, pular
            if metadata.get('categoria') == 'GLOSA_GUIA':
                ja_corretas += 1
                continue
            
            # Corrigir
            metadata['categoria'] = 'GLOSA_GUIA'
            metadata['impacto'] = 'ALTO'
            metadata['razao'] = 'CNES incorreto causa glosa total da guia pela operadora'
            metadata['contabilizar'] = True
            
            print(f"   ✅ {rule_id}: VALIDACAO → GLOSA_GUIA")
            corrigidas += 1
            
        else:
            # Adicionar metadata
            regra['metadata_glosa'] = {
                'categoria': 'GLOSA_GUIA',
                'impacto': 'ALTO',
                'razao': 'CNES incorreto causa glosa total da guia pela operadora',
                'contabilizar': True
            }
            print(f"   ➕ {rule_id}: Metadata adicionada")
            corrigidas += 1
    
    # Salvar
    print(f"\n💾 Salvando alterações...")
    with open(arquivo_cnes, 'w', encoding='utf-8') as f:
        json.dump(regras, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Concluído!")
    print(f"   Corrigidas: {corrigidas}")
    print(f"   Já corretas: {ja_corretas}")
    print(f"   Total: {corrigidas + ja_corretas}")

if __name__ == '__main__':
    corrigir_metadata_cnes()
