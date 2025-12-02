#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para corrigir layout do dashboard
"""

# Ler arquivo
with open('src/dashboard_page.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Ajustar larguras das colunas da tabela para não cortar
old_table_setup = '''        self.rules_table = QTableWidget()
        self.rules_table.setColumnCount(3)
        self.rules_table.setHorizontalHeaderLabels(["Regra", "Qtd.", "Impacto (R$)"])
        self.rules_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)'''

new_table_setup = '''        self.rules_table = QTableWidget()
        self.rules_table.setColumnCount(3)
        self.rules_table.setHorizontalHeaderLabels(["Regra", "Qtd.", "Impacto (R$)"])
        
        # Configurar larguras das colunas
        header = self.rules_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Regra: estica
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)     # Qtd: fixa
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)     # Impacto: fixa
        self.rules_table.setColumnWidth(1, 80)   # Qtd: 80px
        self.rules_table.setColumnWidth(2, 150)  # Impacto: 150px'''

content = content.replace(old_table_setup, new_table_setup)

# 2. Ajustar proporção entre tabela e gráfico
old_layout = '''        content_layout.addWidget(table_container, 2) # Peso 2

        # Gráfico (Placeholder por enquanto, ou simples)
        chart_container = QFrame()
        chart_container.setStyleSheet("background-color: #2E3440; border-radius: 8px;")
        chart_layout = QVBoxLayout(chart_container)
        
        lbl_chart = QLabel("Distribuição de Impacto")
        lbl_chart.setStyleSheet("font-size: 16px; font-weight: bold; color: #ECEFF4; margin-bottom: 10px;")
        chart_layout.addWidget(lbl_chart)
        
        self.figure = plt.figure(facecolor='#2E3440')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: transparent;")
        chart_layout.addWidget(self.canvas)

        content_layout.addWidget(chart_container, 1) # Peso 1'''

new_layout = '''        content_layout.addWidget(table_container, 3) # Peso 3 (maior)

        # Gráfico
        chart_container = QFrame()
        chart_container.setStyleSheet("background-color: #2E3440; border-radius: 8px; padding: 10px;")
        chart_layout = QVBoxLayout(chart_container)
        
        lbl_chart = QLabel("📊 Distribuição de Impacto")
        lbl_chart.setStyleSheet("font-size: 16px; font-weight: bold; color: #ECEFF4; margin-bottom: 10px;")
        chart_layout.addWidget(lbl_chart)
        
        # Figura maior e com melhor proporção
        self.figure = plt.figure(figsize=(6, 5), facecolor='#2E3440')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: transparent;")
        self.canvas.setMinimumSize(400, 350)  # Tamanho mínimo
        chart_layout.addWidget(self.canvas)

        content_layout.addWidget(chart_container, 2) # Peso 2'''

content = content.replace(old_layout, new_layout)

# 3. Melhorar formatação da tabela no load_data
old_table_update = '''        for rule in roi_stats['top_rules']:
            row = self.rules_table.rowCount()
            self.rules_table.insertRow(row)
            
            desc = f"{rule['rule_id']} - {rule['description']}"
            self.rules_table.setItem(row, 0, QTableWidgetItem(desc))
            self.rules_table.setItem(row, 1, QTableWidgetItem(str(rule['count'])))
            self.rules_table.setItem(row, 2, QTableWidgetItem(f"R$ {rule['total_impact']:,.2f}"))'''

new_table_update = '''        for rule in roi_stats['top_rules']:
            row = self.rules_table.rowCount()
            self.rules_table.insertRow(row)
            
            # Nome da regra (truncado se muito longo)
            rule_name = rule['rule_id']
            if len(rule_name) > 60:
                rule_name = rule_name[:57] + "..."
            
            desc = f"{rule_name} - {rule['description'][:50]}..."
            item_desc = QTableWidgetItem(desc)
            item_desc.setToolTip(f"{rule['rule_id']} - {rule['description']}")  # Tooltip completo
            
            item_qtd = QTableWidgetItem(str(rule['count']))
            item_qtd.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            item_impact = QTableWidgetItem(f"R$ {rule['total_impact']:,.2f}")
            item_impact.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            
            self.rules_table.setItem(row, 0, item_desc)
            self.rules_table.setItem(row, 1, item_qtd)
            self.rules_table.setItem(row, 2, item_impact)
            
            # Ajustar altura da linha
            self.rules_table.setRowHeight(row, 40)'''

content = content.replace(old_table_update, new_table_update)

# Salvar
with open('src/dashboard_page.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Dashboard ajustado!")
print("  - Colunas da tabela com larguras fixas")
print("  - Gráfico maior e com padding")
print("  - Texto truncado com tooltips")
print("  - Alinhamento de valores melhorado")
print("\n🎨 Reinicie a aplicação para ver as mudanças!")
