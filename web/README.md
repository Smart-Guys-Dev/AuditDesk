# AuditPlus Web 🔒

Versão web do sistema AuditPlus para auditoria de XMLs PTU (Padrão de Troca Unimed).

## Stack Tecnológico

| Camada         | Tecnologia                        |
| -------------- | --------------------------------- |
| Frontend       | Angular 21 (Standalone + Signals) |
| Backend        | .NET 10 (Clean Architecture)      |
| Banco de Dados | SQLite (dev)                      |
| Autenticação   | JWT Bearer                        |

## Arquitetura

```
┌─────────────────┐     ┌──────────────────┐     ┌──────────┐
│   Angular 21    │────▶│   .NET 10 API    │────▶│  SQLite  │
│   localhost:4200│◀────│   localhost:5135 │◀────│auditplus │
└─────────────────┘     └──────────────────┘     └──────────┘
```

---

## 📋 INSTRUÇÃO DE TRABALHO (IT)

### 🚀 1. Iniciar o Sistema

#### Terminal 1 - Backend

```bash
cd web
dotnet run --project AuditPlus.Api
```

> Aguardar mensagem: `Now listening on: http://localhost:5135`

#### Terminal 2 - Frontend

```bash
cd web/auditplus-web
npm start
```

> Aguardar mensagem: `Compiled successfully`

---

### 🔐 2. Acessar o Sistema

1. Abra o navegador em: **http://localhost:4200**
2. Faça login:
   - **Usuário:** admin
   - **Senha:** admin123
3. Clique em **Entrar**

---

### 📤 3. Upload de XMLs

1. No menu lateral, clique em **Validação**
2. Arraste os arquivos XML (ou .051) para a área de upload
3. Os arquivos serão exibidos na lista

---

### ⚙️ 4. Processar Lote

1. Digite o **ID da Execução** (um número qualquer, ex: 1)
2. Clique no botão **🔍 Processar Lote**
3. Aguarde o processamento
4. O resultado mostrará:
   - Total de arquivos
   - Arquivos modificados
   - Total de correções

---

### 👁️ 5. Visualizar Preview

1. Após processar, clique em **📋 Ver Preview**
2. Visualize a tabela com:
   - Regra aplicada
   - Elemento modificado
   - Valor ANTES
   - Valor DEPOIS

---

### ✅ 6. Aplicar Correções

1. Clique no botão **✅ Aplicar Correções**
2. Confirme no modal de confirmação
3. O sistema irá:
   - Criar backup dos originais
   - Aplicar as correções nos XMLs
   - Salvar na pasta `corrigidos/`

---

### 🔐 7. Recalcular Hash PTU

1. Após aplicar correções, clique em **🔐 Recalcular Hash**
2. O sistema irá:
   - Calcular o hash MD5 do bloco `<GuiaCobrancaUtilizacao>`
   - Atualizar a tag `<hash>` no XML
3. Os hashes calculados serão exibidos na tela

---

### 📤 8. Exportar ZIP

#### Opção A - ZIP Simples:

- Clique em **📦 Exportar ZIP**
- Baixa todos os XMLs corrigidos em um único ZIP

#### Opção B - ZIP Formato PTU (Recomendado):

- Clique em **📤 Exportar PTU**
- Estrutura gerada:

```
Validacao_CMB_exec_1.zip
└── Validacao_CMB/
    ├── fatura001.zip → fatura001.051
    ├── fatura002.zip → fatura002.051
    └── ...
```

---

## 📊 Fluxo Completo Resumido

```
Login → Upload → Processar → Preview → Aplicar → Hash → Exportar PTU
```

---

## Estrutura do Projeto

```
web/
├── AuditPlus.slnx              # Solution .NET
├── AuditPlus.Domain/           # Entities, Enums, Interfaces
├── AuditPlus.Application/      # Services, DTOs
├── AuditPlus.Infrastructure/   # EF Core, Repositories
├── AuditPlus.Api/              # Controllers, JWT
├── AuditPlus.Tests/            # Testes xUnit
└── auditplus-web/              # Angular Frontend
    └── src/app/
        ├── core/               # Services, Guards
        └── features/           # Login, Dashboard, Validation, etc
```

## API Endpoints

| Método | Endpoint                        | Descrição                  |
| ------ | ------------------------------- | -------------------------- |
| POST   | /api/auth/login                 | Autenticação JWT           |
| GET    | /api/dashboard/stats            | Estatísticas do dashboard  |
| GET    | /api/regras                     | Listar regras de validação |
| POST   | /api/validation/processar/{id}  | Processar lote de XMLs     |
| GET    | /api/validation/preview/{id}    | Preview das correções      |
| POST   | /api/validation/aplicar/{id}    | Aplicar correções          |
| POST   | /api/validation/hash/{id}       | Recalcular hash PTU        |
| GET    | /api/validation/export/{id}     | Exportar ZIP simples       |
| GET    | /api/validation/export-ptu/{id} | Exportar ZIP formato PTU   |

## Licença

Projeto interno - UNIMEDCG

---

_Última atualização: 03/02/2026_
