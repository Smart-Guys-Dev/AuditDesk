# REGRA_JAMIL_THIAGO_COMPLETAR_CRM / \_COMPLETAR_UF

## Informações Gerais

| Campo               | Valor                                                                  |
| ------------------- | ---------------------------------------------------------------------- |
| **ID da Regra**     | `REGRA_JAMIL_THIAGO_COMPLETAR_CRM` e `REGRA_JAMIL_THIAGO_COMPLETAR_UF` |
| **Data de Criação** | 04/02/2026                                                             |
| **Autor**           | Equipe de Faturamento                                                  |
| **Status**          | ✅ Ativa                                                               |
| **Arquivo JSON**    | `src/config/regras/auditoria.json`                                     |

---

## Fundamentação Normativa

### Padrão TISS/PTU

> O bloco `<dadosAuditoria>` deve conter identificação completa do médico auditor, incluindo nome, número do CRM e UF do conselho, conforme Manual PTU XML 2.2.

### Validação A400

Guias enviadas sem CRM do auditor resultam em erro de validação pelo sistema A400 da Unimed do Brasil.

---

## Dados do Profissional

| Campo     | Valor                        |
| --------- | ---------------------------- |
| **Nome**  | JAMIL THIAGO ROSA RIBEIRO    |
| **CRM**   | 15332                        |
| **UF**    | 50 (MS - Mato Grosso do Sul) |
| **Fonte** | Consulta CFM - 28/04/2025    |

---

## Problema Identificado

Em algumas guias de internação, o bloco `<dadosAuditoria>` vem apenas com o nome do médico auditor, sem as tags de CRM e UF:

```xml
<ptu:dadosAuditoria>
    <ptu:nm_MedicoAuditor>JAMIL THIAGO ROSA RIBEIRO</ptu:nm_MedicoAuditor>
    <!-- ❌ FALTA: nr_CrmAuditor -->
    <!-- ❌ FALTA: cd_UFCRM -->
    <ptu:nm_EnfAuditor>GRAZIELA APARECIDA MENDIETA</ptu:nm_EnfAuditor>
    <ptu:nr_CorenAuditor>591874</ptu:nr_CorenAuditor>
    <ptu:cd_UFCoren>50</ptu:cd_UFCoren>
</ptu:dadosAuditoria>
```

Isso configura **preenchimento incompleto** e resulta em **glosa total da guia** pela operadora de destino.

---

## Lógica da Regra

### Condições de Aplicação

```
REGRA 1 - COMPLETAR CRM:
SE:
  - Bloco é <dadosAuditoria>
  - E nm_MedicoAuditor = "JAMIL THIAGO ROSA RIBEIRO"
  - E nr_CrmAuditor NÃO EXISTE

ENTÃO:
  - Inserir <nr_CrmAuditor>15332</nr_CrmAuditor>

---

REGRA 2 - COMPLETAR UF:
SE:
  - Bloco é <dadosAuditoria>
  - E nm_MedicoAuditor = "JAMIL THIAGO ROSA RIBEIRO"
  - E cd_UFCRM NÃO EXISTE

ENTÃO:
  - Inserir <cd_UFCRM>50</cd_UFCRM>
```

### Fluxo de Decisão

```
┌─────────────────────────────────────────┐
│ Bloco é <dadosAuditoria>?               │
└────────────────┬────────────────────────┘
                 │ SIM
                 ▼
┌─────────────────────────────────────────┐
│ nm_MedicoAuditor = "JAMIL THIAGO..."?   │
└────────────────┬────────────────────────┘
                 │ SIM
                 ▼
┌─────────────────────────────────────────┐
│ nr_CrmAuditor existe?                   │
└────────┬───────────────┬────────────────┘
      NÃO│               │SIM
         ▼               ▼
┌────────────────┐   ┌────────────────────┐
│ INSERIR CRM    │   │ Nenhuma ação       │
│ 15332          │   │ (já existe)        │
└────────────────┘   └────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│ cd_UFCRM existe?                        │
└────────┬───────────────┬────────────────┘
      NÃO│               │SIM
         ▼               ▼
┌────────────────┐   ┌────────────────────┐
│ INSERIR UF     │   │ Nenhuma ação       │
│ 50 (MS)        │   │ (já existe)        │
└────────────────┘   └────────────────────┘
```

---

## Exemplo Real

### Antes (incompleto):

```xml
<ptu:dadosAuditoria>
    <ptu:nm_MedicoAuditor>JAMIL THIAGO ROSA RIBEIRO</ptu:nm_MedicoAuditor>
    <ptu:nm_EnfAuditor>GRAZIELA APARECIDA MENDIETA</ptu:nm_EnfAuditor>
    <ptu:nr_CorenAuditor>591874</ptu:nr_CorenAuditor>
    <ptu:cd_UFCoren>50</ptu:cd_UFCoren>
</ptu:dadosAuditoria>
```

### Depois (corrigido):

```xml
<ptu:dadosAuditoria>
    <ptu:nm_MedicoAuditor>JAMIL THIAGO ROSA RIBEIRO</ptu:nm_MedicoAuditor>
    <ptu:nr_CrmAuditor>15332</ptu:nr_CrmAuditor>      <!-- ✅ INSERIDO -->
    <ptu:cd_UFCRM>50</ptu:cd_UFCRM>                  <!-- ✅ INSERIDO -->
    <ptu:nm_EnfAuditor>GRAZIELA APARECIDA MENDIETA</ptu:nm_EnfAuditor>
    <ptu:nr_CorenAuditor>591874</ptu:nr_CorenAuditor>
    <ptu:cd_UFCoren>50</ptu:cd_UFCoren>
</ptu:dadosAuditoria>
```

---

## Justificativa Técnica

1. **Fonte Oficial**: CRM 15332/MS verificado no site do CFM
2. **Consistência**: O médico aparece corretamente em outras guias
3. **Prevenção de Glosa**: Evita rejeição total da guia por dados incompletos
4. **Reordenação Automática**: A regra `REGRA_ORDEM_DADOS_AUDITORIA` garante ordem correta das tags

---

## Metadados da Glosa

| Campo                  | Valor                                                |
| ---------------------- | ---------------------------------------------------- |
| **Categoria**          | GLOSA_GUIA                                           |
| **Impacto Financeiro** | ALTO                                                 |
| **Risco de Erro**      | BAIXO                                                |
| **Razão**              | Ausência de CRM/UF do auditor resulta em glosa total |

---

## Log de Aplicação

```
"CRM 15332 inserido para médico auditor JAMIL THIAGO ROSA RIBEIRO."
"UF 50 (MS) inserida para médico auditor JAMIL THIAGO ROSA RIBEIRO."
```

---

## Arquivo de Configuração Relacionado

Foi criado o arquivo `src/config/medicos_auditores.json` para referência futura:

```json
[
  {
    "nome": "JAMIL THIAGO ROSA RIBEIRO",
    "crm": "15332",
    "uf_crm": "50",
    "comentario": "CRM/MS - Auditor médico principal"
  }
]
```

---

## Histórico de Alterações

| Data       | Versão | Alteração          | Autor                 |
| ---------- | ------ | ------------------ | --------------------- |
| 04/02/2026 | 1.0    | Criação das regras | Equipe de Faturamento |
