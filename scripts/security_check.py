# security_check.py
"""
Security Check Script
Script local para verificar vulnerabilidades em dependências.

USO: python security_check.py
"""

import subprocess
import sys
import json

def run_command(cmd, description):
    """Executa comando e retorna resultado"""
    print(f"\n{'='*60}")
    print(f"🔍 {description}")
    print(f"{'='*60}\n")
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        
        if result.stderr:
            print("Avisos/Erros:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Erro ao executar: {e}")
        return False


def main():
    """Executa verificações de segurança"""
    
    print("="*60)
    print("🔐 VERIFICAÇÃO DE SEGURANÇA - AuditPlus v2.0")
    print("="*60)
    
    results = {}
    
    # 1. Safety Check
    results['safety'] = run_command(
        "safety check",
        "Safety - Vulnerabilidades Conhecidas em Dependências"
    )
    
    # 2. pip-audit
    results['pip_audit'] = run_command(
        "pip-audit --desc",
        "pip-audit - Auditoria Oficial PyPI"
    )
    
    # 3. Bandit SAST
    results['bandit'] = run_command(
        "bandit -r src/ -f screen",
        "Bandit - Análise Estática de Código"
    )
    
    # Resumo
    print("\n" + "="*60)
    print("📊 RESUMO DAS VERIFICAÇÕES")
    print("="*60)
    
    for tool, success in results.items():
        status = "✅ PASSOU" if success else "⚠️  AVISOS/FALHAS"
        print(f"  {tool.upper()}: {status}")
    
    print("\n" + "="*60)
    print("💡 RECOMENDAÇÕES:")
    print("="*60)
    print("  1. Revisar avisos acima")
    print("  2. Atualizar dependências vulneráveis")
    print("  3. Corrigir issues do Bandit se aplicável")
    print("  4. Executar regularmente (semanalmente)")
    print()
    
    # Retornar código de saída
    if all(results.values()):
        print("✅ Todas as verificações passaram!")
        return 0
    else:
        print("⚠️  Algumas verificações encontraram issues.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
