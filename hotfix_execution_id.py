#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Hotfix: Adicionar current_execution_id ao WorkflowController
"""

# Ler arquivo
with open('src/workflow_controller.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Adicionar current_execution_id no __init__
old_init = '''    def __init__(self):
        self.lista_faturas_processadas: List[dict] = []
        self.pasta_faturas_importadas_atual: Optional[str] = None
        self.plano_ultima_distribuicao: dict = {}
        self.guias_relevantes_por_fatura: dict = {}

        data_manager.carregar_dados_unimed()'''

new_init = '''    def __init__(self):
        self.lista_faturas_processadas: List[dict] = []
        self.pasta_faturas_importadas_atual: Optional[str] = None
        self.plano_ultima_distribuicao: dict = {}
        self.guias_relevantes_por_fatura: dict = {}
        self.current_execution_id = -1  # Para tracking de ROI

        data_manager.carregar_dados_unimed()'''

content = content.replace(old_init, new_init)

# Salvar
with open('src/workflow_controller.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Hotfix aplicado!")
print("  - current_execution_id inicializado no __init__")
print("\n⚠️  NOTA: Por enquanto será -1 (sem tracking de execução)")
print("   Para tracking completo, precisa integrar com ExecutionLog")
