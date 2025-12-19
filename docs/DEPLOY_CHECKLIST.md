# 🚀 Checklist de Deploy - AuditPlus v2.0

## ✅ Pré-Deploy (1 dia antes)

### Preparação de Ambiente

- [ ] Servidor de homologação configurado
- [ ] Dependências Python instaladas (Python 3.8+)
- [ ] Ambiente virtual criado
- [ ] Banco de dados SQLite inicializado
- [ ] Permissões de diretório configuradas

### Backup

- [ ] Backup completo do sistema atual
  ```bash
  python tools/backup.py --create
  ```
- [ ] Backup verificado e testado
- [ ] Plano de rollback documentado

### Testes Finais

- [ ] Todos os testes passando
  ```bash
  pytest tests/ -v
  ```
- [ ] Teste manual com amostra real
- [ ] Performance validada (> 500 guias/hora)

---

## 🎯 Deploy (Dia D)

### Fase 1: Setup (30 min)

- [ ] Clonar/copiar código para servidor
- [ ] Ativar ambiente virtual
  ```bash
  python -m venv venv
  venv\Scripts\activate  # Windows
  ```
- [ ] Instalar dependências
  ```bash
  pip install -r requirements.txt
  ```
- [ ] Configurar variáveis de ambiente

### Fase 2: Configuração (15 min)

- [ ] Copiar arquivos de configuração
- [ ] Verificar regras carregadas (105 regras)
  ```bash
  python -c "from src.business.rules.rule_engine import RuleEngine; e = RuleEngine(); e.load_all_rules(); print(f'Regras: {len(e.loaded_rules)}')"
  ```
- [ ] Criar diretórios necessários
  ```bash
  mkdir logs backups outputs
  ```

### Fase 3: Smoke Test (15 min)

- [ ] Executar aplicação
  ```bash
  python main.py
  ```
- [ ] Processar XML de teste
- [ ] Verificar logs
- [ ] Confirmar regras aplicadas

### Fase 4: Go-Live (Gradual)

**Dia 1**: 1-2 prestadores pequenos (< 100 guias)
- [ ] Processar lotes pequenos
- [ ] Monitorar logs intensivamente
- [ ] Dashboard aberto

**Dia 2-3**: Expandir para 5 prestadores (< 500 guias/dia)
- [ ] Monitorar taxa de erro
- [ ] Verificar performance
- [ ] Coletar feedback

**Semana 1**: Rollout completo
- [ ] Todos os prestadores
- [ ] Processar volumes reais
- [ ] Monitoramento contínuo

---

## 📊 Monitoramento Pós-Deploy

### Métricas Críticas (primeiras 48h)

- [ ] Taxa de erro < 5%
- [ ] Throughput > 500 guias/hora
- [ ] Uso de memória < 2GB
- [ ] Tempo de resposta < 1s/arquivo

### Verificações Diárias (primeira semana)

- [ ] Revisar dashboard
  ```bash
  python -c "from src.infrastructure.monitoring.dashboard import generate_dashboard; generate_dashboard()"
  ```
- [ ] Analisar alertas
- [ ] Verificar audit log de mudanças
- [ ] Coletar feedback dos usuários

---

## 🔙 Plano de Rollback

### Trigger de Rollback

Reverter se:
- Taxa de erro > 10%
- Crash/erro crítico recorrente
- Performance inaceitável (< 100 guias/hora)
- Feedback negativo unânime

### Procedimento de Rollback (< 15 min)

1. **Parar sistema atual**
   ```bash
   # Fechar aplicação
   ```

2. **Restaurar backup**
   ```bash
   python tools/backup.py --restore backups/backup_YYYYMMDD_HHMMSS
   ```

3. **Reiniciar sistema antigo**

4. **Comunicar stakeholders**

---

## 📞 Contatos de Emergência

- **Desenvolvedor**: Pedro Lucas
- **TI Responsável**: [Nome]
- **Product Owner**: [Nome]

---

## 📝 Pós-Mortem (1 semana após deploy)

- [ ] Revisar métricas coletadas
- [ ] Documentar problemas encontrados
- [ ] Identificar melhorias
- [ ] Atualizar documentação
- [ ] Planejar próxima versão

---

**Data de Deploy Planejada**: _____________  
**Responsável**: _____________  
**Aprovado por**: _____________
