# AuditPlus Web 🔒

Versão web do sistema AuditPlus para auditoria de XMLs TISS.

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

## 🚀 Quick Start

### 1. Backend

```bash
cd web
dotnet run --project AuditPlus.Api
```

### 2. Frontend (outro terminal)

```bash
cd web/auditplus-web
npm install
npm start
```

### 3. Acesso

- **URL:** http://localhost:4200
- **Login:** admin / admin123

## Estrutura do Projeto

```
web/
├── AuditPlus.slnx              # Solution .NET
├── AuditPlus.Domain/           # Entities, Enums, Interfaces
├── AuditPlus.Application/      # Services, DTOs
├── AuditPlus.Infrastructure/   # EF Core, Repositories
├── AuditPlus.Api/              # Controllers, JWT
└── auditplus-web/              # Angular Frontend
    └── src/app/
        ├── core/               # Services, Guards
        └── features/           # Login, Dashboard, Regras, Relatórios
```

## Features

- ✅ Login com JWT
- ✅ Dashboard com métricas
- ✅ CRUD de Regras de Auditoria
- ✅ Relatórios (Glosas, Efetividade, Mensal)
- ✅ Seed de dados para demonstração

## API Endpoints

| Método | Endpoint                        | Descrição        |
| ------ | ------------------------------- | ---------------- |
| POST   | /api/auth/login                 | Autenticação     |
| GET    | /api/dashboard/stats            | Estatísticas     |
| GET    | /api/regras                     | Listar regras    |
| GET    | /api/relatorios/glosas-evitadas | Relatório glosas |

## Licença

Projeto interno - UNIMEDCG
