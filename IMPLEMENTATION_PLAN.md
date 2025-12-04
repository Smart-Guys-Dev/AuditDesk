# RELATÓRIO GERENCIAL DE GLOSAS - IMPLEMENTATION PLAN

**Objetivo:** Criar relatório preciso mostrando glosas evitadas com valores REAIS dos XMLs

---

## 🎯 **REQUISITOS PRINCIPAIS**

### O que NÃO queremos (ROI atual):
- ❌ Valores estimados/fixos (R$ 5,50)
- ❌ Contabilização por regra aplicada
- ❌ Possibilidade de duplicação

### O que QUEREMOS:
- ✅ Valores REAIS do XML
- ✅ Contabilização por ITEM/GUIA (sem duplicar)
- ✅ Hierarquia: GLOSA_GUIA > GLOSA_ITEM
- ✅ Relatório individual por fatura
- ✅ Classificação correta das regras

---

## 🔒 **FASE 0: BACKUP E SEGURANÇA**

### 0.1. Criar Backup Completo

```bash
# Tags importantes
git tag backup-pre-relatorio-20241202
git push origin backup-pre-relatorio-20241202

# Commit de checkpoint
git add -A
git commit -m "CHECKPOINT: Antes de implementar relatório gerencial"
```

### 0.2. Branch de Desenvolvimento

```bash
# Criar branch separada
git checkout -b feature/relatorio-gerencial

# TODAS mudanças vão aqui
# NÃO tocar em dev até aprovar testes
```

**Critério de sucesso:** ✅ Pode reverter a qualquer momento com `git checkout dev`

---

## 📋 **FASE 1: ATUALIZAR CLASSIFICAÇÃO DAS REGRAS**

### 1.1. Corrigir Regras CNES

**Mudança:** `VALIDACAO` → `GLOSA_GUIA`

**Justificativa:** CNES errado = guia INTEIRA glosada

**Arquivos:**
- `src/config/regras/cnes.json` (todas as ~20 regras)

**Código:**
```json
"metadata_glosa": {
  "categoria": "GLOSA_GUIA",
  "impacto": "ALTO",
  "razao": "CNES incorreto causa glosa total da guia pela operadora",
  "contabilizar": true
}
```

### 1.2. Adicionar Metadata nas Regras de Participação

**Arquivos:**
- `src/config/regras_tp_participacao.json` (~500 regras)

**Script automático:** `scripts/add_metadata_participacao.py`

```python
# Para cada regra sem metadata:
"metadata_glosa": {
  "categoria": "GLOSA_ITEM",
  "impacto": "MEDIO",
  "razao": "Participação incorreta causa glosa do item pela operadora",
  "contabilizar": true
}
```

### 1.3. Lógica Condicional para REGRA_REMOVER_EQUIPE

**Problema:** Como saber se bloco estava correto ANTES de remover?

**Solução:**

```python
# ANTES de remover, verificar:
elemento = find_element('./ptu:equipe_Profissional')

# Tem CNPJ? → Estava ERRADO (PJ)
if elemento.find('./ptu:cdCnpjCpf/ptu:cd_cnpj'):
    categoria = "GLOSA_ITEM"
    contabilizar = True
    razao = "Equipe com PJ (incorreto) removida - evitou glosa"
    
# Tem CPF? → Estava CERTO (PF)
elif elemento.find('./ptu:cdCnpjCpf/ptu:cd_cpf'):
    categoria = "OTIMIZACAO"
    contabilizar = False
    razao = "Equipe com PF (correto) removida - apenas limpeza"
```

**Implementação:** Adicionar em `rule_engine.py` ANTES da remoção

---

## 💾 **FASE 2: NOVA ESTRUTURA DE BANCO**

### 2.1. Tabela: glosas_evitadas_items

```sql
CREATE TABLE glosas_evitadas_items (
    id INTEGER PRIMARY KEY,
    execution_id INTEGER,
    file_name TEXT,
    guia_id TEXT,               -- nr_GuiaPrestador
    seq_item INTEGER,           -- seq_item
    cd_servico TEXT,            -- código procedimento
    
    -- Valor REAL do XML
    valor_servico REAL,         -- vl_ServCobrado
    valor_taxa REAL,            -- tx_AdmServico  
    valor_total_item REAL,      -- soma
    
    -- Categoria
    categoria TEXT,             -- GLOSA_ITEM
    
    -- Regras aplicadas (JSON)
    regras_aplicadas TEXT,      -- ["REGRA_1", "REGRA_2"]
    
    -- Timestamp
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Índice único para evitar duplicação
    UNIQUE(execution_id, guia_id, seq_item)
)
```

