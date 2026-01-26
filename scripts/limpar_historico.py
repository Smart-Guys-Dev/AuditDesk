"""
Limpa o histórico de arquivos processados para permitir reprocessamento.
"""
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from src.database import db_manager
from src.models.file_log import FileLog

print("=" * 50)
print("LIMPANDO HISTÓRICO DE ARQUIVOS PROCESSADOS")
print("=" * 50)

session = db_manager.get_session()
try:
    count = session.query(FileLog).count()
    print(f"\nRegistros encontrados: {count}")
    
    if count > 0:
        session.query(FileLog).delete()
        session.commit()
        print(f"✅ {count} registro(s) removido(s) com sucesso!")
        print("\nAgora você pode reprocessar os arquivos.")
    else:
        print("Nenhum registro para limpar.")
except Exception as e:
    session.rollback()
    print(f"❌ Erro: {e}")
finally:
    session.close()

print("=" * 50)
