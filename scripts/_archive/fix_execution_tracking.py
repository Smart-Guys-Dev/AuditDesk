#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fix: Criar execution_id válido no início da validação
"""

# Ler arquivo
with open('src/workflow_controller.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Adicionar import do db_manager no topo
if 'from .database import db_manager' not in content:
    old_imports = '''from . import (data_manager, distribution_engine, file_manager,
               hash_calculator, report_generator, xml_parser,
               rule_engine)'''
    
    new_imports = '''from . import (data_manager, distribution_engine, file_manager,
               hash_calculator, report_generator, xml_parser,
               rule_engine)
from .database import db_manager'''
    
    content = content.replace(old_imports, new_imports)

# 2. Adicionar log_execution_start no início da validação
old_validation_start = '''            log(f"INFO: {len(xml_files)} arquivo(s) encontrados. Iniciando validação...")
            modificados = 0
            
            for xml_file in xml_files:'''

new_validation_start = '''            log(f"INFO: {len(xml_files)} arquivo(s) encontrados. Iniciando validação...")
            
            # Criar registro de execução para tracking de ROI
            self.current_execution_id = db_manager.log_execution_start(
                operation_type='VALIDATION',
                total_files=len(xml_files)
            )
            log(f"INFO: Execução ID {self.current_execution_id} criada.")
            
            modificados = 0
            
            for xml_file in xml_files:'''

content = content.replace(old_validation_start, new_validation_start)

# 3. Adicionar log_execution_end no final da validação
old_validation_end = '''            msg_final = f"Validação concluída. {modificados} de {len(xml_files)} arquivo(s) foram modificados."
            log(f"SUCESSO: {msg_final}")
            return True, msg_final'''

new_validation_end = '''            msg_final = f"Validação concluída. {modificados} de {len(xml_files)} arquivo(s) foram modificados."
            log(f"SUCESSO: {msg_final}")
            
            # Finalizar registro de execução
            db_manager.log_execution_end(
                execution_id=self.current_execution_id,
                status='COMPLETED',
                success_count=modificados,
                error_count=len(xml_files) - modificados
            )
            
            return True, msg_final'''

content = content.replace(old_validation_end, new_validation_end)

# Salvar
with open('src/workflow_controller.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Tracking de execução implementado!")
print("  - log_execution_start() no início da validação")
print("  - execution_id válido criado")
print("  - log_execution_end() no final")
print("\n📊 Agora o ROI será registrado corretamente!")
