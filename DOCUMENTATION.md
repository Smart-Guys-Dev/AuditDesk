# AuditPlus v2.0 - Documentação do Sistema

## Visão Geral

O **AuditPlus** é um sistema desktop para auditoria e validação de arquivos XML no padrão PTU (Padrão TISS Unimed). O sistema aplica regras de negócio automaticamente para corrigir inconsistências antes do envio às operadoras, evitando glosas.

## Arquitetura

```
AuditPlusv2.0/
├── src/
│   ├── business/rules/       # Motor de regras
│   ├── config/               # Configurações e regras JSON
│   │   ├── regras/           # Regras por categoria
│   │   └── *.json            # Arquivos de configuração
│   ├── database/             # Camada de persistência
│   ├── infrastructure/       # Parsers e utilidades
│   └── views/pages/          # Interface gráfica (PyQt6)
├── data/                     # Dados e relatórios
└── main.py                   # Ponto de entrada
```

## Funcionalidades Principais

### 1. Processador XML
- Carrega arquivos XML no padrão PTU
- Aplica regras de validação automaticamente
- Gera arquivo corrigido com sufixo `_CORRIGIDO`

### 2. Motor de Regras (Rule Engine)
O sistema suporta os seguintes tipos de ação:

| Ação | Descrição |
|------|-----------|
| `garantir_tag_com_conteudo` | Cria ou atualiza uma tag com valor específico |
| `remover_tag` | Remove uma tag do XML |
| `substituir_conteudo` | Substitui o conteúdo de uma tag |

### 3. Dashboard
Exibe KPIs em tempo real:
- Economia Total
- Glosas Evitadas
- Total Faturado
- Regras Ativas
- Taxa de Sucesso
- Última Execução

### 4. Importação de Relatórios
Suporta 3 tipos de relatórios Excel:
- **A500 Enviados** - Faturas enviadas para NCMB
- **Distribuição de Faturas** - Por auditor/responsável
- **Faturas Emitidas** - Do SGU

---

## Regras Implementadas

### Regras de tp_Participacao
Garantem o código de participação correto para cada procedimento.

| Código | Condição | tp_Participacao |
|--------|----------|-----------------|
| 30602467 | COM porte anestésico | 06 |
| 30602467 | SEM porte anestésico | 00 |
| 40813363 | COM porte anestésico | 06 |
| 40813363 | SEM porte anestésico | 00 |
| 20104103 | - | 12 |
| 20104090 | - | 12 |
| ... | | |

### Regras de CNES
Garantem o CNES correto para cada prestador pelo CNPJ.

| Prestador | CNPJ | CNES |
|-----------|------|------|
| CENTRO DE RITMOLOGIA DE BRASILIA LTDA | 22414227000116 | 9213074 |
| RESGATARE | 52838800000180 | 4892402 |
| LAZARI E OGUCHI | 40659789000101 | 4611004 |
| ... | | |

### Regras de Equipe Obrigatória
Lista de códigos que exigem equipe profissional no XML.

---

## Como Adicionar Novas Regras

### 1. Regra de tp_Participacao
Edite `src/config/regras_tp_participacao.json`:

```json
{
  "id": "REGRA_PARTICIPACAO_[CODIGO]",
  "descricao": "Garante tp_Participacao = '[VALOR]' para o serviço [CODIGO].",
  "ativo": true,
  "condicoes": {
    "tipo_elemento": "procedimentosExecutados",
    "condicao_tag_valor": {
      "xpath": "./ptu:procedimentos/ptu:cd_Servico",
      "valor_permitido": ["[CODIGO]"]
    }
  },
  "acao": {
    "tipo_acao": "garantir_tag_com_conteudo",
    "tag_alvo": "./ptu:equipe_Profissional/ptu:tp_Participacao",
    "novo_conteudo": "[VALOR]",
    "posicao_insercao": "primeiro_filho",
    "tag_pai_referencia": "./ptu:equipe_Profissional"
  }
}
```

### 2. Regra de CNES
Edite `src/config/regras/cnes.json`:

```json
{
  "id": "REGRA_GARANTIR_CNES_[NOME]_[CNPJ]",
  "descricao": "Garante que o CNES ([CNES]) esteja correto para o prestador [NOME] (CNPJ [CNPJ]).",
  "ativo": true,
  "condicoes": {
    "tipo_elemento": "dadosExecutante",
    "condicao_multipla": {
      "tipo": "AND",
      "sub_condicoes": [
        {
          "condicao_tag_valor": {
            "xpath": "./ptu:CPF_CNPJ/ptu:cd_cnpj",
            "valor_permitido": ["[CNPJ]"]
          }
        },
        {
          "condicao_tag_valor": {
            "xpath": "./ptu:CNES",
            "tipo_comparacao": "valor_atual_diferente",
            "valor_atual": "[CNES]"
          }
        }
      ]
    }
  },
  "acao": {
    "tipo_acao": "garantir_tag_com_conteudo",
    "tag_alvo": "./ptu:CNES",
    "novo_conteudo": "[CNES]",
    "tag_referencia_posicao": "./ptu:CPF_CNPJ"
  }
}
```

---

## Execução

```powershell
# Ativar ambiente virtual
& c:/Users/pedro.freitas/AuditPlusv2.0/venv/Scripts/Activate.ps1

# Executar aplicação
python main.py
```

## Tecnologias
- **Python 3.13**
- **PyQt6** - Interface gráfica
- **SQLAlchemy** - ORM
- **lxml** - Processamento XML
- **pandas** - Manipulação de dados Excel

---

*Última atualização: 06/01/2026*
