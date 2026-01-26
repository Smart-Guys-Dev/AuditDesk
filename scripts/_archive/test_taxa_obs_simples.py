# -*- coding: utf-8 -*-
import lxml.etree as etree
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.business.rules.rule_engine import RuleEngine

XML = """<?xml version="1.0" encoding="UTF-8"?>
<ptu:FaturaCobrancaA500 xmlns:ptu="http://ptu.unimed.coop.br/schemas/V3_0">
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

e = RuleEngine()
e.load_all_rules(use_database=False)
tree = etree.fromstring(XML.encode()).getroottree()

ns = {"ptu": "http://ptu.unimed.coop.br/schemas/V3_0"}
procs = tree.xpath("//ptu:procedimentosExecutados", namespaces=ns)

print("ANTES:")
for p in procs:
    cd = p.find("ptu:procedimentos/ptu:cd_Servico", ns).text
    hi = p.find("ptu:hr_Inicial", ns).text
    hf = p.find("ptu:hr_Final", ns).text
    print("  %s: %s - %s" % (cd, hi, hf))

mod = e.apply_rules_to_xml(tree, -1, "test.xml")
print("Modificado: %s" % mod)

print("DEPOIS:")
for p in procs:
    cd = p.find("ptu:procedimentos/ptu:cd_Servico", ns).text
    hi = p.find("ptu:hr_Inicial", ns).text
    hf = p.find("ptu:hr_Final", ns).text
    print("  %s: %s - %s" % (cd, hi, hf))

# Verificar resultado
taxa = procs[1]
hi_novo = taxa.find("ptu:hr_Inicial", ns).text
hf_novo = taxa.find("ptu:hr_Final", ns).text

if hi_novo == "10:53:31" and hf_novo == "14:28:00":
    print("\n[SUCESSO] Horarios corrigidos!")
    sys.exit(0)
else:
    print("\n[FALHA] Horarios NAO corrigidos!")
    sys.exit(1)
