# Tests - Audit+ v2.0

Este diretório contém os testes automatizados do sistema.

## Estrutura

- `test_xml_parser.py` - Testes do módulo de parsing XML
- `fixtures/` - XMLs de exemplo para testes

## Rodar Testes

```bash
# Todos os testes
python -m pytest tests/ -v

# Teste específico
python -m pytest tests/test_xml_parser.py -v

# Com coverage
python -m pytest tests/ --cov=src --cov-report=html
```

## Princípios

- **Test-Driven Development (TDD)**: Testes escritos ANTES do código
- **Isolamento**: Cada teste é independente
- **Clareza**: Nomes descritivos (test_funcao_comportamento)
