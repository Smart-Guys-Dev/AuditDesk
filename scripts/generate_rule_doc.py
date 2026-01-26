"""
Gerador de Documentação de Regras - AuditPlus v2.0

Este script gera automaticamente documentação HTML para regras de negócio
seguindo o padrão definido em docs/PADROES_DOCUMENTACAO.md.

Uso:
    python scripts/generate_rule_doc.py --rule-id REGRA_TAXA_OBSERVACAO_CORRIGIR_HORARIOS
    python scripts/generate_rule_doc.py --rule-id REGRA_CPF --start-time 10:00 --end-time 11:30 --tests 5

Autor: Pedro Lucas Lima de Freitas
Data: 26/01/2026
"""

import sys
import os
import json
import argparse
from datetime import datetime

# Setup paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

# Template HTML
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Documentação de Regra: {rule_id_short}</title>
    <style>
        :root {{
            --primary-color: #00995D;
            --secondary-color: #263238;
            --bg-color: #f4f6f8;
            --card-bg: #ffffff;
            --text-color: #333;
            --border-radius: 8px;
        }}
        body {{
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 30px;
            background-color: var(--bg-color);
            color: var(--text-color);
            line-height: 1.6;
        }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        header {{
            background-color: var(--card-bg);
            padding: 25px 35px;
            border-radius: var(--border-radius);
            box-shadow: 0 2px 15px rgba(0, 0, 0, 0.04);
            margin-bottom: 30px;
            border-left: 6px solid var(--primary-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        h1 {{ color: var(--primary-color); margin: 0; font-size: 24px; font-weight: 600; }}
        .status-badge {{
            padding: 6px 14px;
            border-radius: 15px;
            font-weight: bold;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .status-implementado {{ background-color: #e8f5e9; color: #00995D; border: 1px solid #c8e6c9; }}
        .status-desenvolvimento {{ background-color: #fff3e0; color: #f57c00; border: 1px solid #ffe0b2; }}
        .status-desativado {{ background-color: #ffebee; color: #c62828; border: 1px solid #ffcdd2; }}
        .card {{
            background-color: var(--card-bg);
            border-radius: var(--border-radius);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
            padding: 30px;
            margin-bottom: 25px;
            border: 1px solid rgba(0, 0, 0, 0.02);
        }}
        h2 {{
            color: #444;
            border-bottom: 2px solid #f0f0f0;
            padding-bottom: 12px;
            margin-top: 0;
            font-size: 18px;
            font-weight: 600;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        .info-item label {{
            display: block;
            font-size: 11px;
            text-transform: uppercase;
            color: var(--primary-color);
            margin-bottom: 5px;
            font-weight: 700;
            letter-spacing: 0.5px;
            opacity: 0.9;
        }}
        .info-item span {{ font-size: 16px; color: var(--secondary-color); font-weight: 500; word-break: break-all; }}
        .info-item p {{ margin: 5px 0 0 0; font-size: 14px; }}
        .metric-cards {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }}
        .metric-card {{
            background: #fff;
            border: 1px solid #e0e0e0;
            border-radius: var(--border-radius);
            padding: 20px;
            text-align: center;
            transition: transform 0.2s;
        }}
        .metric-card:hover {{ transform: translateY(-2px); box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05); }}
        .metric-card:nth-child(1) {{ border-top: 3px solid #ff7043; }}
        .metric-card:nth-child(2) {{ border-top: 3px solid var(--primary-color); }}
        .metric-card:nth-child(3) {{ border-top: 3px solid #42a5f5; }}
        .metric-card:nth-child(4) {{ border-top: 3px solid #ab47bc; }}
        .metric-value {{ font-size: 22px; font-weight: bold; color: #333; display: block; }}
        .metric-label {{ font-size: 11px; color: #777; text-transform: uppercase; letter-spacing: 0.5px; }}
        pre {{
            background-color: #263238;
            color: #eceff1;
            padding: 20px;
            border-radius: var(--border-radius);
            overflow-x: auto;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 13px;
            line-height: 1.5;
        }}
        .json-key {{ color: #80cbc4; }}
        .json-string {{ color: #a5d6a7; }}
        .json-number {{ color: #ffab91; }}
        .json-boolean {{ color: #ce93d8; }}
        .test-case {{
            background: #fafafa;
            border-left: 4px solid var(--primary-color);
            padding: 15px;
            margin: 10px 0;
            border-radius: 0 var(--border-radius) var(--border-radius) 0;
        }}
        .test-case.passed {{ border-left-color: #4caf50; }}
        .test-case.failed {{ border-left-color: #f44336; }}
        footer {{
            text-align: center;
            font-size: 13px;
            color: #777;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
        }}
        .category-badge {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
        }}
        .cat-glosa-guia {{ background: #ffebee; color: #c62828; }}
        .cat-glosa-item {{ background: #fff3e0; color: #ef6c00; }}
        .cat-validacao {{ background: #e3f2fd; color: #1565c0; }}
        .cat-otimizacao {{ background: #f3e5f5; color: #7b1fa2; }}
        .cat-correcao {{ background: #e8f5e9; color: #2e7d32; }}
    </style>
</head>
<body>
<div class="container">
    <header>
        <h1>Relatório de Implementação de Regra</h1>
        <span class="status-badge status-{status_class}">{status}</span>
    </header>

    <div class="card">
        <h2>📋 Informações da Regra</h2>
        <div class="info-grid">
            <div class="info-item">
                <label>ID da Regra</label>
                <span>{rule_id}</span>
            </div>
            <div class="info-item">
                <label>Grupo</label>
                <span>{grupo}</span>
            </div>
            <div class="info-item">
                <label>Categoria</label>
                <span class="category-badge cat-{categoria_class}">{categoria}</span>
            </div>
            <div class="info-item">
                <label>Tipo de Ação</label>
                <span>{tipo_acao}</span>
            </div>
        </div>
        <div class="info-item">
            <label>Descrição</label>
            <p>{descricao}</p>
        </div>
    </div>

    <div class="card">
        <h2>📊 Métricas de Desenvolvimento</h2>
        <div class="metric-cards">
            <div class="metric-card">
                <span class="metric-value">{data}</span>
                <span class="metric-label">Data</span>
            </div>
            <div class="metric-card">
                <span class="metric-value">{inicio}</span>
                <span class="metric-label">Início</span>
            </div>
            <div class="metric-card">
                <span class="metric-value">{fim}</span>
                <span class="metric-label">Conclusão</span>
            </div>
            <div class="metric-card">
                <span class="metric-value">{testes}</span>
                <span class="metric-label">Testes</span>
            </div>
        </div>
    </div>

    <div class="card">
        <h2>⚙️ Configuração JSON</h2>
        <pre>{json_content}</pre>
    </div>

    <div class="card">
        <h2>📝 Detalhes da Solução</h2>
        <p>{detalhes}</p>
    </div>

    {test_cases_section}

    <footer>
        Unimed Campo Grande • {data_completa} • AuditPlus v2.0 • Documentado por: {autor}
    </footer>
</div>
</body>
</html>'''


def format_json_with_syntax_highlight(obj):
    """Formata JSON com destaque de sintaxe HTML"""
    json_str = json.dumps(obj, indent=4, ensure_ascii=False)
    
    # Simples highlighting (pode ser melhorado)
    import re
    
    # Keys
    json_str = re.sub(r'"([^"]+)":', r'<span class="json-key">"\1"</span>:', json_str)
    # Strings values (que não são keys)
    json_str = re.sub(r': "([^"]*)"', r': <span class="json-string">"\1"</span>', json_str)
    # Numbers
    json_str = re.sub(r': (\d+\.?\d*)', r': <span class="json-number">\1</span>', json_str)
    # Booleans
    json_str = re.sub(r': (true|false)', r': <span class="json-boolean">\1</span>', json_str)
    
    return json_str


def load_rule_from_json_files(config_dir, rule_id):
    """Busca uma regra nos arquivos JSON"""
    rules_config_path = os.path.join(config_dir, "rules_config.json")
    
    if not os.path.exists(rules_config_path):
        return None
    
    with open(rules_config_path, 'r', encoding='utf-8') as f:
        rules_config = json.load(f)
    
    for grupo in rules_config.get("grupos_para_carregar", []):
        arquivo = grupo.get("arquivo_regras")
        arquivo_path = os.path.join(config_dir, arquivo)
        
        if not os.path.exists(arquivo_path):
            continue
        
        with open(arquivo_path, 'r', encoding='utf-8') as f:
            regras = json.load(f)
        
        if isinstance(regras, list):
            for regra in regras:
                if regra.get("id") == rule_id:
                    regra["_grupo"] = grupo.get("nome_grupo", "Outros")
                    return regra
    
    return None


def get_category_class(categoria):
    """Retorna classe CSS para a categoria"""
    mapping = {
        "GLOSA_GUIA": "glosa-guia",
        "GLOSA_ITEM": "glosa-item",
        "VALIDACAO": "validacao",
        "OTIMIZACAO": "otimizacao",
        "CORRECAO_AUTOMATICA": "correcao",
    }
    return mapping.get(categoria, "validacao")


def generate_documentation(
    rule_id: str,
    start_time: str = None,
    end_time: str = None,
    tests_count: int = 1,
    details: str = None,
    author: str = "Pedro Lucas Lima de Freitas",
    status: str = "IMPLEMENTADO",
    test_cases: list = None
) -> str:
    """Gera documentação HTML para uma regra"""
    
    config_dir = os.path.join(project_root, "src", "config")
    
    # Carregar regra
    rule = load_rule_from_json_files(config_dir, rule_id)
    
    if not rule:
        print(f"ERRO: Regra '{rule_id}' não encontrada nos arquivos JSON.")
        return None
    
    # Extrair dados
    now = datetime.now()
    
    # Preparar valores
    rule_id_short = rule_id.replace("REGRA_", "").replace("_", " ")
    grupo = rule.get("_grupo", "Outros")
    categoria = rule.get("metadata_glosa", {}).get("categoria", "VALIDACAO")
    tipo_acao = rule.get("acao", {}).get("tipo_acao", "N/A")
    descricao = rule.get("descricao", "Sem descrição")
    
    # Métricas
    data = now.strftime("%d/%m")
    data_completa = now.strftime("%d/%m/%Y %H:%M")
    inicio = start_time or now.strftime("%H:%M")
    fim = end_time or now.strftime("%H:%M")
    testes = str(tests_count)
    
    # Status class
    status_class = "implementado"
    if "DESENVOLVIMENTO" in status.upper():
        status_class = "desenvolvimento"
    elif "DESATIV" in status.upper():
        status_class = "desativado"
    
    # JSON formatado
    json_content = format_json_with_syntax_highlight(rule)
    
    # Detalhes
    if not details:
        details = f"Regra implementada conforme especificação. Tipo de ação: {tipo_acao}."
    
    # Casos de teste (opcional)
    test_cases_section = ""
    if test_cases:
        test_cases_html = []
        for tc in test_cases:
            status_tc = "passed" if tc.get("passed", True) else "failed"
            test_cases_html.append(f'''
            <div class="test-case {status_tc}">
                <strong>Entrada:</strong> {tc.get("entrada", "N/A")}<br>
                <strong>Esperado:</strong> {tc.get("esperado", "N/A")}<br>
                <strong>Obtido:</strong> {tc.get("obtido", "N/A")}
            </div>
            ''')
        
        test_cases_section = f'''
        <div class="card">
            <h2>🧪 Casos de Teste</h2>
            {''.join(test_cases_html)}
        </div>
        '''
    
    # Gerar HTML
    html = HTML_TEMPLATE.format(
        rule_id_short=rule_id_short,
        rule_id=rule_id,
        grupo=grupo,
        categoria=categoria,
        categoria_class=get_category_class(categoria),
        tipo_acao=tipo_acao,
        descricao=descricao,
        data=data,
        data_completa=data_completa,
        inicio=inicio,
        fim=fim,
        testes=testes,
        json_content=json_content,
        detalhes=details,
        status=status,
        status_class=status_class,
        autor=author,
        test_cases_section=test_cases_section
    )
    
    return html


def main():
    parser = argparse.ArgumentParser(
        description='Gera documentação HTML para regras de negócio do AuditPlus',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Exemplos:
  python generate_rule_doc.py --rule-id REGRA_TAXA_OBSERVACAO_CORRIGIR_HORARIOS
  python generate_rule_doc.py --rule-id REGRA_CPF --start-time 10:00 --end-time 11:30 --tests 5
        '''
    )
    
    parser.add_argument('--rule-id', required=True, help='ID da regra (ex: REGRA_TAXA_OBSERVACAO_CORRIGIR_HORARIOS)')
    parser.add_argument('--start-time', help='Hora de início (HH:MM)')
    parser.add_argument('--end-time', help='Hora de conclusão (HH:MM)')
    parser.add_argument('--tests', type=int, default=1, help='Número de testes realizados')
    parser.add_argument('--details', help='Detalhes da solução (texto)')
    parser.add_argument('--author', default='Pedro Lucas Lima de Freitas', help='Nome do autor')
    parser.add_argument('--status', default='IMPLEMENTADO', choices=['IMPLEMENTADO', 'EM DESENVOLVIMENTO', 'DESATIVADO'], help='Status da regra')
    parser.add_argument('--output', help='Caminho de saída (padrão: docs/regras/[ID].html)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("GERADOR DE DOCUMENTAÇÃO DE REGRAS")
    print("=" * 60)
    print(f"Regra: {args.rule_id}")
    
    # Gerar HTML
    html = generate_documentation(
        rule_id=args.rule_id,
        start_time=args.start_time,
        end_time=args.end_time,
        tests_count=args.tests,
        details=args.details,
        author=args.author,
        status=args.status
    )
    
    if not html:
        sys.exit(1)
    
    # Determinar caminho de saída
    if args.output:
        output_path = args.output
    else:
        # Gerar nome do arquivo baseado no ID
        file_name = args.rule_id.replace("REGRA_", "") + ".html"
        output_path = os.path.join(project_root, "docs", "regras", file_name)
    
    # Garantir que o diretório existe
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Salvar arquivo
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n✅ Documentação gerada com sucesso!")
    print(f"   Arquivo: {output_path}")
    print("=" * 60)
    
    return output_path


if __name__ == "__main__":
    main()
