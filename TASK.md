# TASK: Relatório Gerencial de Glosas Evitadas

## 🎯 **OBJETIVO**
Criar relatório gerencial mostrando glosas evitadas com valores REAIS (não estimados), sem duplicação, com hierarquia GUIA > ITEM.

---

## 📋 **FASE 0: BACKUP E SEGURANÇA**

- [x] Criar tag de backup (`backup-pre-relatorio-20241202`)
- [x] Criar commit checkpoint (3bf7e0d)
- [x] Criar branch `feature/relatorio-gerencial`
- [x] Confirmar que pode reverter com `git checkout dev`

---

## 📋 **FASE 1: CLASSIFICAÇÃO DE REGRAS**

### Correção de CNES
- [x] Criar script `corrigir_metadata_cnes.py`
- [x] Atualizar todas regras CNES: VALIDACAO → GLOSA_GUIA
- [x] Testar script em arquivo temporário
- [x] Aplicar em produção (11 regras)
- [x] Commit: "Adicionar metadata em regras CNES"

### Metadata em Participação
- [x] Criar script `add_metadata_participacao.py`
- [x] Adicionar metadata em 25 regras de participação
- [x] Testar em arquivo temporário
- [x] Aplicar em produção
- [x] Commit: "Adicionar metadata em regras de participação"

### Lógica Condicional REMOVER_EQUIPE
- [ ] Implementar verificação PJ vs PF em `rule_engine.py`
- [ ] Se CNPJ → categoria=GLOSA_ITEM, contabilizar=True
- [ ] Se CPF → categoria=OTIMIZACAO, contabilizar=False
- [ ] Testar com XMLs de exemplo
- [ ] Commit: "Lógica condicional para REGRA_REMOVER_EQUIPE"

---

## 📋 **FASE 2: ESTRUTURA DE BANCO**

### Novos Models
- [x] Criar `src/relatorio_glosas/models.py`
- [x] Model: `GlosaGuia` (execution_id, guia_id, valor_total, regras)
- [x] Model: `GlosaItem` (execution_id, guia_id, seq_item, valor, regras)
- [x] Model: `Otimizacao` (execution_id, regra_id, descricao)
- [x] Adicionar UNIQUE constraints

### Migração
- [x] Criar script de migração do banco
- [x] Testar criação de tabelas
- [x] Commit: "Adicionar tabelas para tracking de glosas"

---

## 📋 **FASE 3: LÓGICA DE TRACKING**

### Extração de Valores
- [x] Criar `src/relatorio_glosas/extractor.py`
- [x] Função: `extrair_valor_total_guia(elemento)`
- [x] Função: `extrair_nr_guia_prestador(elemento)`
- [x] Função: `extrair_seq_item(elemento)`
- [x] Função: `extrair_valores_item(procedimento)` → vl_ServCobrado + tx_AdmServico
- [ ] Testar com XMLs reais

### Tracker Principal
- [x] Criar `src/relatorio_glosas/tracker.py`
- [x] Função: `processar_correcao()` (dispatcher)
- [x] Função: `processar_glosa_guia()` com anti-duplicação
- [x] Função: `processar_glosa_item()` com hierarquia
- [x] Função: `log_otimizacao()` (não contabilizar)
- [ ] Testar lógica de não-duplicação

### Integração
- [x] Modificar `rule_engine.apply_rules_to_xml()`
- [x] Chamar tracker APÓS aplicar cada regra
- [x] Passar execution_id, file_name, xml_tree, rule
- [x] Testar integração completa
- [x] Commit: "Implementar tracking de glosas com valores reais"

---

## 📋 **FASE 4: RELATÓRIO INDIVIDUAL**

### Reporter
- [x] Criar `src/relatorio_glosas/reporter.py`
- [x] Função: `gerar_relatorio_individual(execution_id)`
- [x] Buscar dados: guias salvas
- [x] Buscar dados: itens corrigidos
- [x] Buscar dados: otimizações
- [x] Calcular totais e resumo

### Exporter
- [x] Criar `src/relatorio_glosas/exporter.py`
- [x] Função: `formatar_relatorio_texto()` (relatório em texto)
- [x] Função: `exportar_para_json()` (dados brutos)
- [x] Função: `exportar_para_arquivo()` (txt formatado)
- [ ] Opcional: `export_pdf()` (relatório visual)
- [ ] Testar todas exportações
- [ ] Commit: "Implementar geração de relatórios"

---

## 📋 **FASE 5: TESTES**

### Testes Unitários
- [ ] Criar `tests/test_glosa_tracking.py`
- [ ] Test: `test_glosa_guia_nao_duplica()`
- [ ] Test: `test_glosa_item_nao_duplica()`
- [ ] Test: `test_hierarquia_guia_item()`
- [ ] Test: `test_remover_equipe_pj_vs_pf()`
- [ ] Test: `test_extractor_valores_xml()`
- [ ] Todos testes passando (verde)

### Teste Manual
- [ ] Cenário 1: Arquivo com CNES errado (GLOSA_GUIA)
- [ ] Cenário 2: Arquivo com 3 itens erro participação (GLOSA_ITEM)
- [ ] Cenário 3: Mesmo item com 2 regras aplicadas (sem duplicar)
- [ ] Validar valores contra cálculo manual
- [ ] Documentar resultados

### Validação com XML Real
- [ ] Processar 1 fatura completa (156 arquivos)
- [ ] Abrir alguns XMLs e calcular manualmente
- [ ] Comparar com relatório gerado
- [ ] Valores devem bater 100%
- [ ] Corrigir discrepâncias

---

## 📋 **FASE 6: DASHBOARD**

### Página Dashboard Glosas
- [ ] Criar `src/dashboard_glosas_page.py`
- [ ] Implementar layout com KPIs
- [ ] Card: Guias Salvas (R$)
- [ ] Card: Itens Corrigidos (R$)
- [ ] Card: Valor Total Protegido (R$)
- [ ] Card: Taxa de Sucesso (%)

### Gráficos
- [ ] Gráfico pizza: GLOSA_GUIA vs GLOSA_ITEM
- [ ] Gráfico barras: Top 10 regras
- [ ] Tabela: Detalhamento por arquivo
- [ ] Opcional: Gráfico linha temporal

### Funcionalidades
- [ ] Filtro por período
- [ ] Filtro por tipo (GUIA/ITEM)
- [ ] Botão: Exportar Relatório
- [ ] Botão: Atualizar Dados
- [ ] Commit: "Adicionar dashboard de glosas"

---

## 📋 **APROVAÇÃO PARA PRODUÇÃO**

### Pré-requisitos
- [ ] Todos testes unitários passando
- [ ] Teste manual validado
- [ ] Cálculo conferido manualmente
- [ ] Nenhuma duplicação encontrada
- [ ] Hierarquia GUIA > ITEM funcionando
- [ ] Relatório gerado corretamente
- [ ] Dashboard funcionando

### Aprovação Final
- [ ] **Pedro testa em dev**
- [ ] **Pedro aprova resultados**
- [ ] **Pedro autoriza merge**

### Deploy
- [ ] Merge `feature/relatorio-gerencial` → `dev`
- [ ] Testar em produção com fatura real
- [ ] Gerar relatório para gerente
- [ ] Coletar feedback
- [ ] Ajustes finais (se necessário)

---

## ✅ **CONCLUSÃO**

- [ ] Sistema em produção
- [ ] Relatório apresentado à gerente
- [ ] Feedback positivo recebido
- [ ] Documentação atualizada
- [ ] **TAREFA CONCLUÍDA!** 🎉
