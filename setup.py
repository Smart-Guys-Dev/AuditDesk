"""
AuditPlus v2.0 - Sistema de Auditoria e Validação de Contas Médicas
Unimed Campo Grande - Cooperativa de Trabalho Médico
"""

from setuptools import setup, find_packages
import os

# Ler versão do arquivo
VERSION = "2.0.0"

# Ler README para descrição longa
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

# Ler dependências do requirements.txt
def read_requirements():
    req_file = "requirements.txt"
    if os.path.exists(req_file):
        with open(req_file, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return []

setup(
    name="auditplus",
    version=VERSION,
    author="BisonCode Enterprise",
    author_email="ti@unimedcg.coop.br",
    description="Sistema de Auditoria e Validação Automatizada de Contas Médicas",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bisoncode-enterprise/AuditPlus_Desktop",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Healthcare Industry",
        "License :: Other/Proprietary License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial :: Accounting",
    ],
    python_requires=">=3.10",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "flake8>=6.0",
            "mypy>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "auditplus=main:main",
        ],
        "gui_scripts": [
            "auditplus-gui=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.xsd", "*.qss", "*.css"],
    },
    zip_safe=False,
)
