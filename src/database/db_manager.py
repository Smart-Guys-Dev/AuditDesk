import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime
from .models import Base, ExecutionLog, FileLog, User, ROIMetrics
from .models_fatura import Fatura, FaturaHistorico  # Modelos de faturas para consulta
from .models_rules import AuditRule, AuditRuleHistory, AuditRuleList  # Modelos de regras

# ✅ SEGURANÇA: Importar gerenciador seguro de senhas
from src.infrastructure.security.password_manager import PasswordManager
from src.infrastructure.security.validator import SecurityValidator
from src.infrastructure.security.audit_logger import AuditLogger  # ✅ LGPD
import logging

logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

# ======== Configuração Dual-Provider ========
DB_PROVIDER = os.getenv("DB_PROVIDER", "sqlite").lower().strip()

if DB_PROVIDER == "postgresql":
    # PostgreSQL
    PG_HOST = os.getenv("POSTGRES_HOST", "localhost")
    PG_PORT = os.getenv("POSTGRES_PORT", "5432")
    PG_DB   = os.getenv("POSTGRES_DB", "audit_plus")
    PG_USER = os.getenv("POSTGRES_USER", "postgres")
    PG_PASS = os.getenv("POSTGRES_PASSWORD", "")
    DATABASE_URL = f"postgresql+psycopg2://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{PG_DB}"
    engine = create_engine(DATABASE_URL, echo=False, pool_size=10, max_overflow=20, pool_pre_ping=True)
    logger.info(f"Banco de dados: PostgreSQL em {PG_HOST}:{PG_PORT}/{PG_DB}")
else:
    # SQLite (fallback)
    DB_FILE = os.getenv("DATABASE_PATH", "audit_plus.db")
    DATABASE_URL = f"sqlite:///{DB_FILE}"
    engine = create_engine(DATABASE_URL, echo=False)
    logger.info(f"Banco de dados: SQLite em {os.path.abspath(DB_FILE)}")

# Session Factory
SessionFactory = sessionmaker(bind=engine)
Session = scoped_session(SessionFactory)

def init_db():
    """Cria as tabelas no banco de dados se não existirem e cria usuário admin."""
    Base.metadata.create_all(engine)
    logger.info(f"Banco de dados inicializado ({DB_PROVIDER})")
    
    # ✅ SEGURANÇA: Criar usuário admin sem senha padrão
    session = get_session()
    try:
        admin = session.query(User).filter_by(username='admin').first()
        if not admin:
            # ✅ SEGURANÇA: Solicitar senha forte ao invés de hardcoded
            print("\n" + "="*60)
            print("🔐 PRIMEIRA EXECUÇÃO - Configuração de Segurança")
            print("="*60)
            print("Por favor, crie uma senha FORTE para o usuário admin.")
            print("Requisitos:")
            print("  - Mínimo 12 caracteres")
            print("  - Letras maiúsculas e minúsculas")
            print("  - Números e caracteres especiais")
            print("="*60 + "\n")
            
            # Loop até senha forte
            while True:
                admin_password = input("Digite a senha para o admin: ")
                valid, msg = SecurityValidator.validate_password_strength(admin_password)
                if valid:
                    logger.info("✅ Senha segura aceita para admin")
                    break
                else:
                    print(f"❌ {msg}")
                    print("Tente novamente.\n")
            
            # ✅ SEGURANÇA: Usar bcrypt ao invés de SHA-256
            pwd_hash = PasswordManager.hash_password(admin_password)
            
            new_admin = User(
                username='admin',
                password_hash=pwd_hash,
                full_name='Administrador do Sistema',
                role='ADMIN'
            )
            session.add(new_admin)
            session.commit()
            logger.info("✅ Usuário 'admin' criado com senha segura (bcrypt)")
            print("\n✅ Configuração concluída! Usuário admin criado com sucesso.\n")
    except Exception as e:
        logger.error(f"Erro ao criar admin: {e}")
        session.rollback()
    finally:
        session.close()

def get_session():
    """Retorna uma nova sessão do banco de dados."""
    return Session()

def log_execution_start(operation_type: str, total_files: int = 0, user_id: int = None) -> int:
    """
    Registra o início de uma execução.
    Retorna o ID da execução criada.
    """
    session = get_session()
    try:
        new_exec = ExecutionLog(
            operation_type=operation_type,
            total_files=total_files,
            status='RUNNING',
            user_id=user_id
        )
        session.add(new_exec)
        session.commit()
        return new_exec.id
    except Exception as e:
        print(f"Erro ao logar início de execução: {e}")
        session.rollback()
        return -1
    finally:
        session.close()

