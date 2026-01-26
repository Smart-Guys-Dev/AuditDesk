import sys
import os
import logging

import sys
import os
import logging

# Configurar logging para arquivo
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='debug_run.log',
    filemode='w'
)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lxml import etree

# XML de teste com taxa de observacao com horarios iguais
xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<ans:mensagemTISS xmlns:ans="http://www.ans.gov.br/padroes/tiss/schemas"
                  xmlns:ptu="http://ptu.unimed.coop.br/schemas/V3_0">
  <ans:cabecalho>
    <ans:identificacaoTransacao>
      <ans:tipoTransacao>ENVIO_LOTE_GUIAS</ans:tipoTransacao>
    </ans:identificacaoTransacao>
    <ans:origem>
      <ans:identificacaoPrestador>
        <ans:codigoPrestadorNaOperadora>123456</ans:codigoPrestadorNaOperadora>
      </ans:identificacaoPrestador>
    </ans:origem>
    <ans:destino>
      <ans:registroANS>123456</ans:registroANS>
    </ans:destino>
    <ans:versaoPadrao>3.05.00</ans:versaoPadrao>
  </ans:cabecalho>
  <ans:prestadorParaOperadora>
    <ans:loteGuias>
      <ans:guiasTISS>
        <ptu:guiaSP-SADT>
          <ptu:dadosGuia>
            <ptu:procedimentosExecutados>
              <ptu:cd_Servico>10101012</ptu:cd_Servico>
              <ptu:ds_Servico>Consulta Medica</ptu:ds_Servico>
              <ptu:hr_Inicial>10:00:00</ptu:hr_Inicial>
              <ptu:hr_Final>12:00:00</ptu:hr_Final>
            </ptu:procedimentosExecutados>
            <ptu:procedimentosExecutados>
              <ptu:cd_Servico>60033681</ptu:cd_Servico>
              <ptu:ds_Servico>TAXA DE SALA DE OBSERVACAO ATE 6 HORAS</ptu:ds_Servico>
              <ptu:hr_Inicial>00:00:01</ptu:hr_Inicial>
              <ptu:hr_Final>00:00:01</ptu:hr_Final>
            </ptu:procedimentosExecutados>
          </ptu:dadosGuia>
        </ptu:guiaSP-SADT>
      </ans:guiasTISS>
    </ans:loteGuias>
  </ans:prestadorParaOperadora>
</ans:mensagemTISS>"""

# Parse o XML
tree = etree.fromstring(xml_content.encode('utf-8'))
xml_tree = etree.ElementTree(tree)

# Capturar valores ANTES
ns = {'ptu': 'http://ptu.unimed.coop.br/schemas/V3_0', 'ans': 'http://www.ans.gov.br/padroes/tiss/schemas'}
procs = tree.xpath('.//ptu:procedimentosExecutados', namespaces=ns)

print("=== ANTES ===")
for i, proc in enumerate(procs):
    cd = proc.find('ptu:cd_Servico', ns)
    hi = proc.find('ptu:hr_Inicial', ns)
    hf = proc.find('ptu:hr_Final', ns)
    print(f"  Proc {i+1}: cd={cd.text if cd is not None else 'N/A'}, hr_Inicial={hi.text if hi is not None else 'N/A'}, hr_Final={hf.text if hf is not None else 'N/A'}")

# Aplicar regras
from src.business.rules.rule_engine import RuleEngine
engine = RuleEngine()
engine.load_all_rules()

print(f"\n=== REGRAS CARREGADAS: {len(engine.loaded_rules)} ===")

# Verificar se a regra foi carregada
taxa_rule = None
for rule in engine.loaded_rules:
    rule_id = rule.get('id', '')
    if 'TAXA' in rule_id.upper() or 'OBSERVA' in rule_id.upper():
        print(f"  -> Candidata: {rule_id}")
        taxa_rule = rule
    if 'OBSERVACAO' in rule_id:
        taxa_rule = rule
        break

if taxa_rule:
    print(f"\n=== REGRA ENCONTRADA ===")
    print(f"  ID: {taxa_rule.get('id')}")
else:
    print("\n=== REGRA NAO ENCONTRADA ===")
    sys.exit(1)

# Aplicar regras
result = engine.apply_rules_to_xml(xml_tree)
print(f"\n=== RESULTADO ===")
print(f"  Modificado: {result}")

# Capturar valores DEPOIS
print("\n=== DEPOIS ===")
root = xml_tree.getroot()
procs = root.xpath('.//ptu:procedimentosExecutados', namespaces=ns)
for i, proc in enumerate(procs):
    cd = proc.find('ptu:cd_Servico', ns)
    hi = proc.find('ptu:hr_Inicial', ns)
    hf = proc.find('ptu:hr_Final', ns)
    print(f"  Proc {i+1}: cd={cd.text if cd is not None else 'N/A'}, hr_Inicial={hi.text if hi is not None else 'N/A'}, hr_Final={hf.text if hf is not None else 'N/A'}")

# Verificar sucesso
if result:
    # Verificar se os horarios foram corrigidos
    for proc in procs:
        cd = proc.find('ptu:cd_Servico', ns)
        if cd is not None and cd.text == '60033681':
            hi = proc.find('ptu:hr_Inicial', ns)
            hf = proc.find('ptu:hr_Final', ns)
            if hi.text != hf.text:
                print("\n*** SUCESSO! Horarios corrigidos! ***")
            else:
                print("\n*** FALHA: Horarios ainda iguais ***")
else:
    print("\n*** FALHA: Nenhuma modificacao aplicada ***")
