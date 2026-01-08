# Profissionais para Rotação PJ→PF

## Resumo
Lista de profissionais para intercalar quando um beneficiário tem múltiplas consultas (10101039) na mesma fatura.

## Profissionais

| # | Nome | CPF | cd_Prest | CRM | UF | CBO |
|---|------|-----|----------|-----|----|-----|
| 1 | RODRIGO DOMINGUES LARAYA | 20034717153 | 11021 | (existente) | 50 | 225125 |
| 2 | ROTTERDAM PEREIRA GUIMARAES | 60829800182 | 198063 | 10730 | 50 | 225125 |
| 3 | JUSTINIANO BARBOSA VAVAS | 20033389187 | 559 | 1491 | 50 | 225125 |
| 4 | VICTOR H. M. BONOMO | 04700094117 | 18763 | 8108 | 50 | 225125 |

## Lógica de Rotação
- Beneficiário com 1 consulta → Profissional 1
- Beneficiário com 2 consultas → Profissional 1, Profissional 2
- Beneficiário com 3 consultas → Profissional 1, Profissional 2, Profissional 3
- E assim por diante (cíclico)

## Prestador Alvo
- cd_Prest: 11101 (Hospital que envia CNPJ ao invés de CPF)
