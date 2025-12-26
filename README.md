# Audit+ v2.0

**Sistema de automação e validação de arquivos PTU para auditoria médica.**

Desenvolvido por **Pedro Lucas Lima de Freitas**.

---

## 📦 Instalação

### Requisitos
- Python 3.8 ou superior
- pip

### Passos

1. Clone ou baixe o repositório

2. Crie um ambiente virtual (recomendado):
```bash
python -m venv venv
```

3. Ative o ambiente virtual:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. Instale as dependências:
```bash
pip install -r requirements.txt
```

---

## 🚀 Uso

Execute a aplicação:
```bash
python main.py
```

---

## 🔧 Funcionalidades

### 📄 Processador XML
- Importação automática de faturas em arquivos ZIP
- Extração e processamento de XMLs
- Geração de relatórios em Excel e CSV

### 👥 Distribuição Inteligente
- Distribuição automática de faturas entre auditores
- Balanceamento de carga
- Organização por pastas

### ✓ Validação TISS
- Validação de regras de negócio
- Validação de estrutura XSD
- Verificação de internações de curta permanência
- Relatórios detalhados de validação

### # Atualização de Hash
- Atualização seletiva de hash em arquivos específicos
- Recriação de arquivos ZIP
- Modo batch para todos os arquivos

---

## 📁 Estrutura do Projeto

```
AuditPlusv2.0/
├── main.py                 # Ponto de entrada da aplicação
├── requirements.txt        # Dependências Python
├── src/
│   ├── assets/            # Recursos (ícones, estilos)
│   ├── config/            # Arquivos de configuração JSON
│   ├── schemas/           # Schemas XSD para validação
│   ├── constants.py       # Constantes da aplicação
│   ├── logger_config.py   # Configuração de logging
│   ├── main_window.py     # Interface gráfica principal
│   ├── workflow_controller.py  # Controlador de fluxo
│   ├── xml_parser.py      # Parser de XMLs
│   ├── rule_engine.py     # Motor de regras
│   ├── file_manager.py    # Gerenciamento de arquivos
│   ├── hash_calculator.py # Cálculo de hash
│   ├── data_manager.py    # Gerenciamento de dados
│   ├── distribution_engine.py  # Motor de distribuição
│   └── report_generator.py     # Geração de relatórios
└── audit_plus.log         # Arquivo de log (gerado automaticamente)
```

---

## 🛠️ Tecnologias

- **Python 3.8+**
- **PyQt6** - Interface gráfica
- **lxml** - Processamento XML
- **openpyxl** - Geração de relatórios Excel

---

## 📝 Licença

Propriedade de **Pedro Lucas Lima de Freitas**.  
Todos os direitos reservados.

---

## 👨‍💻 Suporte

Para suporte ou dúvidas, entre em contato com Pedro Lucas Lima de Freitas.

---

**Audit+ v2.0** - Desenvolvido por Pedro Lucas Lima de Freitas
# AuditPlus_Desktop
