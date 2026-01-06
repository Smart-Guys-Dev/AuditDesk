# Glox

**Sistema de validação e correção automática de arquivos PTU/TISS para faturamento médico.**

Desenvolvido por **Pedro Lucas Lima de Freitas**.

---

## 📦 Instalação

### Requisitos
- Python 3.11 ou superior
- pip

### Passos

1. Clone o repositório:
```bash
git clone https://github.com/pdrlucs/Autofatx.git
cd Autofatx
```

2. Crie um ambiente virtual:
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

```bash
python main.py
```

---

## 🔧 Funcionalidades

### 📄 Processador XML
- Validação e correção automática de arquivos PTU/TISS
- Aplicação de regras de negócio configuráveis
- Geração de arquivos corrigidos

### ✅ Motor de Regras
- 100+ regras de validação
- Correção de tp_Participacao por procedimento
- Correção de CNES por CNPJ do prestador
- Regras de equipe obrigatória

### 📊 Dashboard
- KPIs em tempo real
- Economia total / Glosas evitadas
- Taxa de sucesso
- Histórico de execuções

### 📥 Importação de Relatórios
- A500 Enviados
- Distribuição de Faturas
- Faturas Emitidas

---

## 🛠️ Tecnologias

- **Python 3.11+**
- **PyQt6** - Interface gráfica
- **SQLAlchemy** - ORM
- **lxml** - Processamento XML
- **pandas** - Manipulação de dados

---

## 📝 Licença

Propriedade de **Pedro Lucas Lima de Freitas**.  
Todos os direitos reservados.

---

## 👨‍💻 Autor

**Pedro Lucas Lima de Freitas**

---

**Glox** - Eliminando glosas automaticamente 🚀
