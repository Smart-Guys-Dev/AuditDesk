#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Testes para xml_parser.py - Fase 1: Extração de Valores  

TDD (Test-Driven Development):
1. RED: Escrever testes que FALHAM
2. GREEN: Implementar código mínimo para PASSAR
3. REFACTOR: Melhorar código mantendo testes passando
"""
import unittest
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import lxml.etree as etree

class TestExtrairValorTotalGuia(unittest.TestCase):
    """Testes para a função extrair_valor_total_guia()"""
    
    @classmethod
    def setUpClass(cls):
        """Carrega XML de teste uma vez para todos os testes"""
        cls.xml_path = os.path.join(
            os.path.dirname(__file__), 
            'fixtures', 
            'internacao_curta.xml'
        )
        # Namespace PTU Unimed (produção)
        cls.NAMESPACES = {
            'ptu': 'http://ptu.unimed.coop.br/schemas/V3_0'
        }
    
    def setUp(self):
        """Executa antes de cada teste"""
        self.tree = etree.parse(self.xml_path)
        self.guia_element = self.tree.find(
            './/ptu:guiaInternacao',
            namespaces=self.NAMESPACES
        )
    
    def test_01_extrair_valor_existente(self):
        """Deve extrair valor 1250.50 quando existe no XML"""
        from xml_parser import extrair_valor_total_guia
        
        valor = extrair_valor_total_guia(self.guia_element)
        
        self.assertIsInstance(valor, float, "Valor deve ser float")
        self.assertEqual(valor, 1250.50, "Valor deve ser 1250.50")
    
    def test_02_extrair_valor_com_virgula(self):
        """Deve converter vírgula para ponto (1.250,50 → 1250.50)"""
        from xml_parser import extrair_valor_total_guia
        
        # Modifica temporariamente o valor no XML
        valor_element = self.guia_element.find(
            './/ptu:valorTotal/ptu:valorTotalGeral',
            namespaces=self.NAMESPACES
        )
        valor_original = valor_element.text
        valor_element.text = "1250,50"  # Com vírgula
        
        valor = extrair_valor_total_guia(self.guia_element)
        
        # Restaura valor original
        valor_element.text = valor_original
        
        self.assertEqual(valor, 1250.50, "Deve converter vírgula para ponto")
    
    def test_03_extrair_valor_inexistente(self):
        """Deve retornar 0.0 quando não há tag de valor"""
        from xml_parser import extrair_valor_total_guia
        
        # Cria elemento vazio sem valor
        elemento_vazio = etree.Element(
            '{http://ptu.unimed.coop.br/schemas/V3_0}guiaInternacao'
        )
        
        valor = extrair_valor_total_guia(elemento_vazio)
        
        self.assertEqual(valor, 0.0, "Deve retornar 0.0 quando não há valor")
    
    def test_04_extrair_valor_none(self):
        """Deve tratar None sem erro"""
        from xml_parser import extrair_valor_total_guia
        
        valor = extrair_valor_total_guia(None)
        
        self.assertEqual(valor, 0.0, "Deve retornar 0.0 para None")
    
    def test_05_extrair_valor_invalido(self):
        """Deve retornar 0.0 para valor não-numérico"""
        from xml_parser import extrair_valor_total_guia
        
        # Modifica temporariamente o valor para string inválida
        valor_element = self.guia_element.find(
            './/ptu:valorTotal/ptu:valorTotalGeral',
            namespaces=self.NAMESPACES
        )
        valor_original = valor_element.text
        valor_element.text = "INVALIDO"
        
        valor = extrair_valor_total_guia(self.guia_element)
        
        # Restaura valor original
        valor_element.text = valor_original
        
        self.assertEqual(valor, 0.0, "Deve retornar 0.0 para valor inválido")


if __name__ == '__main__':
    # Rodar testes com verbosidade
    unittest.main(verbosity=2)
