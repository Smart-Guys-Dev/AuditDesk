# 🔧 Runbook Operacional - Glox

**Para Administradores e Equipe de TI**

---

## 📋 Operações Diárias

### Iniciar Sistema

```bash
cd C:\Users\pedro.freitas\Gloxv2.0
python main.py
```

### Verificar Logs

Logs principais:
- `logs/application.log` - Log geral
- `logs/.audit_log.jsonl` - Mudanças em regras
- `logs/alerts.log` - Alertas de sistema

```bash
# Ver últimas 50 linhas
tail -50 logs/application.log

# Procurar erros
grep "ERROR" logs/application.log
```

### Monitorar Performance

```bash
# Gerar dashboard
python -c "from src.infrastructure.monitoring.dashboard import generate_dashboard; generate_dashboard()"

# Abrir dashboard.html no navegador
```

---

## 🚨 Procedimentos de Emergência

### Regra Causando Problemas

**Sintoma**: Glosas incorretas, erros em produção

**Ação Imediata** (< 2 minutos):
```bash
python tools/manage_rules.py disable \
  --file regras_grupo_XXXX.json \
  --rule-id REGRA_PROBLEMATICA \
  --reason "Bug crítico - Ticket #XXXX" \
  --user seu_nome
```

**Verificar**:
```bash
python tools/manage_rules.py status \
  --file regras_grupo_XXXX.json \
  --rule-id REGRA_PROBLEMATICA
```

### Taxa de Erro Alta (> 10%)

1. Verificar dashboard: `dashboard.html`
2. Analisar `logs/application.log`
3. Identificar padrão de erros
4. Desabilitar regra problemática se necessário

### Sistema Lento

1. Verificar uso de memória: Task Manager
2. Se > 4GB: Reiniciar sistema
3. Dividir lotes grandes em menores (< 500 arquivos)

---

## 🔄 Rollback de Configuração

### Quando fazer rollback

- Após mudança em regras que causou problemas
- Para restaurar configuração estável conhecida

### Como fazer

1. Listar versões disponíveis:
```bash
python tools/manage_rules.py versions \
  --file regras_grupo_XXXX.json
```

2. Fazer rollback:
```bash
python tools/manage_rules.py rollback \
  --file regras_grupo_XXXX.json \
  --timestamp 20251219_140530 \
  --user seu_nome
```

3. Verificar audit log:
```bash
python tools/manage_rules.py audit-log --limit 10
```

---

## 📊 Troubleshooting Técnico

### Import Error / Module Not Found

**Causa**: Ambiente virtual não ativado

**Solução**:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Banco de Dados Bloqueado

**Causa**: Múltiplas instâncias rodando

**Solução**:
1. Fechar todas as instâncias
2. Deletar `*.lock` files
3. Reiniciar

### XML Parser Crashes

**Causa**: XML extremamente grande ou malformado

**Solução**:
- Validar XML manualmente primeiro
- Aumentar memória disponível
- Processar em lotes menores

---

## 🔐 Segurança

### Backup de Configurações

Arquivos críticos para backup:
- `src/config/regras_grupo_*.json`
- `src/config/.versions/` (histórico)
- `database/Glox.db`

```bash
# Backup manual
cp -r src/config/ backup/config_$(date +%Y%m%d)/
```

### Audit Log

Todo acesso e mudança é registrado em:
- `src/config/.audit_log.jsonl`

Nunca deletar este arquivo!

---

## 📞 Escalonamento

### Nível 1: Operações

- Problemas de uso
- Arquivos não processam
- **SLA**: 2 horas

### Nível 2: TI

- Erros técnicos
- Performance
- **SLA**: 4 horas

### Nível 3: Desenvolvedor

- Bugs em regras
- Mudanças no sistema
- **SLA**: 1 dia útil

---

## 📝 Checklist Pré-Produção

Antes de cada deploy:

- [ ] Backup de configurações atual
- [ ] Testes em homologação
- [ ] Verificar logs por erros
- [ ] Confirmar regras habilitadas corretas
- [ ] Preparar rollback se necessário
- [ ] Comunicar stakeholders

---

## 🛠️ Comandos úteis

```bash
# Ver regras desabilitadas
python tools/manage_rules.py list-disabled

# Audit log
python tools/manage_rules.py audit-log --limit 20

# Gerar dashboard
python -c "from src.infrastructure.monitoring.dashboard import generate_dashboard; generate_dashboard()"

# Executar testes
pytest tests/unit/ -v

# Ver cobertura de testes
pytest tests/ --cov=src --cov-report=html
```

---

**Desenvolvido por**: Pedro Lucas  
**Última atualização**: Dezembro 2025  
**Versão**: 2.0
