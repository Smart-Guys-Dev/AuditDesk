# ❓ FAQ - Perguntas Frequentes

## AuditPlus v2.0

---

## Geral

**Q: O que é o AuditPlus v2.0?**  
A: Sistema automatizado de auditoria de contas médicas que valida e corrige arquivos XML PTU/TISS, aplicando 105 regras para evitar glosas.

**Q: Quais arquivos posso processar?**  
A: Arquivos XML no padrão PTU da Unimed ou TISS da ANS.

**Q: Quantos arquivos posso processar de uma vez?**  
A: Recomendado até 500 arquivos por lote. Para mais, divida em lotes menores.

---

## Uso

**Q: Como sei se minhas correções foram aplicadas?**  
A: O relatório mostra todas as regras aplicadas, marcadas com ✅.

**Q: Posso desfazer as correções?**  
A: Sim, o arquivo original é preservado. Salve o corrigido com nome diferente.

**Q: Quanto tempo demora para processar?**  
A: ~0.3 segundos por arquivo. 1000 arquivos = ~5 minutos.

---

## Problemas Comuns

**Q: "Arquivo não pôde ser carregado"**  
A: Verifique se:
- Arquivo está em UTF-8
- XML está bem-formado
- Não está corrompido

**Q: "Nenhuma regra foi aplicada"**  
A: Possíveis causas:
- Arquivo já está correto
- Regras estão desabilitadas (contacte admin)
- Tipo de guia não suportado

**Q: Sistema está lento**  
A: Causas:
- Arquivo muito grande (> 10MB)
- Muitos arquivos no lote (> 500)
- Pouca memória disponível

**Soluções**:
- Dividir arquivos em lotes menores
- Fechar outros programas
- Reiniciar sistema

---

## Regras

**Q: Quantas regras existem?**  
A: 105 regras ativas, divididas em:
- GLOSA_GUIA: evita rejeição de guia inteira
- GLOSA_ITEM: evita rejeição de itens
- OTIMIZAÇÃO: melhora qualidade

**Q: Posso customizar as regras?**  
A: Não pelo usuário. Contacte administrador para mudanças.

**Q: Como sei quais regras foram aplicadas no meu arquivo?**  
A: Confira o relatório gerado após processamento.

---

## Segurança

**Q: Meus dados ficam salvos?**  
A: Sistema funciona 100% local (on-premise). Nenhum dado sai do computador.

**Q: Quem tem acesso aos meus arquivos?**  
A: Apenas você e administradores do sistema.

**Q: O sistema faz backup automático?**  
A: Não. Sempre mantenha backup dos seus arquivos originais.

---

## Performance

**Q: Qual o throughput esperado?**  
A: ~500-2000 arquivos por hora, dependendo do tamanho e complexidade.

**Q: Quanto de memória o sistema usa?**  
A: Tipicamente 200-500MB. Até 2GB para lotes grandes.

**Q: Posso processar em paralelo?**  
A: Não recomendado. Processe um lote por vez.

---

## Erros Específicos

**Q: "XML inválido"**  
A: Arquivo não está em formato XML válido. Use validador XML externo.

**Q: "Namespace não encontrado"**  
A: Arquivo pode não ser PTU/TISS padrão. Verifique o schema.

**Q: "Regra XXXX falhou"**  
A: Regra específica teve problema. Note no relatório e contacte admin.

---

## Suporte

**Q: Onde encontro ajuda?**  
A: 
1. Este FAQ
2. Manual do Usuário (`docs/MANUAL_USUARIO.md`)
3. Runbook Admin (`docs/RUNBOOK_ADMIN.md`)
4. Equipe de TI

**Q: Como reporto um bug?**  
A: 
1. Note o erro exato
2. Salve o arquivo problemático
3. Capture screenshot se possível
4. Contacte TI com estas informações

---

**Desenvolvido por**: Pedro Lucas  
**Versão**: 2.0  
**Última atualização**: Dezembro 2025
