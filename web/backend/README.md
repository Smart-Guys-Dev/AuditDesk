# AuditPlus Web - Backend

Backend FastAPI para o sistema AuditPlus Web.

## Instalação

```bash
cd web/backend
pip install -r requirements.txt
```

## Executar

```bash
uvicorn app.main:app --reload --port 8000
```

## Endpoints

- `GET /health` - Health check
- `POST /api/v1/process-xml` - Processar arquivo XML
- `GET /api/v1/rules` - Listar regras disponíveis
