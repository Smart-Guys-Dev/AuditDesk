# -*- coding: utf-8 -*-
"""
Script para auditar conformidade das regras com estruturas PTU.
Verifica se os xpaths estão corretos baseado no tipo_elemento.
"""
import json
import os

# Estrutura PTU aprendida
# - cd_Excecao está em dadosGuia (NOT em procedimentosExecutados)
# - equipe_Profissional está dentro de procedimentosExecutados (honorários)
# - procedimentos está dentro de procedimentosExecutados (SADT, Internação, Honorários)
# - procedimentos está direto em dadosGuia (Consulta)

# Elementos e seus filhos válidos
ESTRUTURA_PTU = {
    "procedimentosExecutados": [
        "dt_Execucao", "hr_Inicial", "hr_Final", "procedimentos",
        "valores", "taxas", "equipe_Profissional", "dadosAutorizacao",
        "id_Acrescimo", "via_Acesso", "tc_Utilizada", "un_Medida",
        "ft_MultiplicadorServico", "id_AvisadoItem", "id_Pacote", "cd_Ato"
    ],
    "procedimentos": [
        "seq_item", "id_itemUnico", "tp_Tabela", "cd_Servico", "ds_Servico",
        "qt_Cobrada", "vl_ServCobrado", "tx_AdmServico", "cd_Ato"
    ],
    "dadosGuia": [
        "nr_Ver_TISS", "nr_LotePrestador", "dt_Protocolo", "dt_Conhecimento",
        "nr_Guias", "id_Liminar", "id_Continuado", "id_Avisado",
        "cd_Excecao", "id_GlosaTotal", "procedimentosExecutados", "procedimentos",
        "dt_UltimaAutorizacao", "complemento", "dadosAutorizacao", "tp_Consulta"
    ],
    "dadosSolicitante": [
        "contratadoSolicitante", "profissional"
    ],
    "profissional": [
        "nm_Profissional", "dadosConselho", "CBO"
    ],
    "dadosExecutante": [
        "UnimedPrestador", "nome", "CPF_CNPJ", "cd_cnpj", "CNES", "prestador"
    ],
    "dadosAuditoria": [
        "nm_MedicoAuditor", "nr_CrmAuditor", "cd_UFCRM",
        "nm_EnfAuditor", "nr_CorenAuditor", "cd_UFCoren"
    ],
    "dadosInternacao": [
        "tp_Acomodacao", "ft_Multiplicador_AMB", "tp_Internacao",
        "rg_Internacao", "caraterAtendimento", "dadosFaturamento"
    ],
    "equipe_Profissional": [
        "tp_Participacao", "Prestador", "nm_Profissional", "cdCnpjCpf",
        "dadosConselho", "CBO"
    ]
}

# Campos que NÃO estão em procedimentosExecutados (estão no pai - dadosGuia)
CAMPOS_EM_DADOS_GUIA = ["cd_Excecao", "id_GlosaTotal", "id_Liminar", "id_Continuado", "id_Avisado"]

def analisar_regra(regra, arquivo):
    """Analisa uma regra e retorna problemas encontrados."""
    problemas = []
    regra_id = regra.get("id", "SEM_ID")
    
    condicoes = regra.get("condicoes", {})
    tipo_elemento = condicoes.get("tipo_elemento", "")
    
    # Verificar xpaths nas condições
    def verificar_xpath(xpath, contexto):
        if not xpath:
            return
        
        # Se tipo_elemento é procedimentosExecutados e xpath busca cd_Excecao diretamente
        if tipo_elemento == "procedimentosExecutados":
            if "./ptu:cd_Excecao" in xpath and "../ptu:cd_Excecao" not in xpath:
                problemas.append(f"[{regra_id}] ERRO: cd_Excecao buscado com './' em procedimentosExecutados. Deveria usar '../' pois cd_Excecao está em dadosGuia.")
    
    # Buscar xpaths nas condições
    def extrair_xpaths(obj, contexto=""):
        if isinstance(obj, dict):
            if "xpath" in obj:
                verificar_xpath(obj["xpath"], contexto)
            if "tag_alvo" in obj:
                verificar_xpath(obj["tag_alvo"], contexto)
            for k, v in obj.items():
                extrair_xpaths(v, contexto + "." + k)
        elif isinstance(obj, list):
            for item in obj:
                extrair_xpaths(item, contexto)
    
    extrair_xpaths(condicoes, "condicoes")
    
    # Verificar ação
    acao = regra.get("acao", {})
    extrair_xpaths(acao, "acao")
    
    return problemas

def main():
    regras_dir = os.path.join("src", "config", "regras")
    
    todos_problemas = []
    total_regras = 0
    regras_ok = 0
    
    print("=" * 70)
    print("AUDITORIA DE CONFORMIDADE DAS REGRAS PTU")
    print("=" * 70)
    
    for arquivo in sorted(os.listdir(regras_dir)):
        if not arquivo.endswith(".json"):
            continue
        
        caminho = os.path.join(regras_dir, arquivo)
        
        try:
            with open(caminho, 'r', encoding='utf-8') as f:
                regras = json.load(f)
        except Exception as e:
            print(f"\n[ERRO] Falha ao ler {arquivo}: {e}")
            continue
        
        if not isinstance(regras, list):
            continue
        
        print(f"\n--- {arquivo} ({len(regras)} regras) ---")
        
        problemas_arquivo = []
        for regra in regras:
            total_regras += 1
            probs = analisar_regra(regra, arquivo)
            if probs:
                problemas_arquivo.extend(probs)
            else:
                regras_ok += 1
        
        if problemas_arquivo:
            for p in problemas_arquivo:
                print(f"  ⚠️  {p}")
            todos_problemas.extend(problemas_arquivo)
        else:
            print(f"  ✅ Todas as regras OK")
    
    print("\n" + "=" * 70)
    print("RESUMO")
    print("=" * 70)
    print(f"Total de regras analisadas: {total_regras}")
    print(f"Regras OK: {regras_ok}")
    print(f"Problemas encontrados: {len(todos_problemas)}")
    
    if todos_problemas:
        print("\n⚠️  ATENÇÃO: Existem regras com xpaths potencialmente incorretos!")
    else:
        print("\n✅ TODAS AS REGRAS ESTÃO EM CONFORMIDADE!")

if __name__ == "__main__":
    main()