### 2.2. Tabela: glosas_evitadas_guias

```sql
CREATE TABLE glosas_evitadas_guias (
    id INTEGER PRIMARY KEY,
    execution_id INTEGER,
    file_name TEXT,
    guia_id TEXT,               -- nr_GuiaPrestador
    
    -- Valor REAL do XML
    valor_total_guia REAL,      -- nr_GuiaIsPrestador ou soma itens
    qtd_itens INTEGER,          -- quantos procedimentos
    
    -- Categoria
    categoria TEXT,             -- GLOSA_GUIA
    
    -- Regras aplicadas
    regras_aplicadas TEXT,      -- ["REGRA_CNES", ...]
    
    -- Timestamp
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Índice único
    UNIQUE(execution_id, guia_id)
)
```

### 2.3. Tabela: otimizacoes (não contabilizar)

```sql
CREATE TABLE otimizacoes (
    id INTEGER PRIMARY KEY,
    execution_id INTEGER,
    file_name TEXT,
    guia_id TEXT,
    regra_id TEXT,
    descricao TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

---

## 🔧 **FASE 3: LÓGICA DE TRACKING**

### 3.1. Algoritmo Principal

```python
def processar_correcao(execution_id, file_name, xml_tree, rule):
    # 1. Obter categoria da regra
    metadata = rule.get("metadata_glosa", {})
    categoria = metadata.get("categoria", "OTIMIZACAO")
    contabilizar = metadata.get("contabilizar", False)
    
    # Se não contabiliza, apenas logar
    if not contabilizar or categoria == "OTIMIZACAO":
        log_otimizacao(execution_id, file_name, rule['id'])
        return
    
    # 2. Identificar o elemento afetado
    elemento = localizar_elemento_afetado(xml_tree, rule)
    
    # 3. Extrair identificadores
    guia_id = extrair_nr_guia_prestador(elemento)
    
    # 4. GLOSA_GUIA ou GLOSA_ITEM?
    if categoria == "GLOSA_GUIA":
        processar_glosa_guia(execution_id, file_name, guia_id, rule, elemento)
    
    elif categoria == "GLOSA_ITEM":
        seq_item = extrair_seq_item(elemento)
        processar_glosa_item(execution_id, file_name, guia_id, seq_item, rule, elemento)
```

### 3.2. Processar Glosa de GUIA

```python
def processar_glosa_guia(execution_id, file_name, guia_id, rule, elemento):
    # Verificar se guia JÁ foi registrada
    existing = db.query(GlosaGuia).filter_by(
        execution_id=execution_id,
        guia_id=guia_id
    ).first()
    
    if existing:
        # Adicionar regra à lista
        regras = json.loads(existing.regras_aplicadas)
        if rule['id'] not in regras:
            regras.append(rule['id'])
            existing.regras_aplicadas = json.dumps(regras)
            db.commit()
    else:
        # Primeira vez: extrair valor total da guia
        valor_total = extrair_valor_total_guia(elemento)
        qtd_itens = contar_procedimentos(elemento)
        
        nova_guia = GlosaGuia(
            execution_id=execution_id,
            file_name=file_name,
            guia_id=guia_id,
            valor_total_guia=valor_total,
            qtd_itens=qtd_itens,
            categoria="GLOSA_GUIA",
            regras_aplicadas=json.dumps([rule['id']])
        )
        db.add(nova_guia)
        db.commit()
