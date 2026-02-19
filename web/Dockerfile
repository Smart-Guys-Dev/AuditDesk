# ==================================================
# AuditPlus API — Multi-stage Dockerfile
# Stage 1: Build (.NET 10 SDK)
# Stage 2: Runtime (ASP.NET 10 runtime)
# ==================================================

FROM mcr.microsoft.com/dotnet/sdk:10.0-preview AS build
WORKDIR /src

# Copy project files for restore (layer caching)
COPY AuditPlus.Domain/AuditPlus.Domain.csproj AuditPlus.Domain/
COPY AuditPlus.Application/AuditPlus.Application.csproj AuditPlus.Application/
COPY AuditPlus.Infrastructure/AuditPlus.Infrastructure.csproj AuditPlus.Infrastructure/
COPY AuditPlus.Api/AuditPlus.Api.csproj AuditPlus.Api/
RUN dotnet restore AuditPlus.Api/AuditPlus.Api.csproj

# Copy all source and build
COPY . .
RUN dotnet publish AuditPlus.Api/AuditPlus.Api.csproj \
    -c Release -o /app/publish --no-restore

# ==================================================
# Stage 2: Runtime
# ==================================================
FROM mcr.microsoft.com/dotnet/aspnet:10.0-preview AS runtime
WORKDIR /app

# Security: run as non-root
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Copy published app
COPY --from=build /app/publish .

# Create data directory for SQLite
RUN mkdir -p /app/data && chown -R appuser:appgroup /app/data

# Switch to non-root user
USER appuser

# Expose ports
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8080/api/auth || exit 1

ENTRYPOINT ["dotnet", "AuditPlus.Api.dll"]
