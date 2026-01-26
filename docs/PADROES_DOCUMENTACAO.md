# Padrão de Documentação de Regras - AuditPlus v2.0

Este documento define o **padrão oficial** para documentação de regras de negócio do AuditPlus.

---

## 📁 Estrutura de Arquivos

```
docs/
├── regras/                     # Documentação individual de cada regra
│   ├── [ID_REGRA].html        # Relatório HTML da regra
│   └── ...
├── PADROES_DOCUMENTACAO.md    # Este documento
└── CHANGELOG_REGRAS.md        # Histórico de alterações (opcional)
```

---

## 📋 Quando Documentar

Uma documentação **DEVE** ser gerada ou atualizada quando:

| Evento | Ação na Documentação |
|--------|---------------------|
| ✅ Nova regra criada | Criar novo documento |
| 🔧 Regra modificada | Atualizar documento existente |
| ❌ Regra desativada | Marcar status como "DESATIVADO" |
| 🗑️ Regra excluída | Arquivar documento (mover para `regras/arquivo/`) |

---

## 📄 Especificação do Documento

### Nomenclatura
- **Formato**: `[ID_CURTO].html`
- **Convenção**: MAIÚSCULAS, underscores, sem acentos
- **Exemplo**: `TAXA_OBSERVACAO_HORARIOS.html`, `CPF_PRESTADOR_9134.html`

### Seções Obrigatórias

| # | Seção | Descrição |
|---|-------|-----------|
| 1 | **Cabeçalho** | Nome do relatório + Badge de status |
| 2 | **Informações da Regra** | ID, Grupo, Categoria, Tipo de Ação, Descrição |
| 3 | **Métricas de Desenvolvimento** | Data, Horário início/fim, Testes realizados, Versão |
| 4 | **Configuração JSON** | Snapshot da regra no formato JSON |
| 5 | **Detalhes da Solução** | Explicação técnica do que foi implementado |
| 6 | **Casos de Teste** | Exemplos de entrada/saída esperada |
| 7 | **Rodapé** | Unimed • Data • Hora • Sistema • Autor |

### Badges de Status

| Status | Cor | Uso |
|--------|-----|-----|
| `IMPLEMENTADO` | Verde (#00995D) | Regra ativa e funcionando |
| `EM DESENVOLVIMENTO` | Amarelo (#FFC107) | Regra em construção |
| `DESATIVADO` | Vermelho (#F44336) | Regra temporariamente inativa |
| `OBSOLETO` | Cinza (#9E9E9E) | Regra substituída ou removida |

---

## 🎨 Identidade Visual

### Cores
```css
--unimed-green: #00995D;     /* Verde institucional (primária) */
--dark-text: #263238;        /* Texto principal */
--bg-light: #f4f6f8;         /* Fundo da página */
--card-white: #ffffff;       /* Fundo dos cards */
--accent-orange: #ff7043;    /* Destaque métricas */
--accent-blue: #42a5f5;      /* Destaque secundário */
```

### Tipografia
- **Fonte principal**: Segoe UI, Roboto, sans-serif
- **Código/JSON**: Consolas, Monaco, monospace
- **Tamanhos**: H1=24px, H2=18px, Body=14px, Labels=11px

---

## 📝 Campos Detalhados

### 1. Informações da Regra

| Campo | Tipo | Exemplo |
|-------|------|---------|
| ID da Regra | String | `REGRA_TAXA_OBSERVACAO_CORRIGIR_HORARIOS` |
| Grupo | String | `Taxas de Observação`, `Equipe Profissional` |
| Categoria | Enum | `GLOSA_GUIA`, `GLOSA_ITEM`, `VALIDACAO`, `OTIMIZACAO` |
| Tipo de Ação | String | `copiar_horarios_de_outro_item`, `substituir_valor` |
| Descrição | Texto | Descrição completa do que a regra faz e por quê |

### 2. Métricas de Desenvolvimento

| Campo | Tipo | Descrição |
|-------|------|-----------|
| Data | DD/MM/AAAA | Data da implementação |
| Início | HH:MM | Hora de início do desenvolvimento |
| Conclusão | HH:MM | Hora de conclusão |
| Testes Realizados | Número | Quantidade de testes até o sucesso |
| Versão | String | Versão da regra (v1, v2, etc.) |

### 3. Casos de Teste

Formato recomendado:
```
Entrada: [Descrição do XML/dados de entrada]
Esperado: [Resultado esperado]
Obtido: [Resultado obtido - deve ser igual ao esperado]
Status: ✅ PASSOU / ❌ FALHOU
```

---

## 🛠️ Geração Automática

Use o script `scripts/generate_rule_doc.py` para gerar documentação:

```bash
# Gerar documentação para uma regra específica
python scripts/generate_rule_doc.py --rule-id REGRA_TAXA_OBSERVACAO_CORRIGIR_HORARIOS

# Parâmetros obrigatórios
--rule-id         ID da regra no JSON/banco de dados

# Parâmetros opcionais
--start-time      Hora de início (HH:MM)
--end-time        Hora de conclusão (HH:MM)
--tests           Número de testes realizados
--details         Detalhes da solução (texto)
--author          Nome do autor
```

---

## ✅ Checklist de Documentação

Antes de finalizar a documentação, verifique:

- [ ] ID da regra corresponde ao arquivo JSON
- [ ] Descrição é clara e completa
- [ ] JSON está formatado e destacado corretamente
- [ ] Métricas de desenvolvimento preenchidas
- [ ] Casos de teste documentados
- [ ] Rodapé com data, hora e autor
- [ ] Arquivo salvo em `docs/regras/`
- [ ] Nome do arquivo segue o padrão

---

## 📚 Exemplo Completo

Veja: [`docs/regras/TAXA_OBSERVACAO_HORARIOS.html`](regras/TAXA_OBSERVACAO_HORARIOS.html)

---

*Última atualização: 26/01/2026 - AuditPlus v2.0*
