import { Component, inject, OnInit, signal } from '@angular/core';
import { RouterModule } from '@angular/router';
import { DashboardService, DashboardStats } from '../../core/services/dashboard.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [RouterModule],
  template: `
    <div class="dashboard-page">
      <div class="page-title">
        <h1>Dashboard</h1>
        <p class="subtitle">Visão geral do sistema de auditoria</p>
      </div>

      <!-- Stats Cards -->
      <div class="stats-grid">
        <div class="stat-card primary">
          <div class="stat-icon-wrap primary-bg">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <rect x="9" y="3" width="6" height="4" rx="1" stroke="currentColor" stroke-width="2"/>
              <path d="M9 12h6M9 16h4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ stats().totalRegras }}</span>
            <span class="stat-label">Total de Regras</span>
          </div>
        </div>

        <div class="stat-card success">
          <div class="stat-icon-wrap success-bg">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M9 12l2 2 4-4" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
              <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2"/>
            </svg>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ stats().regrasAtivas }}</span>
            <span class="stat-label">Regras Ativas</span>
          </div>
        </div>

        <div class="stat-card info">
          <div class="stat-icon-wrap info-bg">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M12 8v4l3 3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2"/>
            </svg>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ stats().totalExecucoes }}</span>
            <span class="stat-label">Execuções</span>
          </div>
        </div>

        <div class="stat-card warning">
          <div class="stat-icon-wrap warning-bg">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M18 20V10M12 20V4M6 20v-6" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ stats().taxaSucesso }}%</span>
            <span class="stat-label">Taxa de Sucesso</span>
          </div>
        </div>

        <div class="stat-card files">
          <div class="stat-icon-wrap files-bg">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <polyline points="14,2 14,8 20,8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ stats().totalArquivosProcessados }}</span>
            <span class="stat-label">Arquivos Processados</span>
          </div>
        </div>

        <div class="stat-card faturas">
          <div class="stat-icon-wrap faturas-bg">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <rect x="2" y="5" width="20" height="14" rx="2" stroke="currentColor" stroke-width="2"/>
              <line x1="2" y1="10" x2="22" y2="10" stroke="currentColor" stroke-width="2"/>
            </svg>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ stats().totalFaturas }}</span>
            <span class="stat-label">Faturas</span>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="section">
        <h3 class="section-title">Ações Rápidas</h3>
        <div class="actions-grid">
          <a routerLink="/regras" class="action-card">
            <div class="action-icon-wrap">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
                <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                <rect x="9" y="3" width="6" height="4" rx="1" stroke="currentColor" stroke-width="2"/>
              </svg>
            </div>
            <span class="action-label">Gerenciar Regras</span>
            <span class="action-desc">Criar, editar e ativar regras</span>
          </a>
          <a routerLink="/upload" class="action-card">
            <div class="action-icon-wrap">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
                <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <polyline points="17,8 12,3 7,8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <line x1="12" y1="3" x2="12" y2="15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </div>
            <span class="action-label">Upload de Arquivos</span>
            <span class="action-desc">Enviar XMLs para processamento</span>
          </a>
          <a routerLink="/validation" class="action-card">
            <div class="action-icon-wrap">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
                <path d="M9 12l2 2 4-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" stroke="currentColor" stroke-width="2"/>
              </svg>
            </div>
            <span class="action-label">Validação</span>
            <span class="action-desc">Processar e aplicar correções</span>
          </a>
          <a routerLink="/relatorios" class="action-card">
            <div class="action-icon-wrap">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
                <path d="M18 20V10M12 20V4M6 20v-6" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <span class="action-label">Relatórios</span>
            <span class="action-desc">Glosas evitadas e métricas</span>
          </a>
        </div>
      </div>

      @if (isLoading()) {
        <div class="loading">
          <div class="spinner"></div>
          <p>Carregando dados...</p>
        </div>
      }
    </div>
  `,
  styles: [`
    .dashboard-page {
      padding: var(--ap-page-padding);
      max-width: 1200px;
      margin: 0 auto;
    }

    .page-title {
      margin-bottom: 32px;
    }

    .page-title h1 {
      font-size: 1.8rem;
      font-weight: 700;
      margin: 0 0 6px;
    }

    .subtitle {
      color: var(--ap-text-muted);
      font-size: 0.95rem;
    }

    /* Stats Grid */
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(215px, 1fr));
      gap: 18px;
      margin-bottom: 40px;
    }

    .stat-card {
      background: var(--ap-bg-card);
      backdrop-filter: blur(10px);
      border-radius: 16px;
      padding: 22px;
      display: flex;
      align-items: center;
      gap: 18px;
      border: 1px solid var(--ap-border);
      transition: transform var(--ap-transition-normal), box-shadow var(--ap-transition-normal);
    }

    .stat-card:hover {
      transform: translateY(-4px);
      box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
    }

    .stat-icon-wrap {
      width: 48px;
      height: 48px;
      min-width: 48px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .primary-bg  { background: rgba(0, 217, 255, 0.15); color: var(--ap-cyan); }
    .success-bg  { background: rgba(0, 230, 118, 0.15); color: var(--ap-green); }
    .info-bg     { background: rgba(255, 193, 7, 0.15); color: #ffc107; }
    .warning-bg  { background: rgba(255, 87, 34, 0.15); color: #ff5722; }
    .files-bg    { background: rgba(156, 39, 176, 0.15); color: #ce93d8; }
    .faturas-bg  { background: rgba(233, 30, 99, 0.15); color: #f48fb1; }

    .stat-card.primary  { border-left: 3px solid var(--ap-cyan); }
    .stat-card.success  { border-left: 3px solid var(--ap-green); }
    .stat-card.info     { border-left: 3px solid #ffc107; }
    .stat-card.warning  { border-left: 3px solid #ff5722; }
    .stat-card.files    { border-left: 3px solid #ce93d8; }
    .stat-card.faturas  { border-left: 3px solid #f48fb1; }

    .stat-info {
      display: flex;
      flex-direction: column;
    }

    .stat-value {
      font-size: 1.8rem;
      font-weight: 700;
      line-height: 1.1;
    }

    .stat-label {
      color: var(--ap-text-muted);
      font-size: 0.85rem;
      margin-top: 2px;
    }

    /* Section */
    .section {
      margin-bottom: 40px;
    }

    .section-title {
      margin: 0 0 18px;
      color: var(--ap-text-secondary);
      font-size: 1.1rem;
    }

    /* Actions Grid */
    .actions-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
    }

    .action-card {
      background: var(--ap-bg-card);
      border-radius: var(--ap-radius-lg);
      padding: 24px;
      text-decoration: none;
      color: var(--ap-text-primary);
      border: 1px solid var(--ap-border);
      transition: all var(--ap-transition-normal);
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .action-card:hover {
      background: rgba(0, 217, 255, 0.08);
      border-color: rgba(0, 217, 255, 0.25);
      transform: translateY(-3px);
    }

    .action-icon-wrap {
      width: 42px;
      height: 42px;
      border-radius: 10px;
      background: rgba(0, 217, 255, 0.12);
      color: var(--ap-cyan);
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .action-label {
      font-weight: 600;
      font-size: 0.95rem;
    }

    .action-desc {
      color: var(--ap-text-muted);
      font-size: 0.8rem;
      line-height: 1.4;
    }
  `]
})
export class DashboardComponent implements OnInit {
  private dashboardService = inject(DashboardService);

  isLoading = signal(false);
  stats = signal<DashboardStats>({
    totalRegras: 0,
    regrasAtivas: 0,
    totalExecucoes: 0,
    totalFaturas: 0,
    execucoesSucesso: 0,
    execucoesErro: 0,
    totalArquivosProcessados: 0,
    taxaSucesso: 0
  });

  ngOnInit(): void {
    this.isLoading.set(true);
    this.dashboardService.getStats().subscribe(data => {
      this.stats.set(data);
      this.isLoading.set(false);
    });
  }
}
