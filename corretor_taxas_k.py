import os
import random
from datetime import datetime, timedelta
from lxml import etree
import shutil

CAMINHO_ENTRADA = r"c:\Users\pedro.freitas\OneDrive - UNIMEDCG\AuditPlusv2.0\taxas_complementares_k"
CAMINHO_SAIDA = os.path.join(CAMINHO_ENTRADA, "corrigidos")
NAMESPACES = {'ptu': 'http://ptu.unimed.coop.br/schemas/V3_0'}

SINTOMAS = [
    "DOR ABDOMINAL", "FEBRE PERSISTENTE", "CEFALEIA TENSIONAL", 
    "NAUSEAS E VOMITOS", "DOR TORACICA ATIPICA", "TOSSE SECA",
    "DISPNEIA LEVE", "LOMBALGIA AGUDA", "VERTIGEM", "REFLEXO GASTROESOFAGICO"
]

TXT_JUSTIFICATIVA = "INFORMO QUE OS ITENS EM QUESTAO TRATAM-SE DE UMA COBRANCA COMPLEMENTAR DEVIDO A ERROS DE VALORIZACAO NA FATURA ORIGINAL."

# Garantir pasta de saída
os.makedirs(CAMINHO_SAIDA, exist_ok=True)

CODIGO_ALVO = '60033681'
HORARIOS_PARA_TROCAR = ['07:00:00', '08:00:00', '00:00:00']
NOVOS_HORARIOS = ['08:00:00', '09:00:00', '10:00:00', '11:00:00', '13:00:00', '14:00:00', '15:00:00', '16:00:00', '17:00:00', '18:00:00']

# Mapeia nomes de arquivos processados para evitar reprocessar a mesma coisa se rodar várias vezes
# (Opcional, mas bom para garantir)

def parse_time(time_str):
    try:
        return datetime.strptime(time_str, "%H:%M:%S")
    except ValueError:
        return None

def format_time(dt_obj):
    return dt_obj.strftime("%H:%M:%S")

def calcular_horario(hr_ini_str, duracao_horas):
    dt_ini = parse_time(hr_ini_str)
    if not dt_ini:
        return None, None
    
    dt_fim = dt_ini + timedelta(hours=duracao_horas)
    return format_time(dt_ini), format_time(dt_fim)

def criar_bloco_complemento(parent, tipo, texto, indentacao_base="\n\t\t\t", step_indent=None):
    # indentacao_base: o que vem antes da tag <ptu:complemento>
    # indent_children: o que vem antes das tags filhas
    
    # Se step_indent não foi passado, tenta adivinhar
    if step_indent is None:
        step_indent = "\t" # Padrão
        if "\t" not in indentacao_base and " " in indentacao_base:
            step_indent = "    "
    
    indent_children = indentacao_base + step_indent
    
    comp = etree.Element(f"{{{NAMESPACES['ptu']}}}complemento")
    comp.text = indent_children
    
    tp_reg = etree.SubElement(comp, f"{{{NAMESPACES['ptu']}}}tp_RegCPL")
    tp_reg.text = str(tipo)
    tp_reg.tail = indent_children
    
    desc = etree.SubElement(comp, f"{{{NAMESPACES['ptu']}}}nm_DescComplemento")
    desc.text = texto
    desc.tail = indentacao_base 
    
    return comp