def log_execution_end(execution_id: int, status: str, success_count: int, error_count: int):
    """Atualiza o registro de execução com o status final."""
    if execution_id == -1: return

    session = get_session()
    try:
        exec_log = session.query(ExecutionLog).filter_by(id=execution_id).first()
        if exec_log:
            exec_log.end_time = datetime.now()
            exec_log.status = status
            exec_log.success_count = success_count
            exec_log.error_count = error_count
            session.commit()
    except Exception as e:
        print(f"Erro ao logar fim de execução: {e}")
        session.rollback()
    finally:
        session.close()

def log_file_processed(execution_id: int, file_name: str, file_path: str, status: str, message: str = None, file_hash: str = None):
    """Registra o processamento de um arquivo individual."""
    if execution_id == -1: return

    session = get_session()
    try:
        new_file_log = FileLog(
            execution_id=execution_id,
            file_name=file_name,
            file_path=file_path,
            file_hash=file_hash,
            status=status,
            message=message
        )
        session.add(new_file_log)
        session.commit()
    except Exception as e:
        print(f"Erro ao logar arquivo: {e}")
        session.rollback()
    finally:
        session.close()

# Alias para compatibilidade
def log_file_processing(execution_id: int, file_name: str, file_path: str, file_hash: str = None, status: str = 'SUCCESS', message: str = None):
    """Alias para log_file_processed com parâmetros reordenados."""
    log_file_processed(execution_id, file_name, file_path, status, message, file_hash)

def get_dashboard_stats():
    """Retorna estatísticas gerais para o dashboard."""
    session = get_session()
    stats = {
        'total_executions': 0,
        'total_files': 0,
        'total_arquivos': 0,  # Alias para guias corrigidas
        'success_count': 0,
        'error_count': 0,
        'success_rate': 0.0,
        'top_unimed_errors': None  # Maior Unimed com erros de layout
    }
    try:
        # Agregar dados de ExecutionLog
        executions = session.query(ExecutionLog).all()
        stats['total_executions'] = len(executions)
        
        for exc in executions:
            stats['total_files'] += (exc.success_count + exc.error_count)
            stats['success_count'] += exc.success_count
            stats['error_count'] += exc.error_count
            
        if stats['total_files'] > 0:
            stats['success_rate'] = (stats['success_count'] / stats['total_files']) * 100
        
        # Total de arquivos processados = guias corrigidas (success_count)
        stats['total_arquivos'] = stats['success_count']
        
        # Buscar Top Unimed com mais erros (via FileLog se disponível)
        try:
            from sqlalchemy import func
            top_error = session.query(
                FileLog.filename, 
                func.count(FileLog.id).label('error_count')
            ).filter(
                FileLog.status == 'ERRO'
            ).group_by(
                FileLog.filename
            ).order_by(
                func.count(FileLog.id).desc()
            ).first()
            
            if top_error and top_error.error_count > 0:
                # Extrair código da Unimed do nome do arquivo (padrão: N0XXXXXX)
                import re
                match = re.search(r'N0(\d+)', top_error.filename)
                if match:
                    stats['top_unimed_errors'] = f"N0{match.group(1)}"
                else:
                    stats['top_unimed_errors'] = "Ver logs"
        except Exception as e:
            logger.debug(f"Não foi possível obter top unimed: {e}")
            
    except Exception as e:
        print(f"Erro ao gerar estatísticas: {e}")
    finally:
        session.close()
    
    
    return stats


