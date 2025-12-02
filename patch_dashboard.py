#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para atualizar dashboard_page.py com ROI Realizado vs Potencial
"""

# Ler arquivo
with open('src/dashboard_page.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Substituir criação dos cards KPI (linhas 82-85 aproximadamente)
old_cards = '''        self.card_total_saved = KPICard("Valor Recuperado", "R$ 0,00", "💰", "#A3BE8C") # Verde
        self.card_corrections = KPICard("Correções Aplicadas", "0", "🔧", "#EBCB8B") # Amarelo
        self.card_files = KPICard("Arquivos Processados", "0", "📄", "#88C0D0") # Azul
        self.card_roi = KPICard("ROI Estimado", "0%", "📈", "#B48EAD") # Roxo'''

new_cards = '''        self.card_roi_realizado = KPICard("ROI Realizado", "R$ 0,00", "✅", "#A3BE8C") # Verde
        self.card_roi_potencial = KPICard("ROI Potencial", "R$ 0,00", "⚠️", "#EBCB8B") # Amarelo
        self.card_roi_total = KPICard("ROI Total", "R$ 0,00", "💰", "#88C0D0") # Azul
        self.card_alertas = KPICard("Alertas Pendentes", "0", "🔔", "#B48EAD") # Roxo'''

content = content.replace(old_cards, new_cards)

# 2. Substituir adição dos cards ao layout
old_layout = '''        self.kpi_layout.addWidget(self.card_total_saved)
        self.kpi_layout.addWidget(self.card_corrections)
        self.kpi_layout.addWidget(self.card_files)
        self.kpi_layout.addWidget(self.card_roi)'''

new_layout = '''        self.kpi_layout.addWidget(self.card_roi_realizado)
        self.kpi_layout.addWidget(self.card_roi_potencial)
        self.kpi_layout.addWidget(self.card_roi_total)
        self.kpi_layout.addWidget(self.card_alertas)'''

content = content.replace(old_layout, new_layout)

# 3. Substituir atualização dos KPIs no load_data
old_load = '''        # Atualizar KPIs
        total_saved = roi_stats['total_saved']
        self.card_total_saved.update_value(f"R$ {total_saved:,.2f}")
        self.card_corrections.update_value(str(roi_stats['total_corrections']))
        self.card_files.update_value(str(general_stats['total_files']))
        
        # ROI Simulado (Exemplo: Custo da ferramenta vs Economia)
        # Se não houver custo definido, ROI é infinito ou baseado apenas no valor
        self.card_roi.update_value("∞")'''

new_load = '''        # Atualizar KPIs com ROI Realizado vs Potencial
        self.card_roi_realizado.update_value(f"R$ {roi_stats['total_saved']:,.2f}")
        self.card_roi_potencial.update_value(f"R$ {roi_stats['roi_potencial']:,.2f}")
        self.card_roi_total.update_value(f"R$ {roi_stats['roi_total']:,.2f}")
        self.card_alertas.update_value(str(roi_stats['total_alertas']))'''

content = content.replace(old_load, new_load)

# Salvar
with open('src/dashboard_page.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Dashboard atualizado com ROI Realizado vs Potencial!")
print("  - 4 novos cards: Realizado, Potencial, Total, Alertas")
print("  - load_data() atualizado para usar novos dados")
