#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de migração para criar tabelas de glosas
"""
import sys
import os

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sqlalchemy import create_engine
from relatorio_glosas.models import Base, GlosaGuia, GlosaItem, Otimizacao

def criar_tabelas():
    """Cria as tabelas de glosas no banco de dados"""
    
    print("🗄️  Criando tabelas de glosas...")
    
    # Conectar ao banco
    engine = create_engine('sqlite:///audit_plus.db')
    
    # Criar todas as tabelas
    Base.metadata.create_all(engine)
    
    print("✅ Tabelas criadas com sucesso!")
    print("   - glosas_evitadas_guias")
    print("   - glosas_evitadas_items")
    print("   - otimizacoes")
    
    # Verificar
    from sqlalchemy import inspect
    inspector = inspect(engine)
    
    print("\n📋 Verificando estrutura:")
    
    for table_name in ['glosas_evitadas_guias', 'glosas_evitadas_items', 'otimizacoes']:
        columns = inspector.get_columns(table_name)
        print(f"\n   {table_name}:")
        for col in columns:
            print(f"      - {col['name']}: {col['type']}")

if __name__ == '__main__':
    criar_tabelas()