def authenticate_user(username, password):
    """
    Verifica as credenciais do usuário.
    Retorna o objeto User se válido, ou None se inválido.
    
    ✅ SEGURANÇA: Usa bcrypt e protege contra timing attacks
    """
    import time
    import random
    
    session = get_session()
    try:
        user = session.query(User).filter_by(username=username, is_active=True).first()
        
        # ✅ SEGURANÇA: Timing constante para prevenir enumeração de usuários
        # Sempre fazer verificação mesmo se usuário não existir
        if user:
            # Verificar com bcrypt
            password_valid = PasswordManager.verify_password(password, user.password_hash)
            
            # ✅ SEGURANÇA: Rehash se necessário (custo mudou)
            if password_valid and PasswordManager.needs_rehash(user.password_hash):
                logger.info(f"Atualizando hash de senha para usuário: {username}")
                new_hash = PasswordManager.hash_password(password)
                user.password_hash = new_hash
                session.commit()
            
            if password_valid:
                logger.info(f"✅ Autenticação bem-sucedida: {username}")
                return user
        else:
            # ✅ SEGURANÇA: Fazer hash fake para manter timing similar
            PasswordManager.hash_password("fake_password_for_timing")
        
        # ✅ SEGURANÇA: Delay aleatório para prevenir timing attacks
        time.sleep(random.uniform(0.5, 1.5))
        
        logger.warning(f"❌ Tentativa de login falhada: {username[:3]}***")
        return None
        
    except Exception as e:
        logger.error(f"Erro na autenticação: {str(e)[:50]}")  # Não logar detalhes completos
        return None
    finally:
        session.close()

# --- Gestão de Usuários ---

def get_all_users():
    """Retorna lista de todos os usuários."""
    session = get_session()
    try:
        return session.query(User).all()
    except Exception as e:
        print(f"Erro ao listar usuários: {e}")
        return []
    finally:
        session.close()

def create_user(username, password, full_name, role='AUDITOR', email=None, birth_date=None):
    """
    Cria um novo usuário.
    
    ✅ SEGURANÇA: Valida força da senha e usa bcrypt
    """
    session = get_session()
    try:
        # ✅ SEGURANÇA: Validar username
        valid_user, msg_user = SecurityValidator.validate_username(username)
        if not valid_user:
            logger.warning(f"Username inválido tentado: {username[:10]}")
            return False, msg_user
        
        # Verifica se já existe
        if session.query(User).filter_by(username=username).first():
            logger.warning(f"Tentativa de criar usuário duplicado: {username}")
            return False, "Usuário já existe."
        
        # ✅ SEGURANÇA: Validar força da senha
        valid_pwd, msg_pwd = SecurityValidator.validate_password_strength(password)
        if not valid_pwd:
            logger.warning(f"Senha fraca rejeitada para novo usuário: {username}")
            return False, msg_pwd
        
        # ✅ SEGURANÇA: Hash com bcrypt
        pwd_hash = PasswordManager.hash_password(password)
        
        new_user = User(
            username=username,
            password_hash=pwd_hash,
            full_name=full_name,
            email=email,
            birth_date=birth_date,
            role=role
        )
        session.add(new_user)
        session.commit()
        
        # ✅ LGPD: Auditar criação de usuário
        AuditLogger.log_user_action(
            user_id=new_user.id,
            action=AuditLogger.ACTION_CREATE,
            resource=AuditLogger.RESOURCE_USERS,
            record_id=new_user.id,
            changes={"username": username, "role": role}
        )
        
        logger.info(f"✅ Novo usuário criado: {username} (role: {role})")
        return True, "Usuário criado com sucesso."
    except Exception as e:
        session.rollback()
        logger.error(f"Erro ao criar usuário: {str(e)[:100]}")
        return False, f"Erro ao criar usuário: {str(e)}"
    finally:
        session.close()

def update_user(user_id, full_name, role, is_active, email=None, birth_date=None):
    """Atualiza dados de um usuário (exceto senha)."""
    session = get_session()
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return False, "Usuário não encontrado."
            
        user.full_name = full_name
        user.role = role
        user.is_active = is_active
        user.email = email
        user.birth_date = birth_date
        session.commit()
        return True, "Usuário atualizado com sucesso."
    except Exception as e:
        session.rollback()
        return False, f"Erro ao atualizar usuário: {str(e)}"
    finally:
        session.close()

def change_password(user_id, new_password):
    """
    Altera a senha de um usuário.
    
    ✅ SEGURANÇA: Valida força da senha e usa bcrypt
    """
    session = get_session()
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return False, "Usuário não encontrado."
        
        # ✅ SEGURANÇA: Validar força da nova senha
        valid, msg = SecurityValidator.validate_password_strength(new_password)
        if not valid:
            logger.warning(f"Tentativa de senha fraca ao trocar senha: user_id {user_id}")
            return False, msg
        
    except Exception as e:
        session.rollback()
        logger.error(f"Erro ao alterar senha: {str(e)[:100]}")
        return False, f"Erro ao alterar senha: {str(e)}"
    finally:
        session.close()

