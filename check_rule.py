import sys, json
sys.path.insert(0, r'C:\Users\pedro.freitas\AuditPlusv2.0')

# Carregar o JSON real
with open(r'C:\Users\pedro.freitas\AuditPlusv2.0\src\config\regras\pj_pf_rotativo.json', 'r', encoding='utf-8') as f:
    rules = json.load(f)

rule = rules[0]
conds = rule['condicoes']

cm = conds['condicao_multipla']
sub_conds = cm.get('sub_condicoes', [])

print(f"Total sub_condicoes no AND: {len(sub_conds)}")
for i, sc in enumerate(sub_conds):
    print(f"\n[{i}] Tipo: {list(sc.keys())}")
    if 'condicao_multipla' in sc:
        inner = sc['condicao_multipla']
        print(f"    -> Tipo logico: {inner.get('tipo')}")
        print(f"    -> Num sub_condicoes: {len(inner.get('sub_condicoes', []))}")
        for j, isc in enumerate(inner.get('sub_condicoes', [])):
            if 'condicao_tag_valor' in isc:
                ctv = isc['condicao_tag_valor']
                print(f"       [{j}] xpath: {ctv.get('xpath')[-40:]}, tipo: {ctv.get('tipo_comparacao', 'valor_permitido')}")
