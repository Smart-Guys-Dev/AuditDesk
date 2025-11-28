import os
import hashlib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime
from .models import Base, ExecutionLog, FileLog, User, ROIMetrics

# Nome do arquivo do banco de dados
DB_FILE = "audit_plus.db"
DATABASE_URL = f"sqlite:///{DB_FILE}"

# Engine global
engine = create_engine(DATABASE_URL, echo=False)

# Session Factory
SessionFactory = sessionmaker(bind=engine)
Session = scoped_session(SessionFactory)

def init_db():
    """Cria as tabelas no banco de dados se não existirem e cria usuário admin."""
    Base.metadata.create_all(engine)
    print(f"Banco de dados inicializado em: {os.path.abspath(DB_FILE)}")
    
    # Criar usuário admin padrão se não existir
    session = get_session()
    try:
        admin = session.query(User).filter_by(username='admin').first()
        if not admin:
            # Senha padrão: admin123 (hash simples para exemplo, ideal usar bcrypt)
            # MD5 apenas para demonstração rápida, em prod usaríamos bcrypt/argon2
            pwd_hash = hashlib.sha256("admin123".encode()).hexdigest()
            
            new_admin = User(
                username='admin',
                password_hash=pwd_hash,
                full_name='Administrador do Sistema',
                role='ADMIN'
            )
            session.add(new_admin)
            session.commit()
            print("Usuário 'admin' criado com senha padrão 'admin123'.")
    except Exception as e:
        print(f"Erro ao criar admin: {e}")
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

def log_file_processed(execution_id: int, file_name: str, file_path: str, status: str, message: str = None):
    """Registra o processamento de um arquivo individual."""
    if execution_id == -1: return

    session = get_session()
    try:
        new_file_log = FileLog(
            execution_id=execution_id,
            file_name=file_name,
            file_path=file_path,
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

def get_dashboard_stats():
    """Retorna estatísticas gerais para o dashboard."""
    session = get_session()
    stats = {
        'total_executions': 0,
        'total_files': 0,
        'success_count': 0,
        'error_count': 0,
        'success_rate': 0.0
    }
    try:
        # Agregar dados de ExecutionLog
        executions = session.query(ExecutionLog).all()
        stats['total_executions'] = len(executions)
        
        for exc in executions:
            stats['total_files'] += (exc.success_count + exc.error_count) # ou exc.total_files se confiável
            stats['success_count'] += exc.success_count
            stats['error_count'] += exc.error_count
            
        if stats['total_files'] > 0:
            stats['success_rate'] = (stats['success_count'] / stats['total_files']) * 100
            
    except Exception as e:
        print(f"Erro ao gerar estatísticas: {e}")
    finally:
        session.close()
    
    
    return stats

def authenticate_user(username, password):
    """
    Verifica as credenciais do usuário.
    Retorna o objeto User se válido, ou None se inválido.
    """
    session = get_session()
    try:
        user = session.query(User).filter_by(username=username, is_active=True).first()
        if user:
            # Verifica senha (hash SHA-256 simples conforme definido no init_db)
            # Em produção, usaríamos bcrypt.checkpw()
            input_hash = hashlib.sha256(password.encode()).hexdigest()
            if input_hash == user.password_hash:
                return user
        return None
    except Exception as e:
        print(f"Erro na autenticação: {e}")
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

def create_user(username, password, full_name, role='AUDITOR'):
    """Cria um novo usuário."""
    session = get_session()
    try:
        # Verifica se já existe
        if session.query(User).filter_by(username=username).first():
            return False, "Usuário já existe."
            
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        new_user = User(
            username=username,
            password_hash=pwd_hash,
            full_name=full_name,
            role=role
        )
        session.add(new_user)
        session.commit()
        return True, "Usuário criado com sucesso."
    except Exception as e:
        session.rollback()
        return False, f"Erro ao criar usuário: {str(e)}"
    finally:
        session.close()

def update_user(user_id, full_name, role, is_active):
    """Atualiza dados de um usuário (exceto senha)."""
    session = get_session()
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return False, "Usuário não encontrado."
            
        user.full_name = full_name
        user.role = role
        user.is_active = is_active
        session.commit()
        return True, "Usuário atualizado com sucesso."
    except Exception as e:
        session.rollback()
        return False, f"Erro ao atualizar usuário: {str(e)}"
    finally:
        session.close()

def change_password(user_id, new_password):
    """Altera a senha de um usuário."""
    session = get_session()
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return False, "Usuário não encontrado."
            
        user.password_hash = hashlib.sha256(new_password.encode()).hexdigest()
        session.commit()
        return True, "Senha alterada com sucesso."
    except Exception as e:
        session.rollback()
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

# --- ROI Metrics ---

def log_roi_metric(execution_id: int, file_name: str, rule_id: str, 
                   rule_description: str, correction_type: str, financial_impact: float):
    """Registra uma métrica de ROI no banco de dados."""
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
    Retorna estatísticas consolidadas de ROI.
    """
    session = get_session()
    stats = {
        'total_saved': 0.0,
        'total_corrections': 0,
        'top_rules': []
    }
    try:
        metrics = session.query(ROIMetrics).all()
        stats['total_corrections'] = len(metrics)
        stats['total_saved'] = sum(m.financial_impact for m in metrics)
        
        # Top regras
        from sqlalchemy import func
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
