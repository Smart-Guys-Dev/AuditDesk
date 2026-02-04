import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';

interface DashboardStats {
  totalRegras: number;
  regrasAtivas: number;
  totalExecucoes: number;
  taxaSucesso: number;
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <div class="dashboard-container">
      <!-- Header -->
      <header class="dashboard-header">
        <div class="logo">
          <h1>🔒 AuditPlus</h1>
        </div>
        <div class="user-menu">
          <span class="user-name">{{ currentUser()?.fullName }}</span>
          <span class="user-role">{{ currentUser()?.role }}</span>
          <button class="btn-logout" (click)="logout()">Sair</button>
        </div>
      </header>
      
      <!-- Main Content -->
      <main class="dashboard-main">
        <h2>Dashboard</h2>
        
        <!-- Stats Cards -->
        <div class="stats-grid">
          <div class="stat-card primary">
            <div class="stat-icon">📋</div>
            <div class="stat-info">
              <span class="stat-value">{{ stats().totalRegras }}</span>
              <span class="stat-label">Total de Regras</span>
            </div>
          </div>
          
          <div class="stat-card success">
            <div class="stat-icon">✅</div>
            <div class="stat-info">
              <span class="stat-value">{{ stats().regrasAtivas }}</span>
              <span class="stat-label">Regras Ativas</span>
            </div>
          </div>
          
          <div class="stat-card info">
            <div class="stat-icon">🔄</div>
            <div class="stat-info">
              <span class="stat-value">{{ stats().totalExecucoes }}</span>
              <span class="stat-label">Execuções</span>
            </div>
          </div>
          
          <div class="stat-card warning">
            <div class="stat-icon">📊</div>
            <div class="stat-info">
              <span class="stat-value">{{ stats().taxaSucesso }}%</span>
              <span class="stat-label">Taxa de Sucesso</span>
            </div>
          </div>
        </div>
        
        <!-- Quick Actions -->
        <div class="quick-actions">
          <h3>Ações Rápidas</h3>
          <div class="actions-grid">
            <a routerLink="/regras" class="action-card">
              <span class="action-icon">📝</span>
              <span class="action-label">Gerenciar Regras</span>
            </a>
            <a routerLink="/upload" class="action-card">
              <span class="action-icon">▶️</span>
              <span class="action-label">Nova Execução</span>
            </a>
            <a routerLink="/relatorios" class="action-card">
              <span class="action-icon">📈</span>
              <span class="action-label">Relatórios</span>
            </a>
          </div>
        </div>
      </main>
    </div>
  `,
  styles: [`
    .dashboard-container {
      min-height: 100vh;
      background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
      color: #fff;
    }
    
    .dashboard-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 20px 40px;
      background: rgba(0, 0, 0, 0.2);
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .logo h1 {
      margin: 0;
      font-size: 1.5rem;
    }
    
    .user-menu {
      display: flex;
      align-items: center;
      gap: 15px;
    }
    
    .user-name {
      font-weight: 600;
    }
    
    .user-role {
      background: rgba(0, 217, 255, 0.2);
      color: #00d9ff;
      padding: 4px 10px;
      border-radius: 20px;
      font-size: 0.8rem;
    }
    
    .btn-logout {
      padding: 8px 16px;
      border-radius: 8px;
      border: 1px solid rgba(255, 255, 255, 0.3);
      background: transparent;
      color: #fff;
      cursor: pointer;
      transition: all 0.3s ease;
    }
    
    .btn-logout:hover {
      background: rgba(255, 255, 255, 0.1);
    }
    
    .dashboard-main {
      padding: 40px;
      max-width: 1200px;
      margin: 0 auto;
    }
    
    .dashboard-main h2 {
      margin: 0 0 30px 0;
      font-size: 1.8rem;
    }
    
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 20px;
      margin-bottom: 40px;
    }
    
    .stat-card {
      background: rgba(255, 255, 255, 0.05);
      backdrop-filter: blur(10px);
      border-radius: 16px;
      padding: 25px;
      display: flex;
      align-items: center;
      gap: 20px;
      border: 1px solid rgba(255, 255, 255, 0.1);
      transition: transform 0.3s ease;
    }
    
    .stat-card:hover {
      transform: translateY(-5px);
    }
    
    .stat-icon {
      font-size: 2.5rem;
    }
    
    .stat-info {
      display: flex;
      flex-direction: column;
    }
    
    .stat-value {
      font-size: 2rem;
      font-weight: 700;
    }
    
    .stat-label {
      color: rgba(255, 255, 255, 0.6);
      font-size: 0.9rem;
    }
    
    .stat-card.primary { border-left: 4px solid #00d9ff; }
    .stat-card.success { border-left: 4px solid #00e676; }
    .stat-card.info { border-left: 4px solid #ffc107; }
    .stat-card.warning { border-left: 4px solid #ff5722; }
    
    .quick-actions h3 {
      margin: 0 0 20px 0;
      color: rgba(255, 255, 255, 0.8);
    }
    
    .actions-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 20px;
    }
    
    .action-card {
      background: rgba(255, 255, 255, 0.05);
      border-radius: 12px;
      padding: 30px;
      text-align: center;
      text-decoration: none;
      color: #fff;
      border: 1px solid rgba(255, 255, 255, 0.1);
      transition: all 0.3s ease;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 15px;
    }
    
    .action-card:hover {
      background: rgba(0, 217, 255, 0.1);
      border-color: rgba(0, 217, 255, 0.3);
      transform: translateY(-3px);
    }
    
    .action-icon {
      font-size: 2rem;
    }
    
    .action-label {
      font-weight: 500;
    }
  `]
})
export class DashboardComponent implements OnInit {
  private authService = inject(AuthService);
  
  currentUser = this.authService.currentUser;
  stats = signal<DashboardStats>({
    totalRegras: 0,
    regrasAtivas: 0,
    totalExecucoes: 0,
    taxaSucesso: 0
  });
  
  ngOnInit(): void {
    // TODO: Carregar stats da API
    this.stats.set({
      totalRegras: 25,
      regrasAtivas: 18,
      totalExecucoes: 142,
      taxaSucesso: 94.5
    });
  }
  
  logout(): void {
    this.authService.logout();
  }
}