def processar_arquivo(arquivo):
    path_in = os.path.join(CAMINHO_ENTRADA, arquivo)
    
    try:
        parser = etree.XMLParser(remove_blank_text=False)
        tree = etree.parse(path_in, parser)
        root = tree.getroot()
    except Exception as e:
        print(f"Erro ao ler {arquivo}: {e}")
        return

    # Busca recursiva por guiaSADT
    # O lxml precisa do namespace map correto
    guias_sadt = root.findall(f"{{{NAMESPACES['ptu']}}}guiaSADT")
    if not guias_sadt:
         # Tenta XPath se findall falhar (as vezes root ja é guiaSADT ou estrutura difere)
         guias_sadt = root.xpath('//ptu:guiaSADT', namespaces=NAMESPACES)

    modificado_arquivo = False
    
    print(f"Analisando: {arquivo}")
    
    for guia in guias_sadt:
        # 0. LIMPEZA GLOBAL: Remove complementos na raiz da guia (local incorreto)
        comps_errados = guia.findall(f"{{{NAMESPACES['ptu']}}}complemento")
        if comps_errados:
            for c in comps_errados:
                guia.remove(c)
            modificado_arquivo = True

        # 1. Verifica Exceção K
        excecao = guia.xpath('.//ptu:cd_Excecao/text()', namespaces=NAMESPACES)
        if not (excecao and excecao[0].strip().upper() == 'K'):
            continue
        
        # 2. Verifica Procedimentos alvo
        procs = guia.xpath(f'.//ptu:cd_Servico[text()="{CODIGO_ALVO}"]', namespaces=NAMESPACES)
        if not procs:
            continue
            
        guia_alvo = True
            
        # 3. Ajuste de Horários
        # (Lógica existente de horários mantida simplificada aqui pois foco é complemento)
        # Para cada procedimento encontrado...
        for proc_cd in procs:
            proc_node = proc_cd.getparent()
            exec_node = proc_node.getparent() # procedimentosExecutados
            
            hr_ini_node = exec_node.findall(f"{{{NAMESPACES['ptu']}}}hr_Inicial")
            hr_fim_node = exec_node.findall(f"{{{NAMESPACES['ptu']}}}hr_Final")
            
            if not (hr_ini_node and hr_fim_node):
                continue
                
            h_ini = hr_ini_node[0].text
            h_fim = hr_fim_node[0].text
            novo_ini, novo_fim = None, None
            tipo_correcao = ""
            
            if h_ini in HORARIOS_PARA_TROCAR or h_ini == h_fim:
                novo_ini, novo_fim = calcular_horario(random.choice(NOVOS_HORARIOS), 6)
                tipo_correcao = f"FIXO/ZERADO->RANDOM (Orig: {h_ini})"
            elif h_ini == "07:00:00":
                 if random.random() < 0.5:
                     novo_ini, novo_fim = calcular_horario(random.choice(NOVOS_HORARIOS), 6)
                     tipo_correcao = "07:00->RANDOM"
                 else:
                     tipo_correcao = "MANTIDO"
                     
            if novo_ini and novo_fim:
                hr_ini_node[0].text = novo_ini
                hr_fim_node[0].text = novo_fim
                modificado_arquivo = True
                print(f"  [CORRIGIDO] Guia Exceção K | Item {CODIGO_ALVO} -> {novo_ini} - {novo_fim} ({tipo_correcao})")

        # 5. Injeção de Complementos
        if guia_alvo:
            dados_guia = guia.find(f"{{{NAMESPACES['ptu']}}}dadosGuia")
            if dados_guia is None:
                print("    [ERRO] dadosGuia não encontrado.")
                continue

            # LÓGICA DE INDENTAÇÃO CORRIGIDA (PAI vs FILHO) - RELATIVA COMPLEXA
            # Tenta descobrir indentação interna (para irmãos) e externa (para fechar)
            indent_filho_ref = "\n\t\t\t" # Default nivel 3
            indent_fechamento = "\n\t\t" # Default nivel 2
            
            last_child = None
            if len(dados_guia) > 0:
                last_child = dados_guia[-1]
                
                # 1. Indentação de fechamento (tail do último elemento)
                if last_child.tail and '\n' in last_child.tail:
                    indent_fechamento = last_child.tail.replace('\r', '')
                
                # 2. Tenta descobrir a indentação dos IRMÃOS (Sibling Indent)
                # Se houver mais de 1 filho, pegamos o tail do penúltimo
                sibling_indent = None
                if len(dados_guia) > 1:
                    penult = dados_guia[-2]
                    if penult.tail and '\n' in penult.tail:
                        sibling_indent = penult.tail.replace('\r', '')
                elif dados_guia.text and '\n' in dados_guia.text:
                    # Se só tem 1 filho, pegamos o text do pai
                    sibling_indent = dados_guia.text.replace('\r', '')
                
                # 3. Calcula o "Degrau" (Step)
                add_indent = "\t" # Default
                
                if sibling_indent is not None:
                     # Se conseguimos medir a indentação do irmão...
                     # E ela for IGUAL à de fechamento (ex: ambos são só \n)
                     # Entao o arquivo é PLANO (Flat).
                     if sibling_indent == indent_fechamento:
                         add_indent = ""
                     else:
                         # Se forem diferentes, tentamos respeitar o padrão do fechamento
                         if " " in indent_fechamento and "\t" not in indent_fechamento:
                             add_indent = "    "
                else:
                    # Se não conseguimos medir irmão, usamos heurística baseada no fechamento
                    if " " in indent_fechamento and "\t" not in indent_fechamento:
                        add_indent = "    "
                    # Se fechamento é só \n (nivel 0), assumimos que filhos são nivel 1 (\t)
                    # A menos que o arquivo seja todo plano. Mas sem siblings para comparar, difícil saber.
                    # Mas se fechamento é \n, sibling seria \n\t? Ou \n?
                    # Vamos assumir que se fechamento é \n, pode ser plano. 
                    # Mas por segurança, indented é melhor que flat se incerto.
                    pass
                
                indent_filho = indent_fechamento + add_indent

            else:
                 # Se vazio
                 if dados_guia.text and '\n' in dados_guia.text:
                     indent_filho = dados_guia.text.replace('\r', '')
                     # Deduz fechamento
                     indent_fechamento = indent_filho.replace('\t', '', 1).replace('    ', '', 1)

            # Verifica duplicidade no lugar certo (dadosGuia)
            complementos_existentes = dados_guia.findall(f"{{{NAMESPACES['ptu']}}}complemento")
            tipos_existentes = []
            for c in complementos_existentes:
                 tp = c.find(f"{{{NAMESPACES['ptu']}}}tp_RegCPL")
                 if tp is not None and tp.text:
                     tipos_existentes.append(tp.text.strip())
            
            needs_1 = '1' not in tipos_existentes
            needs_2 = '2' not in tipos_existentes
            
            if needs_1 or needs_2:
                 novos_comps = []
                 
                 if needs_1:
                     sintoma = random.choice(SINTOMAS)
                     # Usa indent_filho para alinhar conteudo interno dos complementos
                     # Passa add_indent (que pode ser vazio se flat)
                     comp1 = criar_bloco_complemento(dados_guia, 1, f"PACIENTE APRESENTA {sintoma}.", indent_filho, add_indent)
                     novos_comps.append(comp1)
                     
                 if needs_2:
                     comp2 = criar_bloco_complemento(dados_guia, 2, TXT_JUSTIFICATIVA, indent_filho, add_indent)
                     novos_comps.append(comp2)
                 
                 if novos_comps:
                     # ENCONTRA POSIÇÃO DE INSERÇÃO (Schema PTU)
                     # Ordem: procedimentosExecutados -> dt_UltimaAutorizacao -> COMPLEMENTO -> id_GuiaPrincipal
                     
                     index_insert = -1
                     target_insert = None
                     
                     # Tenta achar id_GuiaPrincipal para inserir ANTES dele
                     id_guia_principal = dados_guia.find(f"{{{NAMESPACES['ptu']}}}id_GuiaPrincipal")
                     if id_guia_principal is not None:
                         # Encontra o indice
                         for i, child in enumerate(dados_guia):
                             if child == id_guia_principal:
                                 index_insert = i
                                 target_insert = child
                                 break
                     
                     if index_insert != -1:
                         # INSERÇÃO NO MEIO (Antes de id_GuiaPrincipal)
                         
                         # O elemento anterior ao ponto de inserção precisa apontar para o primeiro novo complemento
                         # Se index_insert > 0, pega o anterior
                         if index_insert > 0:
                             elem_anterior = dados_guia[index_insert - 1]
                             elem_anterior.tail = indent_filho
                         
                         # Insere os novos componentes
                         for i, c in enumerate(novos_comps):
                             # Tail dos novos componentes
                             if i < len(novos_comps) - 1:
                                 c.tail = indent_filho
                             else:
                                 # O último novo deve ter o tail do elemento que estava lá (para manter a indentação do próximo)
                                 # Ou melhor, deve ter a indentação do irmão...
                                 # Se o próximo elemento existe, o tail do ultimo novo deve ser indent_filho para alinhar o próximo
                                 c.tail = indent_filho
                                 
                             dados_guia.insert(index_insert + i, c)
                             
                     else:
                         # FALLBACK: APPEND (Se não achou id_GuiaPrincipal, joga no final)
                         if last_child is not None:
                             last_child.tail = indent_filho
                         
                         for i, c in enumerate(novos_comps):
                             if i < len(novos_comps) - 1:
                                 c.tail = indent_filho
                             else:
                                 c.tail = indent_fechamento
                                 
                         for c in novos_comps:
                             dados_guia.append(c)

                     modificado_arquivo = True
                     print(f"  [COMPLEMENTO] Inseridos em dadosGuia (Posição {index_insert}): {[1 if needs_1 else '', 2 if needs_2 else '']}")

    if modificado_arquivo:
        path_out = os.path.join(CAMINHO_SAIDA, arquivo)
        
        # SISTEMA DE SEGURANÇA: BACKUP ANTES DE SOBRESCREVER
        if os.path.exists(path_out):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            path_backup = f"{path_out}.{timestamp}.bak"
            try:
                shutil.copy2(path_out, path_backup)
                print(f"  [BACKUP] Versão anterior salva em: {os.path.basename(path_backup)}")
            except Exception as e:
                print(f"  [AVISO] Falha ao criar backup: {e}")

        tree.write(path_out, encoding='ISO-8859-1', xml_declaration=True)
        print(f"  -> Salvo (Modificado): {path_out}")
    else:
        # Copia para garantir que a saída tenha todos os arquivos
        path_out = os.path.join(CAMINHO_SAIDA, arquivo)
        shutil.copy(path_in, path_out)
        print(f"  -> Salvo (Copia): {path_out}")

print("--- INICIANDO CORRECÃO ---")
arquivos = sorted([f for f in os.listdir(CAMINHO_ENTRADA) if f.endswith('.051') and 'corrigidos' not in f])
print(f"Arquivos na pasta: {len(arquivos)}")
count = 0
for f in arquivos:
    processar_arquivo(f)
    count += 1
print(f"--- FIM DA EXECUÇÃO (Processados: {count}) ---")
