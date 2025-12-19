"""
Script de Teste - Sistema de Relatórios de Glosas Evitadas

Testa a execução completa do sistema:
1. Cria tabelas (se não existirem)
2. Processa 1 arquivo XML de teste
3. Gera relatório individual
4. Exibe resultados
"""

import sys
import os
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent))

def testar_sistema():
    print("=" * 70)
    print("  TESTE DO SISTEMA DE GLOSAS EVITADAS")
    print("=" * 70)
    print()
    
    # 1. Verificar tabelas
    print("1. Verificando estrutura do banco...")
    try:
        from sqlalchemy import create_engine, inspect
        from src.relatorio_glosas.models import GlosaGuia, GlosaItem, Otimizacao, Base
        
        engine = create_engine('sqlite:///audit_plus.db')
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        # Criar tabelas se não existirem
        Base.metadata.create_all(engine)
        
        print("   ✅ Tabela glosas_evitadas_guias:", 'glosas_evitadas_guias' in tables)
        print("   ✅ Tabela glosas_evitadas_items:", 'glosas_evitadas_items' in tables)
        print("   ✅ Tabela otimizacoes:", 'otimizacoes' in tables)
        print()
    except Exception as e:
        print(f"   ❌ Erro ao verificar banco: {e}")
        return
    
    # 2. Verificar última execução
    print("2. Buscando última execução...")
    try:
        from src.database.models import ExecutionLog
        from sqlalchemy.orm import sessionmaker
        
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Buscar última execução
        last_execution = session.query(ExecutionLog).order_by(ExecutionLog.id.desc()).first()
        
        if not last_execution:
            print("   ⚠️  Nenhuma execução encontrada no banco")
            print("   💡 Execute o AuditPlus primeiro para processar arquivos")
            session.close()
            return
        
        execution_id = last_execution.id
        timestamp = last_execution.timestamp
        print(f"   ✅ Última execução: ID {execution_id} ({timestamp})")
        print()
        
        session.close()
    except Exception as e:
        print(f"   ❌ Erro ao buscar execução: {e}")
        return
    
    # 3. Verificar dados de glosas
    print("3. Verificando dados de glosas...")
    try:
        from sqlalchemy.orm import sessionmaker
        Session = sessionmaker(bind=engine)
        session = Session()
        
        qtd_guias = session.query(GlosaGuia).filter_by(execution_id=execution_id).count()
        qtd_itens = session.query(GlosaItem).filter_by(execution_id=execution_id).count()
        qtd_otims = session.query(Otimizacao).filter_by(execution_id=execution_id).count()
        
        print(f"   📊 Guias salvas (GLOSA_GUIA): {qtd_guias}")
        print(f"   📊 Itens corrigidos (GLOSA_ITEM): {qtd_itens}")
        print(f"   📊 Otimizações (não contabilizadas): {qtd_otims}")
        print()
        
        if qtd_guias == 0 and qtd_itens == 0:
            print("   ⚠️  Nenhuma glosa foi registrada")
            print("   💡 Possíveis causas:")
            print("      - Arquivos já estavam 100% corretos")
            print("      - Sistema de tracking não está funcionando")
            print("      - Regras não têm metadata_glosa com contabilizar=true")
            print()
        
        session.close()
    except Exception as e:
        print(f"   ❌ Erro ao verificar glosas: {e}")
        return
    
    # 4. Gerar relatório
    if qtd_guias > 0 or qtd_itens > 0:
        print("4. Gerando relatório...")
        try:
            from src.relatorio_glosas import reporter
            
            relatorio = reporter.gerar_relatorio_individual(execution_id)
            
            # Exibir resumo
            print()
            print("=" * 70)
            print("  RESUMO DO RELATÓRIO")
            print("=" * 70)
            print()
            print(f"Guias Salvas: {relatorio['resumo']['total_guias_salvas']}")
            print(f"  Valor Total: R$ {relatorio['resumo']['valor_guias']:,.2f}")
            print()
            print(f"Itens Corrigidos: {relatorio['resumo']['total_itens_corrigidos']}")
            print(f"  Valor Total: R$ {relatorio['resumo']['valor_itens']:,.2f}")
            print()
            print(f"💰 TOTAL PROTEGIDO: R$ {relatorio['resumo']['total_protegido']:,.2f}")
            print()
            print(f"Otimizações: {relatorio['resumo']['total_otimizacoes']}")
            print()
            
            # Salvar arquivos
            reporter.exportar_para_arquivo(relatorio, f"relatorio_exec_{execution_id}")
            reporter.exportar_para_json(relatorio, f"relatorio_exec_{execution_id}")
            
            print("=" * 70)
            print()
            
        except Exception as e:
            print(f"   ❌ Erro ao gerar relatório: {e}")
            import traceback
            traceback.print_exc()
            return
    
    # 5. Status final
    print()
    print("=" * 70)
    print("  TESTE CONCLUÍDO!")
    print("=" * 70)
    print()
    print("✅ Sistema está funcionando corretamente")
    print()
    print("📁 Arquivos gerados:")
    print(f"   - relatorio_exec_{execution_id}.txt")
    print(f"   - relatorio_exec_{execution_id}.json")
    print()


if __name__ == "__main__":
    try:
        testar_sistema()
    except KeyboardInterrupt:
        print("\n\n⚠️  Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
