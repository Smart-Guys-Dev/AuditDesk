"""Script para verificar XMLs e testar regra"""
import sys
sys.path.insert(0, 'c:/Users/pedro.freitas/AuditPlusv2.0')
from lxml import etree
import os

NAMESPACES = {'ptu': 'http://ptu.unimed.coop.br/schemas/V3_0'}
pasta = 'C:/Spool/pedro.freitas/FATURAMENTO SGU/12.Dez/ARQUIVOS/SEMANA 4/ERRO'

count = 0
found_9134 = 0

print("=== Verificando XMLs ===")
for f in os.listdir(pasta)[:10]:
    if f.endswith('.xml'):
        try:
            tree = etree.parse(os.path.join(pasta, f))
            prests = tree.xpath('//ptu:cd_Prest', namespaces=NAMESPACES)
            for p in prests:
                if p.text == '9134':
                    found_9134 += 1
                    parent = p.getparent().getparent()
                    cpf = parent.find('.//ptu:cdCnpjCpf', namespaces=NAMESPACES)
                    status = "JA TEM CPF" if cpf is not None else "SEM CPF"
                    print(f"  {f}: cd_Prest=9134 -> {status}")
            count += 1
        except Exception as e:
            print(f"  {f}: ERRO - {str(e)[:50]}")

print(f"\nTotal verificados: {count}")
print(f"Com prestador 9134: {found_9134}")

if found_9134 == 0:
    print("\n⚠️ Nenhum XML tem cd_Prest=9134!")
    print("   A regra só se aplica quando cd_Prest=9134")
