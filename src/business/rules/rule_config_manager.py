"""
Sistema de gerenciamento de regras com feature flags.

Permite:
- Habilitar/desabilitar regras individualmente
- Versionamento de configurações
- Audit log de mudanças
- Rollback para versão anterior
"""
import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class RuleConfigManager:
    """Gerencia configurações de regras com versionamento e audit log"""
    
    def __init__(self, config_dir: str = None):
        """
        Inicializa o gerenciador.
        
        Args:
            config_dir: Diretório de configurações (padrão: src/config)
        """
        if config_dir is None:
            # Detectar config_dir automaticamente
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent.parent
            self.config_dir = project_root / "config"
        else:
            self.config_dir = Path(config_dir)
        
        # Diretórios de versionamento e audit
        self.versions_dir = self.config_dir / ".versions"
        self.audit_log_file = self.config_dir / ".audit_log.jsonl"
        
        # Criar diretórios se não existem
        self.versions_dir.mkdir(exist_ok=True)
        
        logger.info(f"RuleConfigManager inicializado: {self.config_dir}")
    
    def get_rule_file_path(self, rule_file: str) -> Path:
        """Retorna caminho completo do arquivo de regras"""
        return self.config_dir / rule_file
    
    def load_rules(self, rule_file: str) -> List[Dict]:
        """
        Carrega regras de um arquivo.
        
        Args:
            rule_file: Nome do arquivo (ex: 'regras_grupo_1200.json')
            
        Returns:
            Lista de regras
        """
        file_path = self.get_rule_file_path(rule_file)
        
        if not file_path.exists():
            logger.warning(f"Arquivo não encontrado: {file_path}")
            return []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Se for dicionário com chave 'rules', extrair
        if isinstance(data, dict) and 'rules' in data:
            return data['rules']
        elif isinstance(data, list):
            return data
        else:
            logger.error(f"Formato inesperado em {rule_file}")
            return []
    
    def save_rules(self, rule_file: str, rules: List[Dict], user: str = "system"):
        """
        Salva regras com versionamento automático.
        
        Args:
            rule_file: Nome do arquivo
            rules: Lista de regras
            user: Usuário que está salvando
        """
        file_path = self.get_rule_file_path(rule_file)
        
        # Criar backup/versão ANTES de salvar
        if file_path.exists():
            self._create_version(rule_file, user)
        
        # Salvar arquivo
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(rules, f, indent=2, ensure_ascii=False)
        
        # Log da mudança
        self._log_change(rule_file, "save_rules", user, f"Salvo com {len(rules)} regras")
        
        logger.info(f"Regras salvas: {file_path} ({len(rules)} regras)")
    
    def enable_rule(self, rule_file: str, rule_id: str, user: str = "admin"):
        """
        Habilita uma regra específica.
        
        Args:
            rule_file: Arquivo de regras
            rule_id: ID da regra
            user: Usuário fazendo a mudança
        """
        rules = self.load_rules(rule_file)
        
        # Encontrar e habilitar regra
        rule_found = False
        for rule in rules:
            if rule.get('id') == rule_id:
                rule['enabled'] = True
                rule_found = True
                break
        
        if not rule_found:
            logger.warning(f"Regra {rule_id} não encontrada em {rule_file}")
            return False
        
        # Salvar
        self.save_rules(rule_file, rules, user)
        self._log_change(rule_file, "enable_rule", user, f"Habilitada regra: {rule_id}")
        
        logger.info(f"✅ Regra habilitada: {rule_id}")
        return True
    
    def disable_rule(self, rule_file: str, rule_id: str, user: str = "admin", reason: str = ""):
        """
        Desabilita uma regra específica.
        
        Args:
            rule_file: Arquivo de regras
            rule_id: ID da regra
            user: Usuário fazendo a mudança
            reason: Motivo da desabilitação
        """
        rules = self.load_rules(rule_file)
        
        # Encontrar e desabilitar regra
        rule_found = False
        for rule in rules:
            if rule.get('id') == rule_id:
                rule['enabled'] = False
                rule_found = True
                break
        
        if not rule_found:
            logger.warning(f"Regra {rule_id} não encontrada em {rule_file}")
            return False
        
        # Salvar
        self.save_rules(rule_file, rules, user)
        
        log_msg = f"Desabilitada regra: {rule_id}"
        if reason:
            log_msg += f" | Motivo: {reason}"
        
        self._log_change(rule_file, "disable_rule", user, log_msg)
        
        logger.info(f"🚫 Regra desabilitada: {rule_id} | Motivo: {reason}")
        return True
    
    def get_rule_status(self, rule_file: str, rule_id: str) -> Optional[bool]:
        """
        Verifica se uma regra está habilitada.
        
        Returns:
            True se habilitada, False se desabilitada, None se não encontrada
        """
        rules = self.load_rules(rule_file)
        
        for rule in rules:
            if rule.get('id') == rule_id:
                # Se não tem campo 'enabled', assume True (retrocompatibilidade)
                return rule.get('enabled', True)
        
        return None
    
    def list_disabled_rules(self, rule_file: str = None) -> List[Dict]:
        """
        Lista todas as regras desabilitadas.
        
        Args:
            rule_file: Arquivo específico, ou None para todos
            
        Returns:
            Lista de dicionários com regra info
        """
        disabled = []
        
        # Se não especificou arquivo, buscar todos
        if rule_file is None:
            rule_files = [f.name for f in self.config_dir.glob("regras_grupo_*.json")]
        else:
            rule_files = [rule_file]
        
        for rf in rule_files:
            rules = self.load_rules(rf)
            for rule in rules:
                if rule.get('enabled', True) == False:
                    disabled.append({
                        'file': rf,
                        'id': rule.get('id'),
                        'descricao': rule.get('descricao', 'N/A')
                    })
        
        return disabled
    
    def _create_version(self, rule_file: str, user: str):
        """Cria versão/backup do arquivo de regras"""
        source = self.get_rule_file_path(rule_file)
        
        if not source.exists():
            return
        
        # Nome da versão com timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version_name = f"{rule_file}.{timestamp}.backup"
        version_path = self.versions_dir / version_name
        
        # Copiar arquivo
        shutil.copy2(source, version_path)
        
        logger.debug(f"Versão criada: {version_path}")
    
    def _log_change(self, rule_file: str, action: str, user: str, details: str):
        """Registra mudança no audit log"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'file': rule_file,
            'action': action,
            'user': user,
            'details': details
        }
        
        # Append to JSONL file
        with open(self.audit_log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    def get_audit_log(self, limit: int = 50) -> List[Dict]:
        """
        Retorna últimas entradas do audit log.
        
        Args:
            limit: Número máximo de entradas
            
        Returns:
            Lista de entradas (mais recentes primeiro)
        """
        if not self.audit_log_file.exists():
            return []
        
        entries = []
        with open(self.audit_log_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))
        
        # Retornar as últimas 'limit' entradas
        return entries[-limit:][::-1]  # Inverter para mais recentes primeiro
    
    def list_versions(self, rule_file: str) -> List[Dict]:
        """
        Lista versões disponíveis de um arquivo.
        
        Returns:
            Lista de dicionários com info da versão
        """
        pattern = f"{rule_file}.*.backup"
        versions = []
        
        for version_file in self.versions_dir.glob(pattern):
            # Extrair timestamp do nome
            parts = version_file.stem.split('.')
            if len(parts) >= 2:
                timestamp_str = parts[-2]  # Formato: YYYYMMDD_HHMMSS
                
                versions.append({
                    'file': version_file.name,
                    'timestamp': timestamp_str,
                    'path': str(version_file),
                    'size': version_file.stat().st_size
                })
        
        # Ordenar por timestamp (mais recente primeiro)
        versions.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return versions
    
    def rollback(self, rule_file: str, version_timestamp: str, user: str = "admin"):
        """
        Faz rollback para uma versão anterior.
        
        Args:
            rule_file: Arquivo de regras
            version_timestamp: Timestamp da versão (formato: YYYYMMDD_HHMMSS)
            user: Usuário fazendo rollback
        """
        # Encontrar arquivo de versão
        version_name = f"{rule_file}.{version_timestamp}.backup"
        version_path = self.versions_dir / version_name
        
        if not version_path.exists():
            logger.error(f"Versão não encontrada: {version_name}")
            return False
        
        # Criar backup da versão atual ANTES do rollback
        current_path = self.get_rule_file_path(rule_file)
        if current_path.exists():
            self._create_version(rule_file, user)
        
        # Copiar versão antiga para o arquivo atual
        shutil.copy2(version_path, current_path)
        
        # Log
        self._log_change(
            rule_file,
            "rollback",
            user,
            f"Rollback para versão: {version_timestamp}"
        )
        
        logger.info(f"🔙 Rollback realizado: {rule_file} → {version_timestamp}")
        return True
