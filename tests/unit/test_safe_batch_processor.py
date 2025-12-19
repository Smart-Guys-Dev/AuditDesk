"""
Testes para SafeBatchProcessor - error handling robusto.
"""
import pytest
import tempfile
import os
from pathlib import Path
from lxml import etree


class TestSafeBatchProcessing:
    """Testes de processamento seguro em lote"""
    
    def test_process_file_safe_sucesso(self, rule_engine, xml_reader):
        """Testa processamento bem-sucedido de arquivo"""
        from src.business.processing.safe_batch_processor import process_file_safe
        
        # Criar arquivo temporário
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<ans:mensagemTISS xmlns:ans="http://www.ans.gov.br/padroes/tiss/schemas" xmlns:ptu="http://unimedbh.com.br/PTU">
    <ans:prestadorParaOperadora>
        <ans:loteGuias>
            <ans:guiasTISS>
                <ans:guiaSADT>
                    <ans:dadosAtendimento>
                        <ptu:tp_Atendimento>05</ptu:tp_Atendimento>
                    </ans:dadosAtendimento>
                </ans:guiaSADT>
            </ans:guiasTISS>
        </ans:loteGuias>
    </ans:prestadorParaOperadora>
</ans:mensagemTISS>"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False, encoding='utf-8') as f:
            f.write(xml_content)
            temp_file = f.name
        
        try:
            # Processar
            success, result, error = process_file_safe(temp_file, rule_engine, xml_reader)
            
            # Validar
            assert success == True
            assert result is not None
            assert error is None
            assert 'modified' in result
            assert 'tree' in result
        finally:
            os.unlink(temp_file)
    
    def test_process_file_safe_xml_invalido(self, rule_engine, xml_reader):
        """Testa handling de XML inválido"""
        from src.business.processing.safe_batch_processor import process_file_safe
        
        # XML malformado
        xml_content = "<?xml version='1.0'?><broken><tag>"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False, encoding='utf-8') as f:
            f.write(xml_content)
            temp_file = f.name
        
        try:
            # Processar
            success, result, error = process_file_safe(temp_file, rule_engine, xml_reader)
            
            # Deve falhar gracefully
            assert success == False
            assert result is None
            assert error is not None
            assert "XML inválido" in error or "Erro" in error
        finally:
            os.unlink(temp_file)
    
    def test_process_batch_multiplos_arquivos(self, rule_engine):
        """Testa processamento de lote com múltiplos arquivos"""
        from src.business.processing.safe_batch_processor import process_batch
        
        xml_bom = """<?xml version="1.0" encoding="UTF-8"?>
<ans:mensagemTISS xmlns:ans="http://www.ans.gov.br/padroes/tiss/schemas" xmlns:ptu="http://unimedbh.com.br/PTU">
    <ans:prestadorParaOperadora>
        <ans:loteGuias>
            <ans:guiasTISS>
                <ans:guiaSADT>
                    <ans:dadosAtendimento>
                        <ptu:tp_Atendimento>05</ptu:tp_Atendimento>
                    </ans:dadosAtendimento>
                </ans:guiaSADT>
            </ans:guiasTISS>
        </ans:loteGuias>
    </ans:prestadorParaOperadora>
</ans:mensagemTISS>"""
        
        xml_ruim = "<?xml version='1.0'?><broken>"
        
        # Criar 3 arquivos: 2 bons, 1 ruim
        temp_files = []
        
        try:
            # Arquivo bom 1
            with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False, encoding='utf-8') as f:
                f.write(xml_bom)
                temp_files.append(f.name)
            
            # Arquivo ruim
            with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False, encoding='utf-8') as f:
                f.write(xml_ruim)
                temp_files.append(f.name)
            
            # Arquivo bom 2
            with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False, encoding='utf-8') as f:
                f.write(xml_bom)
                temp_files.append(f.name)
            
            # Processar lote
            summary = process_batch(temp_files, rule_engine, max_errors=10)
            
            # Validações
            assert summary['total'] == 3
            assert summary['processed'] == 3  # Todos foram tentados
            assert summary['success'] >= 2  # Pelo menos os 2 bons
            assert summary['errors'] >= 1  # Pelo menos o ruim
            assert len(summary['results']) >= 2
            assert len(summary['error_details']) >= 1
            assert summary['duration'] > 0
            
            print(f"\n✅ Lote processado:")
            print(f"  Total: {summary['total']}")
            print(f"  Sucesso: {summary['success']}")
            print(f"  Erros: {summary['errors']}")
            print(f"  Tempo: {summary['duration']:.2f}s")
            
        finally:
            for f in temp_files:
                if os.path.exists(f):
                    os.unlink(f)
    
    def test_process_batch_aborta_com_muitos_erros(self, rule_engine):
        """Testa que lote aborta quando atinge limite de erros"""
        from src.business.processing.safe_batch_processor import process_batch
        
        xml_ruim = "<?xml version='1.0'?><broken>"
        
        # Criar 10 arquivos ruins
        temp_files = []
        
        try:
            for _ in range(10):
                with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False, encoding='utf-8') as f:
                    f.write(xml_ruim)
                    temp_files.append(f.name)
            
            # Processar com limite de 5 erros
            summary = process_batch(temp_files, rule_engine, max_errors=5)
            
            # Deve ter parado em 5 erros
            assert summary['errors'] == 5
            assert summary['processed'] == 5  # Processou apenas 5, não os 10
            assert summary['success'] == 0
            
            print(f"\n✅ Lote abortado corretamente após {summary['errors']} erros")
            
        finally:
            for f in temp_files:
                if os.path.exists(f):
                    os.unlink(f)
    
    @pytest.mark.slow
    def test_throughput_minimo(self, rule_engine):
        """Testa que throughput é adequado (> 1 arquivo/segundo)"""
        from src.business.processing.safe_batch_processor import process_batch
        
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<ans:mensagemTISS xmlns:ans="http://www.ans.gov.br/padroes/tiss/schemas" xmlns:ptu="http://unimedbh.com.br/PTU">
    <ans:prestadorParaOperadora>
        <ans:loteGuias>
            <ans:guiasTISS>
                <ans:guiaSADT>
                    <ans:dadosAtendimento>
                        <ptu:tp_Atendimento>05</ptu:tp_Atendimento>
                    </ans:dadosAtendimento>
                </ans:guiaSADT>
            </ans:guiasTISS>
        </ans:loteGuias>
    </ans:prestadorParaOperadora>
</ans:mensagemTISS>"""
        
        # Criar 10 arquivos
        temp_files = []
        
        try:
            for i in range(10):
                with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False, encoding='utf-8') as f:
                    f.write(xml_content)
                    temp_files.append(f.name)
            
            # Processar
            summary = process_batch(temp_files, rule_engine)
            
            # Validar performance
            assert summary['throughput'] > 1.0, f"Throughput muito baixo: {summary['throughput']:.2f} arquivos/s"
            
            print(f"\n⚡ Performance:")
            print(f"  10 arquivos em {summary['duration']:.2f}s")
            print(f"  Throughput: {summary['throughput']:.1f} arquivos/s")
            print(f"  Projeção: ~{summary['throughput']*3600:.0f} arquivos/hora")
            
        finally:
            for f in temp_files:
                if os.path.exists(f):
                    os.unlink(f)
