# -*- coding: utf-8 -*-
"""
AuditPlus Web - Backend FastAPI
Aplicação principal
"""
import os
import sys
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Adicionar o diretório raiz ao path para importar módulos compartilhados
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.business.rules.rule_engine import RuleEngine
from src.infrastructure.parsers.xml_reader import XMLReader

# Inicialização do FastAPI
app = FastAPI(
    title="AuditPlus Web API",
    description="API para processamento e correção de faturas XML",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar origens permitidas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar motor de regras (singleton)
rule_engine: Optional[RuleEngine] = None


def get_rule_engine() -> RuleEngine:
    """Retorna instância do motor de regras."""
    global rule_engine
    if rule_engine is None:
        rule_engine = RuleEngine()
        rule_engine.load_all_rules(use_database=False)
    return rule_engine


# ============== MODELOS ==============

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str


class RuleInfo(BaseModel):
    id: str
    descricao: str
    ativo: bool


class ProcessingResult(BaseModel):
    success: bool
    message: str
    arquivo: str
    regras_aplicadas: int
    modificado: bool
    xml_corrigido: Optional[str] = None


# ============== ENDPOINTS ==============

@app.get("/health", response_model=HealthResponse, tags=["Sistema"])
async def health_check():
    """Verificação de saúde da API."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )


@app.get("/api/v1/rules", response_model=List[RuleInfo], tags=["Regras"])
async def list_rules():
    """Lista todas as regras disponíveis."""
    engine = get_rule_engine()
    
    rules = []
    for rule in engine.loaded_rules:
        rules.append(RuleInfo(
            id=rule.get("id", "SEM_ID"),
            descricao=rule.get("descricao", ""),
            ativo=rule.get("ativo", True)
        ))
    
    return rules


@app.get("/api/v1/rules/count", tags=["Regras"])
async def count_rules():
    """Retorna contagem de regras carregadas."""
    engine = get_rule_engine()
    return {
        "total": len(engine.loaded_rules),
        "ativas": len([r for r in engine.loaded_rules if r.get("ativo", True)])
    }


@app.post("/api/v1/process-xml", response_model=ProcessingResult, tags=["Processamento"])
async def process_xml(file: UploadFile = File(...)):
    """
    Processa um arquivo XML aplicando as regras de correção.
    
    - **file**: Arquivo XML para processar
    """
    if not file.filename.endswith('.xml'):
        raise HTTPException(status_code=400, detail="Arquivo deve ter extensão .xml")
    
    try:
        # Ler conteúdo do arquivo
        content = await file.read()
        
        # Parsear XML
        import lxml.etree as etree
        tree = etree.fromstring(content).getroottree()
        
        # Aplicar regras
        engine = get_rule_engine()
        modificado = engine.apply_rules_to_xml(tree, -1, file.filename)
        
        # Converter XML de volta para string
        xml_corrigido = etree.tostring(
            tree.getroot(),
            encoding='unicode',
            pretty_print=True
        )
        
        return ProcessingResult(
            success=True,
            message="XML processado com sucesso",
            arquivo=file.filename,
            regras_aplicadas=len(engine.loaded_rules),
            modificado=modificado,
            xml_corrigido=xml_corrigido if modificado else None
        )
        
    except etree.XMLSyntaxError as e:
        raise HTTPException(status_code=400, detail=f"Erro de sintaxe XML: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar: {str(e)}")


@app.get("/", tags=["Sistema"])
async def root():
    """Página inicial da API."""
    return {
        "app": "AuditPlus Web API",
        "status": "online",
        "docs": "/docs",
        "health": "/health"
    }


# ============== INICIALIZAÇÃO ==============

@app.on_event("startup")
async def startup_event():
    """Executado ao iniciar a aplicação."""
    print("=" * 50)
    print("AuditPlus Web API - Iniciando...")
    print("=" * 50)
    
    # Pré-carregar motor de regras
    engine = get_rule_engine()
    print(f"✅ Motor de regras carregado: {len(engine.loaded_rules)} regras")
    print(f"📍 Documentação: http://localhost:8000/docs")
    print("=" * 50)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
