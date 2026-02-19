import sqlite3
import json
import os

DB_FILE = "audit_plus.db"
RULE_ID = "REGRA_CORRIGIR_CNPJ_CNES_UNIMED_CGR_03315918000118"

def verify_rule():
    if not os.path.exists(DB_FILE):
        print(f"ERRO: Banco de dados {DB_FILE} não encontrado.")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    print(f"--- VERIFICANDO REGRA NO BANCO DE DADOS ---")
    print(f"ID: {RULE_ID}")
    
    cursor.execute("SELECT id, nome, ativo, condicoes, acao FROM audit_rules WHERE id = ?", (RULE_ID,))
    row = cursor.fetchone()
    
    if row:
        print("STATUS: ENCONTRADA")
        print(f"Nome: {row[1]}")
        print(f"Ativo: {bool(row[2])}")
        print(f"Condições (DB): {row[3]}")
        print(f"Ação (DB): {row[4]}")
    else:
        print("STATUS: NÃO ENCONTRADA")
        print("A regra NÃO existe no banco de dados. O sistema pode estar usando uma versão desatualizada das regras.")

    conn.close()

if __name__ == "__main__":
    verify_rule()
