# 📖 Manual do Usuário - AuditPlus v2.0

**Sistema de auditoria de contas médicas e validação de arquivos PTU/XML**

---

## 🎯 Visão Geral

O AuditPlus v2.0 processa automaticamente arquivos XML PTU/TISS, aplicando 105 regras de validação e correção para evitar glosas e rejeições.

---

## 🚀 Início Rápido

### 1. Abrir o Sistema

Execute `main.py` no diretório do projeto.

### 2. Carregar Arquivos

1. Clique em **"Validador PTU XML"**
2. Clique em **"Carregar XML(s)"**
3. Selecione um ou múltiplos arquivos XML

### 3. Processar

- O sistema aplica automaticamente as 105 regras
- Correções são feitas em tempo real
- Resultados aparecem na interface

### 4. Salvar Resultados

- **Salvar XML corrigido**: Exporta arquivo com correções
- **Relatório**: Gera relatório de mudanças aplicadas

---

## 📊 Interpretando Resultados

### Tipos de Regras

**🔴 GLOSA_GUIA** - Evita rejeição da guia inteira
- Ex: tp_Atendimento incorreto
- Ex: CNES inválido

**🟡 GLOSA_ITEM** - Evita rejeição de itens específicos
- Ex: Procedimento sem equipe obrigatória
- Ex: CBO inválido

**🟢 OTIMIZAÇÃO** - Melhora qualidade do arquivo
- Ex: Ordem de elementos
- Ex: Formatação

### Cores no Relatório

- ✅ **Verde**: Correção aplicada com sucesso
- ⚠️ **Amarelo**: Aviso (não crítico)
- ❌ **Vermelho**: Erro que precisa atenção manual

---

## ❓ Troubleshooting

### Arquivo não carrega

**Causa**: XML malformado ou encoding incorreto  
**Solução**: Verifique se o arquivo está em UTF-8

### Muitas glosas ainda aparecem

**Causa**: Regra pode estar desabilitada  
**Solução**: Contacte administrador

### Processamento está lento

**Causa**: Arquivo muito grande (> 10MB)  
**Solução**: Divida em lotes menores

---

## 📞 Suporte

Para dúvidas ou problemas:
1. Consulte este manual
2. Verifique o log de erros
3. Entre em contato com TI

---

**Versão**: 2.0  
**Desenvolvido por**: Pedro Lucas  
**Última atualização**: Dezembro 2025
