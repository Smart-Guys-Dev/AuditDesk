#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Testes para AlertMetrics - Fase 2: Persistência de Alertas

TDD (Test-Driven Development):
1. RED: Escrever testes que FALHAM
2. GREEN: Implementar código para PASSAR
3. REFACTOR: Melhorar código
"""
import unittest
import os
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sqlalchemy import create_engine, inspect, func
from sqlalchemy.orm import sessionmaker


class TestAlertMetrics(unittest.TestCase):
    """Testes para tabela AlertMetrics e funções relacionadas"""
    
    @classmethod
    def setUpClass(cls):
        """Configuração inicial para todos os testes"""
        # Banco de dados em memória para testes
        cls.engine = create_engine('sqlite:///:memory:', echo=False)
        cls.Session = sessionmaker(bind=cls.engine)
    
    def setUp(self):
        """Executa antes de cada teste - cria tabelas"""
        from database.models import Base
        Base.metadata.create_all(self.engine)
        self.session = self.Session()
    
    def tearDown(self):
        """Executa após cada teste - limpa banco"""
        self.session.close()
        from database.models import Base
        Base.metadata.drop_all(self.engine)
    
    def test_01_criar_tabela_alert_metrics(self):
        """Deve criar tabela alert_metrics no banco"""
        from database.models import AlertMetrics
        
        inspector = inspect(self.engine)
        tables = inspector.get_table_names()
        
        self.assertIn('alert_metrics', tables, "Tabela alert_metrics deve existir")
    
    def test_02_inserir_alerta_com_valor(self):
        """Deve inserir alerta com valor financeiro"""
        from database.models import AlertMetrics
        
        alerta = AlertMetrics(
            execution_id=1,
            file_name='test_internacao.xml',
            alert_type='INTERNACAO_CURTA',
            alert_description='Internação < 12h - Risco de glosa',
            financial_impact=1250.50,
            status='POTENCIAL'
        )
        
        self.session.add(alerta)
        self.session.commit()
        
        # Buscar alerta inserido
        resultado = self.session.query(AlertMetrics).first()
        
        self.assertIsNotNone(resultado, "Alerta deve ser inserido")
        self.assertEqual(resultado.file_name, 'test_internacao.xml')
        self.assertEqual(resultado.financial_impact, 1250.50)
        self.assertEqual(resultado.status, 'POTENCIAL')
    
    def test_03_consultar_alertas_por_execution(self):
        """Deve retornar todos os alertas de uma execução específica"""
        from database.models import AlertMetrics
        
        # Inserir 3 alertas para execution_id=1
        for i in range(3):
            self.session.add(AlertMetrics(
                execution_id=1,
                file_name=f'test{i}.xml',
                alert_type='INTERNACAO_CURTA',
                financial_impact=1000.0 * (i + 1)
            ))
        
        # Inserir 2 alertas para execution_id=2
        for i in range(2):
            self.session.add(AlertMetrics(
                execution_id=2,
                file_name=f'other{i}.xml',
                alert_type='INTERNACAO_CURTA',
                financial_impact=500.0
            ))
        
        self.session.commit()
        
        # Consultar apenas execution_id=1
        alertas_exec1 = self.session.query(AlertMetrics).filter_by(execution_id=1).all()
        
        self.assertEqual(len(alertas_exec1), 3, "Deve retornar 3 alertas da execução 1")
    
    def test_04_calcular_roi_potencial_total(self):
        """Deve somar corretamente o ROI potencial de todos os alertas"""
        from database.models import AlertMetrics
        
        # Inserir alertas com valores específicos
        self.session.add(AlertMetrics(
            execution_id=1,
            file_name='guia1.xml',
            financial_impact=1000.0
        ))
        self.session.add(AlertMetrics(
            execution_id=1,
            file_name='guia2.xml',
            financial_impact=2500.50
        ))
        self.session.add(AlertMetrics(
            execution_id=1,
            file_name='guia3.xml',
            financial_impact=750.25
        ))
        self.session.commit()
        
        # Calcular total usando SQLAlchemy
        total = self.session.query(func.sum(AlertMetrics.financial_impact)).\
                filter_by(execution_id=1).scalar()
        
        self.assertEqual(total, 4250.75, "Soma deve ser 1000.0 + 2500.50 + 750.25")
    
    def test_05_timestamp_automatico(self):
        """Deve preencher timestamp automaticamente"""
        from database.models import AlertMetrics
        
        alerta = AlertMetrics(
            execution_id=1,
            file_name='test.xml',
            financial_impact=100.0
        )
        
        self.session.add(alerta)
        self.session.commit()
        
        resultado = self.session.query(AlertMetrics).first()
        
        self.assertIsNotNone(resultado.timestamp, "Timestamp deve ser preenchido automaticamente")
        self.assertIsInstance(resultado.timestamp, datetime, "Timestamp deve ser datetime")
    
    def test_06_log_alert_via_session(self):
        """Deve permitir logar alerta diretamente via sessão"""
        from database.models import AlertMetrics
        
        # Simula o que a função log_alert_metric() faria
        new_alert = AlertMetrics(
            execution_id=1,
            file_name='test.xml',
            alert_type='INTERNACAO_CURTA',
            alert_description='Teste',
            financial_impact=1500.0,
            status='POTENCIAL'
        )
        
        self.session.add(new_alert)
        self.session.commit()
        
        # Verificar que foi salvo
        resultado = self.session.query(AlertMetrics).first()
        self.assertEqual(resultado.financial_impact, 1500.0)
    
    def test_07_calcular_estatisticas(self):
        """Deve calcular estatísticas corretamente"""
        from database.models import AlertMetrics
        
        # Inserir alertas
        self.session.add(AlertMetrics(execution_id=1, file_name='t1.xml', financial_impact=1000.0))
        self.session.add(AlertMetrics(execution_id=1, file_name='t2.xml', financial_impact=2000.0))
        self.session.commit()
        
        # Calcular estatísticas (simulando get_alert_stats)
        total = self.session.query(func.count(AlertMetrics.id)).\
                filter_by(execution_id=1).scalar()
        
        roi = self.session.query(func.sum(AlertMetrics.financial_impact)).\
              filter_by(execution_id=1).scalar()
        
        self.assertEqual(total, 2)
        self.assertEqual(roi, 3000.0)


if __name__ == '__main__':
    # Rodar testes com verbosidade
    unittest.main(verbosity=2)
