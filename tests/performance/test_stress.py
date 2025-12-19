"""
Stress tests para validar performance em escala.

Testa processamento de 100, 500, 1000 guias.
Meta: > 500 guias/hora, < 4GB RAM
"""
import pytest
import time
import psutil
import os
from pathlib import Path

# Importar gerador
import sys
sys.path.insert(0, str(Path(__file__).parent))
from generate_test_xmls import generate_test_batch


def get_memory_usage_mb():
    """Retorna uso de memória em MB"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024


@pytest.mark.slow
@pytest.mark.skipif(not os.getenv('RUN_STRESS_TESTS'), reason="Stress tests desabilitados por padrão")
class TestStressPerformance:
    """Testes de stress e performance"""
    
    def test_100_guias_benchmark(self, rule_engine, tmp_path):
        """
        Processa 100 guias e mede performance baseline.
        
        Meta: < 3 minutos (33 guias/min = 2000/hora)
        """
        from src.business.processing.safe_batch_processor import process_batch
        
        # Gerar XMLs
        print("\n🔧 Gerando 100 XMLs...")
        files = generate_test_batch(
            count=100,
            output_dir=str(tmp_path / "batch_100"),
            error_rate=0.0
        )
        
        # Medir memória inicial
        mem_start = get_memory_usage_mb()
        
        # Processar
        print("\n🚀 Processando lote...")
        start = time.time()
        summary = process_batch(files, rule_engine)
        duration = time.time() - start
        
        # Medir memória final
        mem_end = get_memory_usage_mb()
        mem_delta = mem_end - mem_start
        
        # Métricas
        throughput_per_hour = (summary['success'] / duration) * 3600
        
        # Relatório
        print(f"\n📊 RESULTADOS - 100 Guias:")
        print(f"  ✅ Sucesso: {summary['success']}/{summary['total']}")
        print(f"  ⏱️  Tempo: {duration:.1f}s ({duration/60:.1f} min)")
        print(f"  ⚡ Throughput: {summary['throughput']:.1f} guias/s")
        print(f"  ⚡ Projeção: {throughput_per_hour:.0f} guias/hora")
        print(f"  💾 Memória: {mem_start:.0f} MB → {mem_end:.0f} MB (Δ{mem_delta:+.0f} MB)")
        
        # Asserções
        assert duration < 180, f"100 guias demoraram {duration:.1f}s (limite: 180s)"
        assert summary['success'] >= 95, f"Taxa de sucesso baixa: {summary['success']}/100"
        assert mem_end < 2048, f"Uso de memória alto: {mem_end:.0f} MB (limite: 2GB)"
    
    def test_500_guias_stress(self, rule_engine, tmp_path):
        """
        Stress test com 500 guias.
        
        Meta: < 15 minutos, < 3GB RAM
        """
        from src.business.processing.safe_batch_processor import process_batch
        
        # Gerar XMLs
        print("\n🔧 Gerando 500 XMLs...")
        files = generate_test_batch(
            count=500,
            output_dir=str(tmp_path / "batch_500"),
            error_rate=0.05  # 5% com erros
        )
        
        mem_start = get_memory_usage_mb()
        
        # Processar
        print("\n🚀 Processando lote de 500...")
        start = time.time()
        summary = process_batch(files, rule_engine)
        duration = time.time() - start
        
        mem_end = get_memory_usage_mb()
        mem_delta = mem_end - mem_start
        throughput_per_hour = (summary['success'] / duration) * 3600
        
        # Relatório
        print(f"\n📊 RESULTADOS - 500 Guias:")
        print(f"  ✅ Sucesso: {summary['success']}/{summary['total']}")
        print(f"  ❌ Erros: {summary['errors']}")
        print(f"  ⏱️  Tempo: {duration:.1f}s ({duration/60:.1f} min)")
        print(f"  ⚡ Throughput: {summary['throughput']:.1f} guias/s")
        print(f"  ⚡ Projeção: {throughput_per_hour:.0f} guias/hora")
        print(f"  💾 Memória: {mem_start:.0f} MB → {mem_end:.0f} MB (Δ{mem_delta:+.0f} MB)")
        
        # Asserções
        assert duration < 900, f"500 guias demoraram {duration/60:.1f}min (limite: 15min)"
        assert summary['success'] >= 450, f"Muitos erros: {summary['errors']}"
        assert mem_end < 3072, f"Memória alta: {mem_end:.0f} MB (limite: 3GB)"
        assert throughput_per_hour > 500, f"Throughput baixo: {throughput_per_hour:.0f}/hora"
    
    def test_1000_guias_full_stress(self, rule_engine, tmp_path):
        """
        Stress test completo com 1000 guias.
        
        Meta: < 30 minutos, < 4GB RAM, > 500 guias/hora
        """
        from src.business.processing.safe_batch_processor import process_batch
        
        # Gerar XMLs
        print("\n🔧 Gerando 1000 XMLs...")
        files = generate_test_batch(
            count=1000,
            output_dir=str(tmp_path / "batch_1000"),
            error_rate=0.10  # 10% com erros
        )
        
        mem_start = get_memory_usage_mb()
        print(f"💾 Memória inicial: {mem_start:.0f} MB")
        
        # Processar
        print("\n🚀 Processando lote de 1000 guias...")
        print("   (Isso pode demorar alguns minutos...)")
        start = time.time()
        summary = process_batch(files, rule_engine, max_errors=200)
        duration = time.time() - start
        
        mem_end = get_memory_usage_mb()
        mem_delta = mem_end - mem_start
        throughput_per_hour = (summary['success'] / duration) * 3600
        
        # Relatório completo
        print(f"\n" + "="*60)
        print(f"📊 RESULTADOS FINAIS - 1000 Guias STRESS TEST")
        print(f"="*60)
        print(f"  📄 Total de arquivos: {summary['total']}")
        print(f"  ✅ Processados com sucesso: {summary['success']} ({summary['success']/summary['total']*100:.1f}%)")
        print(f"  ❌ Erros: {summary['errors']} ({summary['errors']/summary['total']*100:.1f}%)")
        print(f"  ⏱️  Tempo total: {duration:.1f}s ({duration/60:.1f} min)")
        print(f"  ⚡ Throughput médio: {summary['throughput']:.2f} guias/segundo")
        print(f"  ⚡ Projeção horária: {throughput_per_hour:.0f} guias/hora")
        print(f"  💾 Memória inicial: {mem_start:.0f} MB")
        print(f"  💾 Memória final: {mem_end:.0f} MB")
        print(f"  💾 Delta memória: {mem_delta:+.0f} MB")
        print(f"="*60)
        
        # Asserções críticas
        assert duration < 1800, f"1000 guias demoraram {duration/60:.1f}min (limite: 30min)"
        assert summary['success'] >= 850, f"Taxa de sucesso muito baixa: {summary['success']}/1000"
        assert mem_end < 4096, f"Uso de memória excessivo: {mem_end:.0f} MB (limite: 4GB)"
        assert throughput_per_hour > 500, f"Throughput insuficiente: {throughput_per_hour:.0f}/hora (meta: >500)"
        
        # Validações adicionais
        assert mem_delta < 2048, f"Memory leak possível: Δ{mem_delta:.0f} MB"
        
        print("\n✅ STRESS TEST PASSOU EM TODOS OS CRITÉRIOS!")


@pytest.mark.slow
class TestMemoryStability:
    """Testes de estabilidade de memória"""
    
    def test_no_memory_leak_repetido(self, rule_engine, tmp_path):
        """
        Testa que não há memory leak processando múltiplos lotes.
        
        Processa 3 lotes de 50 guias e verifica memória estável.
        """
        from src.business.processing.safe_batch_processor import process_batch
        
        mem_samples = []
        
        for batch_num in range(3):
            # Gerar novo lote
            files = generate_test_batch(
                count=50,
                output_dir=str(tmp_path / f"batch_{batch_num}"),
                prefix=f"batch{batch_num}"
            )
            
            # Processar
            summary = process_batch(files, rule_engine)
            
            # Medir memória
            mem_current = get_memory_usage_mb()
            mem_samples.append(mem_current)
            
            print(f"\n  Lote {batch_num+1}: {mem_current:.0f} MB")
        
        # Verificar que memória não cresce descontroladamente
        mem_growth = mem_samples[-1] - mem_samples[0]
        print(f"\n💾 Crescimento de memória: {mem_growth:+.0f} MB")
        
        # Memória não deve crescer mais que 500MB após 3 lotes
        assert mem_growth < 500, f"Possível memory leak: +{mem_growth:.0f} MB"
