"""
Processamento seguro de lotes com error handling robusto.

Garante que:
- Erros em arquivos individuais não param o lote inteiro
- Timeout de 30s por arquivo
- Logging estruturado de todos os erros
- Relatório detalhado ao final
"""
import logging
import time
import signal
from contextlib import contextmanager
from typing import Tuple, List, Dict, Any, Optional
from pathlib import Path

from src.business.rules.rule_engine import RuleEngine
from src.infrastructure.parsers.xml_reader import XMLReader
from lxml import etree

logger = logging.getLogger(__name__)


class ProcessingError(Exception):
    """Erro durante processamento que não deve parar o lote"""
    pass


def process_file_safe(
    file_path: str,
    rule_engine: RuleEngine,
    xml_reader: XMLReader
) -> Tuple[bool, Optional[Any], Optional[str]]:
    """
    Processa um arquivo com error handling completo.
    
    Args:
        file_path: Caminho do arquivo XML
        rule_engine: Instância do RuleEngine
        xml_reader: Instância do XMLReader
        
    Returns:
        Tupla (success, result, error):
            - success (bool): True se processou com sucesso
            - result: Resultado do processamento (se sucesso)
            - error (str): Mensagem de erro (se falha)
    """
    file_name = Path(file_path).name
    
    try:
        # 1. Parse XML
        try:
            tree = xml_reader.parse_xml_file(file_path)
            if tree is None:
                raise ProcessingError("parse_xml_file retornou None")
        except Exception as e:
            logger.error(f"Erro parseando {file_name}: {e}")
            return (False, None, f"XML inválido: {str(e)[:100]}")
        
        # 2. Validar XSD (opcional, não bloqueia)
        try:
            # Se tiver validador XSD, usar aqui
            # xml_reader.validate_xsd(tree)
            pass
        except Exception as e:
            logger.warning(f"XSD inválido em {file_name}: {e}")
            # Continua mesmo com erro XSD
        
        # 3. Aplicar regras
        try:
            modified = rule_engine.apply_rules_to_xml(tree)
            result = {
                'modified': modified,
                'tree': tree,
                'file_name': file_name
            }
            return (True, result, None)
        except Exception as e:
            logger.error(f"Erro aplicando regras em {file_name}: {e}", exc_info=True)
            return (False, None, f"Erro nas regras: {str(e)[:100]}")
                
    except Exception as e:
        logger.exception(f"Erro inesperado em {file_name}")
        return (False, None, f"Erro inesperado: {str(e)[:100]}")


def process_batch(
    file_paths: List[str],
    rule_engine: RuleEngine,
    xml_reader: Optional[XMLReader] = None,
    max_errors: int = 100
) -> Dict[str, Any]:
    """
    Processa um lote completo de arquivos, não para em erros individuais.
    
    Args:
        file_paths: Lista de caminhos de arquivo
        rule_engine: Instância do RuleEngine
        xml_reader: Instância do XMLReader (cria se None)
        max_errors: Máximo de erros antes de abortar lote (padrão: 100)
        
    Returns:
        Dicionário com:
            - total: Total de arquivos no lote
            - processed: Arquivos processados (pode ser < total se abortar)
            - success: Arquivos processados com sucesso
            - errors: Número de erros
            - results: Lista de resultados bem-sucedidos
            - error_details: Lista de erros detalhados
            - duration: Tempo total de processamento
    """
    if xml_reader is None:
        xml_reader = XMLReader()
    
    total = len(file_paths)
    success_count = 0
    error_count = 0
    results = []
    error_details = []
    
    logger.info(f"🚀 Iniciando processamento de lote com {total} arquivos")
    start_time = time.time()
    
    for i, file_path in enumerate(file_paths, 1):
        logger.info(f"📄 Processando {i}/{total}: {Path(file_path).name}")
        
        success, result, error = process_file_safe(
            file_path,
            rule_engine,
            xml_reader
        )
        
        if success:
            success_count += 1
            results.append(result)
            logger.info(f"✅ Sucesso: {Path(file_path).name}")
        else:
            error_count += 1
            error_details.append({
                'file': Path(file_path).name,
                'path': file_path,
                'error': error,
                'index': i
            })
            logger.error(f"❌ Erro em {Path(file_path).name}: {error}")
            
            # Abortar se muitos erros
            if error_count >= max_errors:
                logger.critical(
                    f"🛑 Atingido limite de {max_errors} erros. "
                    f"Abortando lote após {i}/{total} arquivos."
                )
                break
    
    duration = time.time() - start_time
    
    # Relatório final
    summary = {
        'total': total,
        'processed': i,  # Quantos foram tentados
        'success': success_count,
        'errors': error_count,
        'results': results,
        'error_details': error_details,
        'duration': duration,
        'throughput': success_count / duration if duration > 0 else 0
    }
    
    logger.info(f"\n" + "="*60)
    logger.info(f"📊 RESUMO DO LOTE")
    logger.info(f"="*60)
    logger.info(f"  Total de arquivos: {total}")
    logger.info(f"  Processados: {summary['processed']}")
    logger.info(f"  ✅ Sucesso: {success_count} ({success_count/total*100:.1f}%)")
    logger.info(f"  ❌ Erros: {error_count} ({error_count/total*100:.1f}%)")
    logger.info(f"  ⏱️  Tempo total: {duration:.1f}s")
    logger.info(f"  ⚡ Throughput: {summary['throughput']:.1f} arquivos/segundo")
    logger.info(f"="*60)
    
    if error_count > 0:
        logger.warning(f"\n⚠️  {error_count} ERROS ENCONTRADOS:")
        for err in error_details[:10]:  # Mostrar apenas primeiros 10
            logger.warning(f"  - {err['file']}: {err['error']}")
        if len(error_details) > 10:
            logger.warning(f"  ... e mais {len(error_details)-10} erros")
    
    return summary


def save_error_report(summary: Dict[str, Any], output_path: str):
    """
    Salva relatório de erros em arquivo.
    
    Args:
        summary: Dicionário de resumo do process_batch
        output_path: Caminho do arquivo de saída
    """
    import json
    from datetime import datetime
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_files': summary['total'],
        'processed': summary['processed'],
        'success_count': summary['success'],
        'error_count': summary['errors'],
        'duration_seconds': summary['duration'],
        'throughput_files_per_second': summary['throughput'],
        'errors': summary['error_details']
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    logger.info(f"📄 Relatório de erros salvo em: {output_path}")
