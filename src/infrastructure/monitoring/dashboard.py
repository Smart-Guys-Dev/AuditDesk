"""
Dashboard de monitoramento para Glox.

Coleta e exibe métricas operacionais em tempo real.
"""
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Coleta métricas de processamento"""
    
    def __init__(self, metrics_file: str = "metrics.jsonl"):
        """
        Inicializa coletor de métricas.
        
        Args:
            metrics_file: Arquivo para armazenar métricas
        """
        self.metrics_file = Path(metrics_file)
        self.current_session = {
            'start_time': time.time(),
            'files_processed': 0,
            'files_success': 0,
            'files_error': 0,
            'rules_applied': 0,
            'errors': []
        }
    
    def record_file_processed(self, success: bool, rules_applied: int = 0):
        """Registra processamento de arquivo"""
        self.current_session['files_processed'] += 1
        
        if success:
            self.current_session['files_success'] += 1
            self.current_session['rules_applied'] += rules_applied
        else:
            self.current_session['files_error'] += 1
    
    def record_error(self, error_type: str, message: str):
        """Registra erro"""
        self.current_session['errors'].append({
            'timestamp': datetime.now().isoformat(),
            'type': error_type,
            'message': message
        })
    
    def get_current_metrics(self) -> Dict:
        """Retorna métricas da sessão atual"""
        duration = time.time() - self.current_session['start_time']
        
        return {
            **self.current_session,
            'duration_seconds': duration,
            'throughput': self.current_session['files_success'] / duration if duration > 0 else 0,
            'error_rate': self.current_session['files_error'] / self.current_session['files_processed'] 
                if self.current_session['files_processed'] > 0 else 0
        }
    
    def save_session(self):
        """Salva métricas da sessão"""
        metrics = self.get_current_metrics()
        metrics['timestamp'] = datetime.now().isoformat()
        
        # Append to JSONL
        with open(self.metrics_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(metrics, ensure_ascii=False) + '\n')
        
        logger.info(f"Métricas salvas: {self.metrics_file}")


def generate_dashboard(metrics_file: str = "metrics.jsonl", output_html: str = "dashboard.html"):
    """
    Gera dashboard HTML com métricas.
    
    Args:
        metrics_file: Arquivo com métricas
        output_html: Arquivo HTML de saída
    """
    # Carregar métricas
    metrics = []
    if Path(metrics_file).exists():
        with open(metrics_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    metrics.append(json.loads(line))
    
    # Calcular agregados
    if metrics:
        last_session = metrics[-1]
        total_processed = sum(m['files_processed'] for m in metrics)
        total_success = sum(m['files_success'] for m in metrics)
        avg_throughput = sum(m['throughput'] for m in metrics) / len(metrics)
    else:
        last_session = {}
        total_processed = 0
        total_success = 0
        avg_throughput = 0
    
    # HTML Dashboard
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Glox - Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f7fa; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ color: #2d3748; margin-bottom: 30px; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom:30px; }}
        .metric-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .metric-value {{ font-size: 2.5rem; font-weight: bold; margin: 10px 0; }}
        .metric-label {{ color: #718096; font-size: 0.9rem; }}
        .success {{ color: #48bb78; }}
        .error {{ color: #f56565; }}
        .info {{ color: #4299e1; }}
        .warning {{ color: #ed8936; }}
        .table {{ background: white; border-radius: 8px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #e2e8f0; }}
        th {{ font-weight: 600; color: #4a5568; }}
        .footer {{ margin-top: 30px; text-align: center; color: #a0aec0; font-size: 0.9rem; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Glox - Dashboard de Monitoramento</h1>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Total Processado</div>
                <div class="metric-value info">{total_processed:,}</div>
                <div class="metric-label">arquivos</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">Taxa de Sucesso</div>
                <div class="metric-value success">{(total_success/total_processed*100) if total_processed > 0 else 0:.1f}%</div>
                <div class="metric-label">{total_success:,} sucessos</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">Throughput Médio</div>
                <div class="metric-value info">{avg_throughput:.1f}</div>
                <div class="metric-label">arquivos/segundo</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">Última Sessão</div>
                <div class="metric-value">
                    <span class="success">{last_session.get('files_success', 0)}</span> / 
                    <span class="error">{last_session.get('files_error', 0)}</span>
                </div>
                <div class="metric-label">sucesso / erros</div>
            </div>
        </div>
        
        <div class="table">
            <h2 style="margin-bottom: 20px;">📈 Histórico de Sessões</h2>
            <table>
                <thead>
                    <tr>
                        <th>Timestamp</th>
                        <th>Processados</th>
                        <th>Sucesso</th>
                        <th>Erros</th>
                        <th>Taxa Erro</th>
                        <th>Throughput</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    # Adicionar últimas 10 sessões
    for session in metrics[-10:][::-1]:
        html += f"""
                    <tr>
                        <td>{session.get('timestamp', 'N/A')[:19]}</td>
                        <td>{session.get('files_processed', 0)}</td>
                        <td class="success">{session.get('files_success', 0)}</td>
                        <td class="error">{session.get('files_error', 0)}</td>
                        <td>{session.get('error_rate', 0)*100:.1f}%</td>
                        <td>{session.get('throughput', 0):.2f} arq/s</td>
                    </tr>
"""
    
    html += """
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>Última atualização: {now}</p>
            <p>Glox - Desenvolvido por Pedro Lucas</p>
        </div>
    </div>
</body>
</html>
""".format(now=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    
    # Salvar HTML
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html)
    
    logger.info(f"Dashboard gerado: {output_html}")
    return output_html


class AlertSystem:
    """Sistema de alertas básico"""
    
    def __init__(self, alert_file: str = "alerts.log"):
        self.alert_file = Path(alert_file)
        self.thresholds = {
            'error_rate': 0.05,  # 5%
            'throughput_min': 1.0  # 1 arquivo/segundo
        }
    
    def check_alerts(self, metrics: Dict) -> List[str]:
        """
        Verifica se métricas disparam alertas.
        
        Returns:
            Lista de alertas
        """
        alerts = []
        
        # Taxa de erro alta
        if metrics.get('error_rate', 0) > self.thresholds['error_rate']:
            alerts.append(
                f"⚠️ ALERTA: Taxa de erro alta: {metrics['error_rate']*100:.1f}% "
                f"(limite: {self.thresholds['error_rate']*100:.1f}%)"
            )
        
        # Throughput baixo
        if metrics.get('throughput', 0) < self.thresholds['throughput_min']:
            alerts.append(
                f"⚠️ ALERTA: Throughput baixo: {metrics['throughput']:.2f} arq/s "
                f"(mínimo: {self.thresholds['throughput_min']:.2f})"
            )
        
        # Registrar alertas
        if alerts:
            self._log_alerts(alerts)
        
        return alerts
    
    def _log_alerts(self, alerts: List[str]):
        """Registra alertas em arquivo"""
        timestamp = datetime.now().isoformat()
        
        with open(self.alert_file, 'a', encoding='utf-8') as f:
            for alert in alerts:
                f.write(f"{timestamp} | {alert}\n")