def delete_user(user_id):
    """Remove um usuário (ou inativa, dependendo da regra. Aqui vamos remover)."""
    session = get_session()
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return False, "Usuário não encontrado."
        
        # Não permite excluir o admin principal se for regra de negócio, mas por enquanto livre
        if user.username == 'admin':
             return False, "Não é possível excluir o usuário admin principal."

        session.delete(user)
        session.commit()
        return True, "Usuário removido com sucesso."
    except Exception as e:
        session.rollback()
        # Se falhar por FK (tem logs associados), sugerir inativar
        return False, f"Erro ao remover (usuário pode ter histórico): {str(e)}"
    finally:
        session.close()

# --- Relatórios ---

def get_productivity_report():
    """
    Gera um relatório de produtividade por usuário.
    Retorna uma lista de dicionários com:
    - Nome do Usuário
    - Total de Execuções
    - Total de Arquivos
    - Taxa de Sucesso
    - Última Atividade
    """
    session = get_session()
    report_data = []
    try:
        users = session.query(User).all()
        for user in users:
            executions = session.query(ExecutionLog).filter_by(user_id=user.id).all()
            
            total_execs = len(executions)
            total_files = sum(e.total_files or 0 for e in executions) # total_files pode ser null em versoes antigas
            
            # Calcular sucesso real baseados nos contadores
            success_count = sum(e.success_count or 0 for e in executions)
            error_count = sum(e.error_count or 0 for e in executions)
            total_processed = success_count + error_count
            
            success_rate = 0.0
            if total_processed > 0:
                success_rate = (success_count / total_processed) * 100
                
            last_activity = "N/A"
            if executions:
                last_exec = max(executions, key=lambda x: x.start_time)
                last_activity = last_exec.start_time.strftime("%d/%m/%Y %H:%M")
                
            report_data.append({
                "usuario": user.username,
                "nome_completo": user.full_name or "",
                "total_execucoes": total_execs,
                "total_arquivos": total_processed, # Usando processados reais
                "taxa_sucesso": f"{success_rate:.1f}%",
                "ultima_atividade": last_activity
            })
            
        return report_data
    except Exception as e:
        print(f"Erro ao gerar relatório: {e}")
        return []
    finally:
        session.close()

def get_recent_activity(limit=5):
    """Retorna as últimas atividades (execuções) do sistema."""
    session = get_session()
    activities = []
    try:
        logs = session.query(ExecutionLog).order_by(ExecutionLog.start_time.desc()).limit(limit).all()
        for log in logs:
            user_name = "Sistema"
            if log.user:
                user_name = log.user.username
            
            activities.append({
                "id": log.id,
                "tipo": log.operation_type,
                "usuario": user_name,
                "data": log.start_time.strftime("%d/%m %H:%M"),
                "status": log.status,
                "arquivos": log.total_files or 0
            })
        return activities
    except Exception as e:
        print(f"Erro ao buscar atividades recentes: {e}")
        return []
        return []
    finally:
        session.close()


def get_last_execution_time():
    """Retorna a data/hora da última execução em formato legível."""
    session = get_session()
    try:
        last_exec = session.query(ExecutionLog).order_by(
            ExecutionLog.start_time.desc()
        ).first()
        
        if last_exec and last_exec.start_time:
            return last_exec.start_time.strftime("%d/%m %H:%M")
        return None
    except Exception as e:
        print(f"Erro ao buscar última execução: {e}")
        return None
    finally:
        session.close()

# --- ROI Metrics ---

def log_roi_metric(execution_id: int, file_name: str, rule_id: str, 
                   rule_description: str, correction_type: str, financial_impact: float):
    """Registra uma métrica de economia/glosa evitada no banco de dados."""
    if execution_id == -1: return

    session = get_session()
    try:
        new_metric = ROIMetrics(
            execution_id=execution_id,
            file_name=file_name,
            rule_id=rule_id,
            rule_description=rule_description,
            correction_type=correction_type,
            financial_impact=financial_impact
        )
        session.add(new_metric)
        session.commit()
    except Exception as e:
        print(f"Erro ao logar métrica de ROI: {e}")
        session.rollback()
    finally:
        session.close()

