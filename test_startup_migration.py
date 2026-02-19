import sys
import logging
from src.database import db_manager
from src.database import rule_migrator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("startup_test")

def test_startup_sequence():
    print("--- TESTE DE INICIALIZAÇÃO E MIGRAÇÃO ---")
    
    # 3. Inicializar Banco de Dados
    print("3. Inicializando DB...")
    db_manager.init_db()
    
    # 4. Migração e Sincronização Automática de Regras
    print("4. Executando Migração de Regras...")
    try:
        stats = rule_migrator.run_migration()
        print(f"Migração concluída com sucesso!")
        print(f"Stats: {stats}")
    except Exception as e:
        print(f"ERRO CRÍTICO na migração: {e}")

if __name__ == "__main__":
    test_startup_sequence()
