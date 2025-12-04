#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de teste para gerar relatório de glosas

Testa o módulo reporter com uma execução de exemplo
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from relatorio_glosas import reporter

def teste_relatorio():
    """Gera relatório da última execução"""
    
    # Buscar última execução
    from database import db_manager
    
    session = db_manager.get_session()
    
    # Pegar ID da última execução
    from database.db_manager import ExecutionLog
    ultima = session.query(ExecutionLog).order_by(ExecutionLog.id.desc()).first()
    
    if not ultima:
        print("❌ Nenhuma execução encontrada no banco")
        return
    
    execution_id = ultima.id
    print(f"📊 Gerando relatório para execução #{execution_id}...")
    
    # Gerar relatório
    relatorio = reporter.gerar_relatorio_individual(execution_id)
    
    # Exibir resumo
    print(f"\n{'='*70}")
    print(f"  RESUMO - Execução #{execution_id}")
    print(f"{'='*70}\n")
    
    resumo = relatorio['resumo']
    print(f"Guias Salvas: {resumo['total_guias_salvas']} (R$ {resumo['valor_guias']:,.2f})")
    print(f"Itens Corrigidos: {resumo['total_itens_corrigidos']} (R$ {resumo['valor_itens']:,.2f})")
    print(f"\n💰 TOTAL PROTEGIDO: R$ {resumo['total_protegido']:,.2f}")
    print(f"\n✅ Otimizações: {resumo['total_otimizacoes']}")
    
    # Exportar
    nome_arquivo = f"relatorio_exec_{execution_id}"
    reporter.exportar_para_arquivo(relatorio, nome_arquivo)
    reporter.exportar_para_json(relatorio, nome_arquivo)
    
    print(f"\n✅ Relatórios gerados com sucesso!")

if __name__ == '__main__':
    teste_relatorio()
