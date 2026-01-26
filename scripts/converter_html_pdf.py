# -*- coding: utf-8 -*-
"""
Script para converter documentos HTML de regras para PDF.
Usa weasyprint (instalado automaticamente).
"""
import os
import sys
from pathlib import Path

def converter_html_para_pdf():
    """Converte todos os arquivos HTML da pasta docs/regras para PDF."""
    
    try:
        from weasyprint import HTML
    except ImportError:
        print("❌ Biblioteca 'weasyprint' não encontrada.")
        print("   Execute: pip install weasyprint")
        return False
    
    # Diretório das regras
    script_dir = Path(__file__).parent
    regras_dir = script_dir.parent / "docs" / "regras"
    
    if not regras_dir.exists():
        print(f"❌ Diretório não encontrado: {regras_dir}")
        return False
    
    # Encontrar arquivos HTML
    html_files = list(regras_dir.glob("*.html"))
    
    if not html_files:
        print("❌ Nenhum arquivo HTML encontrado em docs/regras/")
        return False
    
    print("=" * 50)
    print("CONVERSÃO HTML → PDF")
    print("=" * 50)
    
    convertidos = 0
    
    for html_file in html_files:
        pdf_file = html_file.with_suffix('.pdf')
        
        print(f"\n📄 Convertendo: {html_file.name}")
        
        try:
            HTML(filename=str(html_file)).write_pdf(str(pdf_file))
            print(f"   ✅ Gerado: {pdf_file.name}")
            convertidos += 1
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    
    print("\n" + "=" * 50)
    print(f"Convertidos: {convertidos}/{len(html_files)}")
    print("=" * 50)
    
    return convertidos > 0


if __name__ == "__main__":
    converter_html_para_pdf()