def get_roi_stats():
    """
    Retorna estatísticas consolidadas de Economia (Glosas Evitadas + Potencial).
    """
    session = get_session()
    stats = {
        'total_saved': 0.0,  # ROI Realizado (correções)
        'total_corrections': 0,
        'roi_potencial': 0.0,  # ROI Potencial (alertas)
        'total_alertas': 0,
        'roi_total': 0.0,  # Soma total
        'top_rules': []
    }
    try:
        from sqlalchemy import func
        from .models import AlertMetrics
        
        # GLOSAS EVITADAS (Correções automáticas realizadas)
        metrics = session.query(ROIMetrics).all()
        stats['total_corrections'] = len(metrics)
        stats['total_saved'] = sum(m.financial_impact for m in metrics)
        
        # ECONOMIA POTENCIAL (Alertas pendentes de revisão)
        alertas = session.query(AlertMetrics).filter_by(status='POTENCIAL').all()
        stats['total_alertas'] = len(alertas)
        stats['roi_potencial'] = sum(a.financial_impact for a in alertas)
        
        # ECONOMIA TOTAL (Glosas + Potencial)
        stats['roi_total'] = stats['total_saved'] + stats['roi_potencial']
        
        # Top regras (mantém lógica existente)
        top_rules_query = session.query(
            ROIMetrics.rule_id,
            ROIMetrics.rule_description,
            func.count(ROIMetrics.id).label('count'),
            func.sum(ROIMetrics.financial_impact).label('total_impact')
        ).group_by(ROIMetrics.rule_id).order_by(func.sum(ROIMetrics.financial_impact).desc()).limit(5).all()
        
        for r in top_rules_query:
            stats['top_rules'].append({
                'rule_id': r.rule_id,
                'description': r.rule_description,
                'count': r.count,
                'total_impact': r.total_impact
            })
            
    except Exception as e:
        print(f"Erro ao buscar estatísticas de ROI: {e}")
    finally:
        session.close()
        
    return stats


def log_alert_metric(execution_id: int, file_name: str, alert_type: str, 
                     description: str, financial_impact: float) -> bool:
    '''Registra um alerta no banco de dados.'''
    session = get_session()
    try:
        from .models import AlertMetrics
        
        new_alert = AlertMetrics(
            execution_id=execution_id,
            file_name=file_name,
            alert_type=alert_type,
            alert_description=description,
            financial_impact=financial_impact,
            status='POTENCIAL'
        )
        
        session.add(new_alert)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f'Erro ao logar alerta: {e}')
        return False
    finally:
        session.close()


def get_alert_stats(execution_id: int) -> dict:
    '''Retorna estatísticas de alertas de uma execução.'''
    session = get_session()
    try:
        from .models import AlertMetrics
        from sqlalchemy import func
        
        total = session.query(func.count(AlertMetrics.id)).\
                filter_by(execution_id=execution_id).scalar() or 0
        
        roi = session.query(func.sum(AlertMetrics.financial_impact)).\
              filter_by(execution_id=execution_id).scalar() or 0.0
        
        return {
            'total_alertas': total,
            'roi_potencial': roi
        }
    except Exception as e:
        print(f'Erro ao obter estatísticas de alertas: {e}')
        return {'total_alertas': 0, 'roi_potencial': 0.0}
    finally:
        session.close()
def reset_processing_data():
    """
    Remove todos os registros de execução, logs de arquivos e métricas.
    Útil para reiniciar o processamento do zero ou re-processar mesmos arquivos.
    Mantém usuários e configurações.
    """
    session = get_session()
    try:
        from sqlalchemy import text
        
        # Ordem de remoção para respeitar FKs
        if DB_PROVIDER == "postgresql":
            # Usar TRUNCATE no PostgreSQL para ser mais rápido e resetar IDs
            session.execute(text("TRUNCATE TABLE alert_metrics, roi_metrics, file_logs, execution_logs, audit_logs CASCADE"))
        else:
            # SQLite
            session.query(AlertMetrics).delete()
            session.query(ROIMetrics).delete()
            session.query(FileLog).delete()
            session.query(ExecutionLog).delete()
            session.query(AuditLog).delete()
            
        session.commit()
        logger.info("🗑️ Banco de dados de processamento resetado com sucesso.")
        return True, "Dados de processamento limpos com sucesso!"
    except Exception as e:
        session.rollback()
        logger.error(f"Erro ao resetar banco: {e}")
        return False, f"Erro ao resetar: {e}"
    finally:
        session.close()
