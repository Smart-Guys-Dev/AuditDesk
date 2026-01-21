# Estruturas PTU - Guia de Referência

Este documento descreve as estruturas XML dos diferentes tipos de guias no padrão PTU (Projeto de Troca Unimed) versão 3.0.

## Namespace

```
xmlns:ptu="http://ptu.unimed.coop.br/schemas/V3_0"
```

## Schemas de Referência

- `src/schemas/ptu_CobrancaUtilizacao.xsd` - Schema principal
- `src/schemas/ptu_ComplexTypes-V3_0.xsd` - Tipos complexos (estruturas)
- `src/schemas/ptu_SimpleTypes-V3_0.xsd` - Tipos simples

---

## Tipos de Guias

### 1. Guia SADT (`guiaSADT`)

```
guiaSADT
├── dadosBeneficiario
│   └── cd_Unimed, id_Benef, nm_Benef, id_RN, tp_Paciente
├── dadosSolicitante
│   ├── contratadoSolicitante (cpf_cnpj, UnimedPrestador, nome)
│   └── profissional (nm_Profissional, dadosConselho, CBO)
├── dadosExecutante
│   └── UnimedPrestador, nome, CPF_CNPJ, CNES, prestador
├── dadosAtendimento
│   └── tp_Atendimento, tp_IndAcidente, caraterAtendimento, regimeAtendimento
└── dadosGuia
    ├── nr_Ver_TISS, nr_LotePrestador, dt_Protocolo
    ├── nr_Guias (nr_GuiaTissPrestador, nr_GuiaTissOperadora)
    ├── id_Liminar, id_Continuado, id_Avisado
    ├── cd_Excecao  ← AQUI (não em procedimentosExecutados)
    ├── id_GlosaTotal
    ├── procedimentosExecutados
    │   ├── dt_Execucao, hr_Inicial, hr_Final
    │   └── procedimentos (seq_item, cd_Servico, ds_Servico...)
    ├── dadosAutorizacao
    ├── complemento
    └── id_GuiaPrincipal
```

---

### 2. Guia Consulta (`guiaConsulta`)

```
guiaConsulta
├── dadosBeneficiario
├── contratadoExecutante  ← Diferente de SADT
│   └── UnimedPrestador, nome, CPF_CNPJ, CNES, prestador
├── profissionalExecutante  ← Elemento separado
│   └── UnimedPrestador, nome, dadosConselho, CBO
└── dadosGuia
    ├── nr_Ver_TISS, tp_Consulta, nr_LotePrestador
    ├── tp_IndAcidente, regimeAtendimento, dt_Atendimento
    ├── id_Liminar, id_Continuado, id_Avisado
    ├── cd_Excecao  ← Mesmo local
    ├── id_GlosaTotal
    ├── procedimentos  ← DIRETO (não tem procedimentosExecutados)
    │   └── seq_item, cd_Servico, vl_ServCobrado...
    └── dadosAutorizacao
```

---

### 3. Guia Internação (`guiaInternacao`)

```
guiaInternacao
├── dadosBeneficiario
├── dadosSolicitante
│   ├── contratadoSolicitante
│   └── profissional
├── dadosExecutante
├── dadosInternacao  ← EXCLUSIVO
│   ├── tp_Acomodacao, tp_Internacao, rg_Internacao
│   └── dadosFaturamento (dt_IniFaturamento, dt_FimFaturamento)
├── dadosSaidaInternacao  ← EXCLUSIVO
│   └── tp_IndAcidente, mv_Encerramento, CID
├── dadosAuditoria  ← EXCLUSIVO
│   └── nm_MedicoAuditor, nr_CrmAuditor, nm_EnfAuditor...
└── dadosGuia
    ├── nr_Guias (inclui nr_GuiaTissPrincipal)
    ├── id_Liminar, id_Continuado, id_Avisado
    ├── cd_Excecao  ← Mesmo local
    ├── id_GlosaTotal
    ├── procedimentosExecutados (múltiplos)
    │   ├── procedimentos
    │   └── dadosAutorizacao  ← Dentro de cada procedimento
    └── complemento
```

---

### 4. Guia Honorários (`guiaHonorarios`)

```
guiaHonorarios
├── dadosBeneficiario
├── dadosHospital  ← EXCLUSIVO
│   └── cd_uniHospitalar, cd_Hospitalar, CNPJHospital, CNES
├── dadosExecutante
├── dataFaturamento  ← EXCLUSIVO (separado)
│   └── dt_IniFaturamento, dt_FimFaturamento
└── dadosGuia
    ├── nr_Guias (inclui nr_GuiaTissPrincipal)
    ├── id_Liminar, id_Continuado, id_Avisado
    ├── cd_Excecao  ← Mesmo local
    ├── id_GlosaTotal
    ├── procedimentosExecutados
    │   ├── procedimentos
    │   ├── via_Acesso, tc_Utilizada  ← Específicos
    │   ├── equipe_Profissional  ← Dentro de procedimentosExecutados
    │   └── dadosAutorizacao
    └── complemento
```

---

## Tabela Comparativa

| Elemento | SADT | Consulta | Internação | Honorários |
|----------|:----:|:--------:|:----------:|:----------:|
| dadosSolicitante | ✅ | ❌ | ✅ | ❌ |
| dadosHospital | ❌ | ❌ | ❌ | ✅ |
| dadosInternacao | ❌ | ❌ | ✅ | ❌ |
| dadosAuditoria | ❌ | ❌ | ✅ | ❌ |
| profissionalExecutante | ❌ | ✅ | ❌ | ❌ |
| procedimentosExecutados | ✅ | ❌ | ✅ | ✅ |
| procedimentos (direto) | ❌ | ✅ | ❌ | ❌ |
| equipe_Profissional | Em procExec | ❌ | ❌ | Em procExec |
| cd_Excecao | dadosGuia | dadosGuia | dadosGuia | dadosGuia |

---

## Regras para XPath

### Campo `cd_Excecao`
- **Localização**: Sempre em `dadosGuia`
- Se `tipo_elemento = procedimentosExecutados`:
  - ✅ Correto: `../ptu:cd_Excecao`
  - ❌ Errado: `./ptu:cd_Excecao`

### Campo `equipe_Profissional`
- **Localização**: Dentro de `procedimentosExecutados` (SADT, Honorários)
- Se `tipo_elemento = procedimentosExecutados`:
  - ✅ Correto: `./ptu:equipe_Profissional`

### Campo `procedimentos`
- **SADT/Internação/Honorários**: Dentro de `procedimentosExecutados`
  - `./ptu:procedimentos/ptu:cd_Servico`
- **Consulta**: Direto em `dadosGuia`
  - Usar `tipo_elemento = procedimentos`