```

### 3.3. Processar Glosa de ITEM

```python
def processar_glosa_item(execution_id, file_name, guia_id, seq_item, rule, elemento):
    # IMPORTANTE: Verificar se guia já tem GLOSA_GUIA
    tem_glosa_guia = db.query(GlosaGuia).filter_by(
        execution_id=execution_id,
        guia_id=guia_id
    ).first()
    
    if tem_glosa_guia:
        # Guia INTEIRA foi salva → NÃO contar item individual
        # Apenas adicionar à lista de otimizações
        log_otimizacao(f"Item {seq_item} não contado (guia já salva)")
        return
    
    # Verificar se item JÁ foi registrado
    existing = db.query(GlosaItem).filter_by(
        execution_id=execution_id,
        guia_id=guia_id,
        seq_item=seq_item
    ).first()
    
    if existing:
        # Adicionar regra à lista (NÃO duplicar valor!)
        regras = json.loads(existing.regras_aplicadas)
        if rule['id'] not in regras:
            regras.append(rule['id'])
            existing.regras_aplicadas = json.dumps(regras)
            db.commit()
    else:
        # Primeira vez: extrair valores DO XML
        procedimento = localizar_procedimento(elemento, seq_item)
        
        vl_servico = float(procedimento.find('.//ptu:vl_ServCobrado').text or 0)
        tx_adm = float(procedimento.find('.//ptu:tx_AdmServico').text or 0)
        cd_servico = procedimento.find('.//ptu:cd_Servico').text
        
        novo_item = GlosaItem(
            execution_id=execution_id,
            file_name=file_name,
            guia_id=guia_id,
            seq_item=seq_item,
            cd_servico=cd_servico,
            valor_servico=vl_servico,
            valor_taxa=tx_adm,
            valor_total_item=vl_servico + tx_adm,
            categoria="GLOSA_ITEM",
            regras_aplicadas=json.dumps([rule['id']])
        )
        db.add(novo_item)
        db.commit()
```

### 3.4. Funções Auxiliares

```python
def extrair_valor_total_guia(elemento):
    """Extrai valor total da guia do XML"""
    # Tentar nr_GuiaIsPrestador primeiro
    guia_element = elemento.xpath('ancestor::ptu:guiaInternacao | ancestor::ptu:guiaSADT | ancestor::ptu:guiaHonorarios | ancestor::ptu:guiaConsulta')[0]
    
    valor_tag = guia_element.find('.//ptu:nr_GuiaIsPrestador')
    if valor_tag is not None and valor_tag.text:
        return float(valor_tag.text)
    
    # Se não existir, somar todos procedimentos
    procedimentos = guia_element.findall('.//ptu:procedimentosExecutados/ptu:procedimentos')
    total = 0
    for proc in procedimentos:
        vl_serv = float(proc.find('.//ptu:vl_ServCobrado').text or 0)
        tx_adm = float(proc.find('.//ptu:tx_AdmServico').text or 0)
        total += vl_serv + tx_adm
    
    return total

def extrair_nr_guia_prestador(elemento):
    """Extrai número da guia do prestador"""
    guia = elemento.xpath('ancestor::ptu:guiaInternacao | ancestor::ptu:guiaSADT | ancestor::ptu:guiaHonorarios | ancestor::ptu:guiaConsulta')[0]
    return guia.find('.//ptu:nr_GuiaPrestador').text

def extrair_seq_item(elemento):
    """Extrai seq_item do procedimento"""
    proc = elemento.xpath('ancestor::ptu:procedimentosExecutados')[0]
    return int(proc.find('.//ptu:seq_item').text)
```

---

## 📊 **FASE 4: RELATÓRIO INDIVIDUAL**

### 4.1. Estrutura do Relatório

```
═══════════════════════════════════════════════
  RELATÓRIO DE AUDITORIA - FATURA N045940
═══════════════════════════════════════════════

Data: 02/12/2024
Período: Novembro 2024
Processado por: Audit Plus v2.0

─────────────────────────────────────────────
RESUMO GERAL
─────────────────────────────────────────────

Arquivos processados: 156
Guias salvas (GLOSA_GUIA): 12
Itens corrigidos (GLOSA_ITEM): 450

TOTAL VALOR PROTEGIDO: R$ 425.380,00

─────────────────────────────────────────────
DETALHAMENTO - GUIAS SALVAS
─────────────────────────────────────────────

Guia: 257855217 | Arquivo: N045940_pre.051
  Correção: CNES incorreto → corrigido
  Valor Total Guia: R$ 18.327,00
  Procedimentos na guia: 8
  Regras aplicadas:
    • REGRA_GARANTIR_CNES_RESGATARE

Guia: 257855218 | Arquivo: N045940_pre.051
  Correção: Médico auditor faltando → adicionado
  Valor Total Guia: R$ 32.150,00
  Procedimentos na guia: 12
  Regras aplicadas:
    • REGRA_GARANTIR_NOME_MEDICO_AUDITOR
    • REGRA_GARANTIR_CRM_MEDICO_AUDITOR

