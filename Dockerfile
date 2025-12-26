# ==============================================
# AuditPlus v2.0 - Dockerfile
# ==============================================
# Imagem Docker para deploy do AuditPlus
# Nota: Para aplicações Qt GUI, usar em modo headless ou com X11 forwarding

FROM python:3.11-slim

LABEL maintainer="BisonCode Enterprise <ti@unimedcg.coop.br>"
LABEL description="AuditPlus v2.0 - Sistema de Auditoria de Contas Médicas"
LABEL version="2.0.0"

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Qt dependencies
    libgl1-mesa-glx \
    libglib2.0-0 \
    libxcb1 \
    libxkbcommon0 \
    libdbus-1-3 \
    # XML processing
    libxml2 \
    libxslt1.1 \
    # Fonts
    fonts-dejavu-core \
    # Cleanup
    && rm -rf /var/lib/apt/lists/*

# Criar diretório da aplicação
WORKDIR /app

# Copiar requirements primeiro (para cache de layers)
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código fonte
COPY . .

# Criar diretórios necessários
RUN mkdir -p logs backups data

# Usuário não-root para segurança
RUN useradd -m -s /bin/bash auditplus && \
    chown -R auditplus:auditplus /app
USER auditplus

# Volume para persistência de dados
VOLUME ["/app/data", "/app/logs", "/app/backups"]

# Porta (se houver API futura)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Comando padrão (modo CLI para processamento batch)
# Para GUI, usar: docker run -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix
CMD ["python", "main.py", "--help"]
