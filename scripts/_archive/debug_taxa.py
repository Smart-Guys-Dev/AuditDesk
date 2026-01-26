# debug_taxa.py
import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

import lxml.etree as etree
from src.infrastructure.parsers.xml_reader import XMLReader, NAMESPACES
from src.business.rules.rule_engine import RuleEngine

XML = """<ptu:FaturaCobrancaA500 xmlns:ptu="http://ptu.unimed.coop.br/schemas/V3_0">
<ptu:guiaSADT>
    <ptu:dadosGuia>
        <ptu:procedimentosExecutados>
            <ptu:hr_Inicial>10:53:31</ptu:hr_Inicial>
            <ptu:hr_Final>14:28:00</ptu:hr_Final>
            <ptu:procedimentos><ptu:cd_Servico>1900227633</ptu:cd_Servico></ptu:procedimentos>
        </ptu:procedimentosExecutados>
        <ptu:procedimentosExecutados>
            <ptu:hr_Inicial>00:00:01</ptu:hr_Inicial>
            <ptu:hr_Final>00:00:01</ptu:hr_Final>
            <ptu:procedimentos><ptu:cd_Servico>60033681</ptu:cd_Servico></ptu:procedimentos>
        </ptu:procedimentosExecutados>
    </ptu:dadosGuia>
</ptu:guiaSADT>
</ptu:FaturaCobrancaA500>"""

root = etree.fromstring(XML)
reader = XMLReader()

procs = reader.find_elements_by_xpath(root, ".//ptu:procedimentosExecutados")
print("Encontrados:", len(procs), "procedimentosExecutados")

for i, p in enumerate(procs):
    cd = reader.find_elements_by_xpath(p, "./ptu:procedimentos/ptu:cd_Servico")
    cd_text = cd[0].text if cd else "N/A"
    hi = reader.find_elements_by_xpath(p, "./ptu:hr_Inicial")
    hf = reader.find_elements_by_xpath(p, "./ptu:hr_Final")
    hi_text = hi[0].text if hi else "N/A"
    hf_text = hf[0].text if hf else "N/A"
    print("  Proc %d: cd=%s, hi=%s, hf=%s, iguais=%s" % (i+1, cd_text, hi_text, hf_text, hi_text == hf_text))
    
    # Testar a condicao
    if cd_text in ["60033681", "60033665"]:
        print("    -> E taxa de observacao!")
        if hi_text == hf_text:
            print("    -> Horarios IGUAIS - deveria aplicar regra!")

# Carregar as regras e verificar
e = RuleEngine()
e.load_all_rules(use_database=False)

# Encontrar a regra especifica
regra = None
for r in e.loaded_rules:
    if "TAXA" in r.get("id", ""):
        regra = r
        print("\nRegra encontrada:", r.get("id"))
        print("Condicoes:", r.get("condicoes"))
        break

# Testar manualmente a condicao no segundo procedimento
if regra:
    p = procs[1]  # Taxa de observacao
    result = e._evaluate_condition(p, regra.get("condicoes", {}))
    print("")
    print("RESULTADO AVALIACAO:", result)
    if result:
        action_result = e._apply_action(p, regra.get("acao", {}))
        print("RESULTADO ACAO:", action_result)
        # Mostrar horarios apos acao
        hi = reader.find_elements_by_xpath(p, "./ptu:hr_Inicial")
        hf = reader.find_elements_by_xpath(p, "./ptu:hr_Final")
        print("HORARIOS APOS ACAO:", hi[0].text, hf[0].text)