─────────────────────────────────────────────
DETALHAMENTO - ITENS CORRIGIDOS
─────────────────────────────────────────────

Guia: 257855220 | Item: 1 | Proc: 40160 (Fisioterapia)
  Valor Item: R$ 43,00 (R$ 40,95 + R$ 2,05)
  Correções:
    • tp_Participacao corrigido: 11 → 12
    • Conselho corrigido: CREFONO → CREFITO
  
Guia: 257855220 | Item: 2 | Proc: 20104 (Consulta)
  Valor Item: R$ 125,00 (R$ 120,00 + R$ 5,00)
  Correções:
    • CBO corrigido: 999999 → 225125

─────────────────────────────────────────────
OTIMIZAÇÕES (Não Contabilizadas)
─────────────────────────────────────────────

• 45 blocos de equipe removidos (opcional)
• 120 tags reordenadas (conformidade XSD)

═══════════════════════════════════════════════
```

### 4.2. Exportação

**Formatos:**
- ✅ PDF (relatório visual)
- ✅ Excel (planilhas detalhadas)
- ✅ JSON (dados brutos)

**Função:**
```python
def gerar_relatorio_individual(execution_id):
    # Buscar dados
    guias = db.query(GlosaGuia).filter_by(execution_id=execution_id).all()
    itens = db.query(GlosaItem).filter_by(execution_id=execution_id).all()
    
    # Calcular totais
    total_guias = sum(g.valor_total_guia for g in guias)
    total_itens = sum(i.valor_total_item for i in itens)
    
    # Gerar relatório
    relatorio = {
        'resumo': {
            'guias_salvas': len(guias),
            'itens_corrigidos': len(itens),
            'valor_total_protegido': total_guias + total_itens
        },
        'detalhamento_guias': [...],
        'detalhamento_itens': [...]
    }
    
    # Exportar
    export_pdf(relatorio, f"relatorio_{execution_id}.pdf")
    export_excel(relatorio, f"relatorio_{execution_id}.xlsx")
```

---

## ✅ **FASE 5: TESTES DE VALIDAÇÃO**

### 5.1. Testes Unitários

**Arquivo:** `tests/test_glosa_tracking.py`

```python
def test_glosa_guia_nao_duplica():
    # Aplicar 2 regras na mesma guia
    # Verificar que valor foi contado 1x só
    
def test_glosa_item_nao_duplica():
    # Aplicar 2 regras no mesmo item
    # Verificar que valor foi contado 1x só
    
def test_hierarquia_guia_item():
    # Guia com GLOSA_GUIA + vários itens com GLOSA_ITEM
    # Verificar que contou só GUIA (não somou itens)
    
def test_remover_equipe_pj_vs_pf():
    # Remover equipe com CNPJ → deve contabilizar
    # Remover equipe com CPF → NÃO deve contabilizar
```

### 5.2. Teste Manual

**Cenário 1:** Arquivo com CNES errado
```
Esperado:
  - 1 guia salva
  - Valor = soma TODOS itens
  - NÃO contar itens individuais
```

**Cenário 2:** Arquivo sem erro de guia, mas 3 itens com participação errada
```
Esperado:
  - 0 guias salvas
  - 3 itens corrigidos
  - Valor = soma dos 3 itens
```

**Cenário 3:** Mesmo item com 2 regras aplicadas
```
Esperado:
  - 1 item registrado
  - Valor contado 1x
  - 2 regras na lista
```

### 5.3. Validação com Cálculo Manual

**Script:** `scripts/valida_calculo_manual.py`

```python
# Processar 1 arquivo
# Abrir XML manualmente
# Calcular valores esperados
# Comparar com resultado do sistema
# Deve bater 100%
```

---

## 🚀 **FASE 6: DASHBOARD & PAINEL GERENCIAL**

### 6.1. KPIs Principais

```python
class DashboardGlosas:
    # Cards superiores
    card_guias_salvas = KPICard("Guias Salvas", "R$ XXX", icon="🛡️")
    card_itens_corrigidos = KPICard("Itens Corrigidos", "R$ XXX", icon="✅")
    card_valor_total = KPICard("Valor Total Protegido", "R$ XXX", icon="💰")
    card_taxa_sucesso = KPICard("Taxa de Sucesso", "XX%", icon="📊")
