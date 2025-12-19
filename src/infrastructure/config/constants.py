"""
Constantes centralizadas para Audit+ v2.0.
"""

# ========================================
# Valores de Negócio
# ========================================

VALOR_MINIMO_GUIA = 25000.0
"""Valor mínimo para considerar uma guia relevante (em centavos)."""

DURACAO_MAXIMA_INTERNACAO_CURTA_HORAS = 12
"""Duração máxima em horas para considerar internação de curta permanência."""

# ========================================
# Extensões de Arquivo
# ========================================

EXTENSAO_XML = ".051"
"""Extensão padrão para arquivos XML PTU."""

EXTENSAO_ZIP = ".zip"
"""Extensão padrão para arquivos compactados."""

# ========================================
# Namespaces XML
# ========================================

NAMESPACE_PTU = 'http://ptu.unimed.coop.br/schemas/V3_0'
"""Namespace padrão para arquivos PTU XML."""

# ========================================
# Diretórios
# ========================================

DIR_CONFIG = "config"
"""Diretório de arquivos de configuração."""

DIR_SCHEMAS = "schemas"
"""Diretório de schemas XSD."""

DIR_ASSETS = "assets"
"""Diretório de assets (ícones, estilos, etc)."""

# ========================================
# Nomes de Pastas Padrão
# ========================================

PASTA_BACKUP = "Backup"
"""Nome da pasta de backup."""

PASTA_CORRECAO_XML = "Correção XML"
"""Nome da pasta onde XMLs são preparados para correção."""

PASTA_ZIPS_FINAIS = "ZIPs Finais"
"""Nome da pasta onde ZIPs finais são salvos."""

# ========================================
# Configurações de Processamento
# ========================================

ENCODING_PADRAO = 'utf-8'
"""Encoding padrão para leitura/escrita de arquivos."""

ENCODING_CSV = 'utf-8-sig'
"""Encoding para arquivos CSV (com BOM para Excel)."""

DELIMITADOR_CSV = ';'
"""Delimitador padrão para arquivos CSV."""
