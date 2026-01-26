# REGRA_TAXA_OBSERVACAO_CORRIGIR_HORARIOS

## Informações Gerais

| Campo | Valor |
|-------|-------|
| **ID da Regra** | `REGRA_TAXA_OBSERVACAO_CORRIGIR_HORARIOS` |
| **Data de Criação** | 22/01/2026 |
| **Autor** | Equipe de Faturamento |
| **Status** | ✅ Ativa |
| **Arquivo JSON** | `src/config/regras/taxas_observacao.json` |

---

## Fundamentação Normativa

### Boletim GTFI 25/09/2025
> "Para atendimento em pronto socorro com a utilização e cobrança da taxa de observação, é obrigatório o preenchimento com horários distintos nos campos 'hr_inicial' e 'hr_final', de modo a refletir com precisão o período efetivo de permanência do beneficiário em observação, para a correta cobrança e pagamento da taxa de observação."

### Manual PTU XML 2.2
Os campos `hr_Inicial` e `hr_Final` devem representar o horário real de início e término do serviço prestado.

---

## Códigos Afetados

| Código | Descrição | tp_Tabela |
|--------|-----------|-----------|
| **60033681** | Taxa de Sala de Observação, até 6 horas | 18 |
| **60033665** | Taxa de Sala de Observação, até 12 horas | 18 |

---

## Problema Identificado

Em algumas cobranças, o item de taxa de sala de observação é enviado com horários idênticos ou zerados:

```xml
<ptu:hr_Inicial>00:00:01</ptu:hr_Inicial>
<ptu:hr_Final>00:00:01</ptu:hr_Final>
<ptu:cd_Servico>60033681</ptu:cd_Servico>
```

Isso configura **preenchimento incorreto** e pode resultar em **glosa** pela Unimed de destino.

---

## Lógica da Regra

### Condições de Aplicação

```
SE:
  - cd_Servico = "60033681" OU "60033665"
  - E hr_Inicial = hr_Final (horários idênticos)
  - E existem outros itens na guia com horários válidos (diferentes)

ENTÃO:
  - Copiar hr_Inicial e hr_Final do primeiro item válido da mesma guia
```

### Fluxo de Decisão

```
┌─────────────────────────────────────────┐
│ Item é taxa de observação?              │
│ (60033681 ou 60033665)                  │
└────────────────┬────────────────────────┘
                 │ SIM
                 ▼
┌─────────────────────────────────────────┐
│ hr_Inicial = hr_Final?                  │
└────────────────┬────────────────────────┘
                 │ SIM
                 ▼
┌─────────────────────────────────────────┐
│ Existe outro item com horários válidos?│
└────────────────┬────────────────────────┘
                 │ SIM
                 ▼
┌─────────────────────────────────────────┐
│ CORRIGIR: Copiar horários do item      │
│ válido para a taxa de observação       │
└─────────────────────────────────────────┘
```

---

## Ação Corretiva

1. Localizar o primeiro `procedimentosExecutados` da mesma guia que possua `hr_Inicial ≠ hr_Final`
2. Copiar os valores de `hr_Inicial` e `hr_Final` deste item
3. Aplicar no item da taxa de observação

---

## Exemplo Real

### Antes (incorreto):
```xml
<!-- Taxa de Observação com horários zerados -->
<ptu:procedimentosExecutados>
    <ptu:hr_Inicial>00:00:01</ptu:hr_Inicial>
    <ptu:hr_Final>00:00:01</ptu:hr_Final>
    <ptu:procedimentos>
        <ptu:cd_Servico>60033681</ptu:cd_Servico>
    </ptu:procedimentos>
</ptu:procedimentosExecutados>

<!-- Outros itens com horários corretos -->
<ptu:procedimentosExecutados>
    <ptu:hr_Inicial>10:53:31</ptu:hr_Inicial>
    <ptu:hr_Final>14:28:00</ptu:hr_Final>
    <ptu:procedimentos>
        <ptu:cd_Servico>1900227633</ptu:cd_Servico>
    </ptu:procedimentos>
</ptu:procedimentosExecutados>
```

### Depois (corrigido):
```xml
<!-- Taxa de Observação com horários corrigidos -->
<ptu:procedimentosExecutados>
    <ptu:hr_Inicial>10:53:31</ptu:hr_Inicial>
    <ptu:hr_Final>14:28:00</ptu:hr_Final>
    <ptu:procedimentos>
        <ptu:cd_Servico>60033681</ptu:cd_Servico>
    </ptu:procedimentos>
</ptu:procedimentosExecutados>
```

---

## Justificativa Técnica

1. **Consistência**: Os horários dos demais itens refletem o período real de atendimento
2. **Evidência**: Materiais e medicamentos foram utilizados neste período
3. **Compatibilidade**: O período corrigido (ex: 3h35min) é compatível com a taxa cobrada (até 6 horas)
4. **Prevenção de Glosa**: Evita rejeição por preenchimento incorreto

---

## Metadados da Glosa

| Campo | Valor |
|-------|-------|
| **Categoria** | CORRECAO_AUTOMATICA |
| **Impacto Financeiro** | ALTO |
| **Risco de Erro** | BAIXO |
| **Razão** | Correção de preenchimento de campos obrigatórios |

---

## Log de Aplicação

```
"Horários da taxa de observação (cd_Servico: 60033681) corrigidos de 00:00:01/00:00:01 para hr_Inicial=10:53:31 e hr_Final=14:28:00, conforme boletim GTFI 25/09/2025."
```

---

## Histórico de Alterações

| Data | Versão | Alteração | Autor |
|------|--------|-----------|-------|
| 22/01/2026 | 1.0 | Criação da regra | Equipe de Faturamento |