```

### 6.2. Gráficos

- **Pizza:** Distribuição GLOSA_GUIA vs GLOSA_ITEM
- **Barras:** Top 10 regras que mais economizaram
- **Linha:** Evolução temporal (mensal)
- **Tabela:** Detalhamento por arquivo

### 6.3. Filtros

- Período (mês, trimestre, ano, customizado)
- Tipo de glosa (GUIA, ITEM, ambos)
- Arquivo específico
- Regra específica

---

## 📦 **ESTRUTURA DE ARQUIVOS**

```
src/
├── relatorio_glosas/
│   ├── __init__.py
│   ├── tracker.py           # Lógica de tracking
│   ├── extractor.py         # Extrair valores do XML
│   ├── reporter.py          # Gerar relatórios
│   ├── exporter.py          # PDF/Excel/JSON
│   └── models.py            # Modelos do banco
│
├── database/
│   ├── db_manager.py        # ATUALIZAR
│   └── models.py            # Adicionar novos models
│
└── rule_engine.py           # Integrar tracking

scripts/
├── add_metadata_participacao.py
├── corrigir_metadata_cnes.py
├── backup_automatico.py
└── valida_calculo_manual.py

tests/
└── test_glosa_tracking.py
```

---

## 📋 **CHECKLIST DE IMPLEMENTAÇÃO**

### Preparação
- [ ] Criar backup (tag + commit)
- [ ] Criar branch `feature/relatorio-gerencial`
- [ ] Atualizar `task.md` com itens

### Fase 1: Classificação
- [ ] Script: corrigir CNES → GLOSA_GUIA
- [ ] Script: adicionar metadata em participação
- [ ] Implementar lógica condicional REGRA_REMOVER_EQUIPE
- [ ] Testar todas as mudanças de metadata

### Fase 2: Banco de Dados
- [ ] Criar models (GlosaGuia, GlosaItem, Otimizacao)
- [ ] Criar migração/schema
- [ ] Testar criação de tabelas

### Fase 3: Tracking
- [ ] Implementar `tracker.py`
- [ ] Implementar `extractor.py`
- [ ] Integrar em `rule_engine.py`
- [ ] Testes unitários

### Fase 4: Relatório
- [ ] Implementar `reporter.py`
- [ ] Implementar `exporter.py` (PDF/Excel)
- [ ] Testar geração de relatórios

### Fase 5: Testes
- [ ] Testes unitários (100% coverage)
- [ ] Teste manual (3 cenários)
- [ ] Validação cálculo manual
- [ ] Correção de bugs encontrados

### Fase 6: Dashboard
- [ ] Criar página dashboard glosas
- [ ] Implementar KPIs
- [ ] Implementar gráficos
- [ ] Implementar filtros

### Produção
- [ ] Pedro aprova testes
- [ ] Merge para `dev`
- [ ] Testar em produção (arquivo real)
- [ ] Gerar relatório para gerente
- [ ] Feedback final

---

## ⚠️ **PONTOS DE ATENÇÃO**

### Críticos
1. **NUNCA duplicar valores** (implementar UNIQUE constraints)
2. **Hierarquia GUIA > ITEM** (verificar SEMPRE antes de contar item)
3. **Lógica condicional REMOVER_EQUIPE** (PJ vs PF)

### Importantes
4. Extrair valores corretos do XML (testar XPath)
5. Tratar casos de valores ausentes (default 0)
6. Log detalhado para debug

### Opcionais
7. Cache de resultados para dashboard rápido
8. Exportação automática ao final de cada processamento
9. Integração com sistema de notificações

---

## 🎯 **CRITÉRIO DE SUCESSO**

**Para aprovar merge em produção:**

✅ Todos os testes passando (verde)  
✅ Validação manual conferida (valores corretos)  
✅ Nenhuma duplicação encontrada  
✅ Hierarquia funcionando (GUIA > ITEM)  
✅ Relatório PDF gerado corretamente  
✅ Dashboard funcionando  
✅ **Pedro aprova testes** 👍

---

**PRÓXIMO PASSO:** Implementar Fase 0 (Backup) + Fase 1 (Classificação)

Pronto para começar? 🚀
