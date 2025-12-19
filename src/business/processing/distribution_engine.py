# src/distribution_engine.py

def distribuir_faturas(lista_faturas, nomes_auditores):
    """
    Distribui as faturas processadas entre os auditores de forma equilibrada
    por valor total, ordenando as faturas da mais cara para a mais barata.
    """
    # 1. Preparação: Inicializa a estrutura para cada auditor.
    plano_distribuicao = {}
    for nome_auditor in nomes_auditores:
        plano_distribuicao[nome_auditor] = {
            'faturas': [],
            'total_valor': 0.0,
            'total_quantidade': 0
        }

    # 2. Converte os valores de string para float para poder ordenar.
    faturas_com_valor_numerico = []
    for fatura in lista_faturas:
        fatura_copia = fatura.copy()
        # Converte a string de valor para um número (float)
        valor_str_corrigido = fatura.get('valor_total_documento', "0.0").replace(',', '.')
        fatura_copia['valor_numerico'] = float(valor_str_corrigido)
        faturas_com_valor_numerico.append(fatura_copia)

    # 3. Ordena a lista de faturas da mais cara para a mais barata.
    faturas_ordenadas = sorted(faturas_com_valor_numerico, key=lambda f: f['valor_numerico'], reverse=True)

    # 4. Lógica de Distribuição: Atribui cada fatura ao auditor com o menor valor total acumulado.
    for fatura_obj in faturas_ordenadas:
        # Encontra o auditor com o menor total de valor acumulado no momento
        auditor_escolhido = min(plano_distribuicao, key=lambda nome: plano_distribuicao[nome]['total_valor'])

        # Atribui a fatura ao auditor escolhido
        plano_distribuicao[auditor_escolhido]['faturas'].append(fatura_obj)
        plano_distribuicao[auditor_escolhido]['total_valor'] += fatura_obj['valor_numerico']
        plano_distribuicao[auditor_escolhido]['total_quantidade'] += 1

    return plano_distribuicao