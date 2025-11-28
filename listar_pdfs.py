#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para extrair texto dos PDFs de referência
"""
import os

# Lista os arquivos PDF
pasta = r"c:\Users\pedro.freitas\AuditPlusv2.0\docs\referencias"
pdfs = [f for f in os.listdir(pasta) if f.endswith('.pdf')]

print(f"📚 {len(pdfs)} PDFs encontrados:\n")
for i, pdf in enumerate(pdfs, 1):
    caminho = os.path.join(pasta, pdf)
    tamanho_mb = os.path.getsize(caminho) / (1024*1024)
    print(f"{i}. {pdf}")
    print(f"   Tamanho: {tamanho_mb:.2f} MB\n")

print("\n💡 Para ler os PDFs, preciso instalar PyPDF2 ou pdfplumber.")
print("Deseja que eu instale? (usuário precisa confirmar)")
