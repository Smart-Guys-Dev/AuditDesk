"""
Gerador de XMLs de teste para stress testing.

Cria lotes de XMLs SADT válidos para testes de performance.
"""
import os
from pathlib import Path
from lxml import etree


def generate_sadt_xml(index: int, with_errors: bool = False) -> str:
    """
    Gera um XML de guia SADT.
    
    Args:
        index: Número sequencial da guia
        with_errors: Se True, gera XML com erros intencionais
        
    Returns:
        String do XML completo
    """
    # tp_Atendimento incorreto se with_errors
    tp_atend = "05" if with_errors else "23"
    
    # Código de procedimento varia
    cod_proc = f"3100{(index % 9000) + 1000:04d}"
    
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<ans:mensagemTISS xmlns:ans="http://www.ans.gov.br/padroes/tiss/schemas" xmlns:ptu="http://unimedbh.com.br/PTU">
    <ans:cabecalho>
        <ans:identificacaoTransacao>
            <ans:tipoTransacao>ENVIO_LOTE_GUIAS</ans:tipoTransacao>
            <ans:sequencialTransacao>{index}</ans:sequencialTransacao>
        </ans:identificacaoTransacao>
    </ans:cabecalho>
    <ans:prestadorParaOperadora>
        <ans:loteGuias>
            <ans:numeroLote>{index // 100 + 1}</ans:numeroLote>
            <ans:guiasTISS>
                <ans:guiaSADT>
                    <ans:cabecalhoGuia>
                        <ans:registroANS>123456</ans:registroANS>
                    </ans:cabecalhoGuia>
                    <ans:dadosAutorizacao>
                        <ans:numeroGuiaPrestador>{index:08d}</ans:numeroGuiaPrestador>
                    </ans:dadosAutorizacao>
                    <ans:dadosAtendimento>
                        <ptu:tp_Atendimento>{tp_atend}</ptu:tp_Atendimento>
                        <ptu:tpCaraterAtend>01</ptu:tpCaraterAtend>
                    </ans:dadosAtendimento>
                    <ans:dadosSolicitante>
                        <ans:contratadoSolicitante>
                            <ans:codigoPrestadorNaOperadora>123</ans:codigoPrestadorNaOperadora>
                        </ans:contratadoSolicitante>
                    </ans:dadosSolicitante>
                    <ans:dadosExecutante>
                        <ans:contratadoExecutante>
                            <ans:codigoPrestadorNaOperadora>456</ans:codigoPrestadorNaOperadora>
                            <ans:CNES>1234567</ans:CNES>
                        </ans:contratadoExecutante>
                    </ans:dadosExecutante>
                    <ans:procedimentosExecutados>
                        <ans:procedimentoExecutado>
                            <ans:sequencialItem>1</ans:sequencialItem>
                            <ans:procedimento>
                                <ans:codigoTabela>22</ans:codigoTabela>
                                <ans:codigoProcedimento>{cod_proc}</ans:codigoProcedimento>
                            </ans:procedimento>
                            <ans:quantidadeExecutada>1</ans:quantidadeExecutada>
                            <ans:valorUnitario>{100 + (index % 900)}.00</ans:valorUnitario>
                            <ans:valorTotal>{100 + (index % 900)}.00</ans:valorTotal>
                        </ans:procedimentoExecutado>
                    </ans:procedimentosExecutados>
                </ans:guiaSADT>
            </ans:guiasTISS>
        </ans:loteGuias>
    </ans:prestadorParaOperadora>
</ans:mensagemTISS>"""
    
    return xml


def generate_test_batch(
    count: int,
    output_dir: str,
    error_rate: float = 0.0,
    prefix: str = "sadt"
) -> list:
    """
    Gera um lote de XMLs de teste.
    
    Args:
        count: Número de XMLs a gerar
        output_dir: Diretório de saída
        error_rate: Taxa de XMLs com erros (0.0 a 1.0)
        prefix: Prefixo dos arquivos
        
    Returns:
        Lista de caminhos dos arquivos criados
    """
    # Criar diretório se não existe
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    files_created = []
    errors_to_create = int(count * error_rate)
    
    print(f"🔧 Gerando {count} XMLs...")
    print(f"  📁 Diretório: {output_dir}")
    print(f"  ✅ XMLs corretos: {count - errors_to_create}")
    print(f"  ❌ XMLs com erros: {errors_to_create}")
    
    for i in range(count):
        # Primeiros 'errors_to_create' com erro
        with_errors = i < errors_to_create
        
        xml_content = generate_sadt_xml(i + 1, with_errors=with_errors)
        filename = f"{prefix}_{i+1:05d}.xml"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        files_created.append(filepath)
        
        # Progresso
        if (i + 1) % 100 == 0:
            print(f"  ⏳ {i+1}/{count} XMLs gerados...")
    
    print(f"✅ {count} XMLs gerados com sucesso!")
    return files_created


def main():
    """Menu interativo para geração de lotes"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Gera XMLs de teste para stress testing')
    parser.add_argument('--count', type=int, default=100, help='Número de XMLs (padrão: 100)')
    parser.add_argument('--output', type=str, default='tests/fixtures/performance', 
                       help='Diretório de saída')
    parser.add_argument('--errors', type=float, default=0.0, 
                       help='Taxa de erros 0.0-1.0 (padrão: 0.0)')
    parser.add_argument('--prefix', type=str, default='sadt', help='Prefixo dos arquivos')
    
    args = parser.parse_args()
    
    files = generate_test_batch(
        count=args.count,
        output_dir=args.output,
        error_rate=args.errors,
        prefix=args.prefix
    )
    
    print(f"\n📊 Resumo:")
    print(f"  Total de arquivos: {len(files)}")
    print(f"  Primeiro arquivo: {files[0]}")
    print(f"  Último arquivo: {files[-1]}")
    print(f"  Tamanho médio: ~{len(generate_sadt_xml(1))} bytes")


if __name__ == "__main__":
    main()
