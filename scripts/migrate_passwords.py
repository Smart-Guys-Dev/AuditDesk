# migrate_passwords.py
"""
Script de Migração de Senhas SHA-256 para bcrypt
Converte senhas antigas para o novo formato seguro.
"""

from src.database import db_manager
from src.database.models import User
from src.infrastructure.security import PasswordManager
import hashlib

def migrate_admin_password():
    """Migra senha do admin de SHA-256 para bcrypt"""
    
    session = db_manager.get_session()
    
    try:
        # Buscar admin
        admin = session.query(User).filter_by(username='admin').first()
        
        if not admin:
            print("❌ Usuário admin não encontrado")
            return
        
        # Verificar se já está em bcrypt
        if isinstance(admin.password_hash, bytes) or admin.password_hash.startswith('$2b$'):
            print("✅ Senha já está em bcrypt!")
            return
        
        print(f"Hash atual: {admin.password_hash[:50]}...")
        
        # Senha padrão antiga era "admin123"
        # Vamos resetar para uma senha conhecida em bcrypt
        default_password = "admin123"  # Você pode mudar depois
        
        print(f"\n🔄 Migrando senha do admin...")
        print(f"   Senha temporária: {default_password}")
        print(f"   (MUDE IMEDIATAMENTE após fazer login!)\n")
        
        # Criar novo hash bcrypt
        new_hash = PasswordManager.hash_password(default_password)
        
        # Atualizar no banco
        admin.password_hash = new_hash
        session.commit()
        
        print("✅ Migração concluída!")
        print(f"\n   Login: admin")
        print(f"   Senha: {default_password}")
        print(f"\n⚠️  IMPORTANTE: Troque a senha após fazer login!\n")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    migrate_admin_password()
