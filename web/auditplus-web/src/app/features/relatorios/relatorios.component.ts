import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { RelatoriosService } from '../../core/services/relatorios.service';
import { AuthService } from '../../core/services/auth.service';
import { RelatorioGlosasEvitadas, RegraEfetividade, ResumoMensal } from '../../core/models/relatorio.model';

@Component({
  selector: 'app-relatorios',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  template: `
    <div class="page-container">
      <!-- Header -->
      <header class="page-header">
        <div class="header-left">
          <a routerLink="/dashboard" class="back-btn">← Dashboard</a>
          <h1>📊 Relatórios</h1>
        </div>
        <div class="header-right">
          <span class="user-info">{{ currentUser()?.fullName }}</span>
          <button class="btn-logout" (click)="logout()">Sair</button>
        </div>
      </header>
      
      <!-- Tabs -->
      <div class="tabs">
        <button 
          class="tab" 
          [class.active]="activeTab === 'glosas'"
          (click)="activeTab = 'glosas'; loadGlosas()"
        >
          💰 Glosas Evitadas
        </button>
        <button 
          class="tab" 
          [class.active]="activeTab === 'efetividade'"
          (click)="activeTab = 'efetividade'; loadEfetividade()"
        >
          📈 Efetividade das Regras
        </button>
        <button 
          class="tab" 
          [class.active]="activeTab === 'mensal'"
          (click)="activeTab = 'mensal'; loadResumo()"
        >
          📅 Resumo Mensal
        </button>
      </div>
      
      <!-- Content -->
      <main class="content">
        @if (isLoading()) {
          <div class="loading">Carregando relatório...</div>
        } @else {
          <!-- Glosas Evitadas -->
          @if (activeTab === 'glosas' && glosas()) {
            <div class="report-glosas">
              <div class="filters-row">
                <input type="date" [(ngModel)]="dataInicio" (change)="loadGlosas()">
                <span>até</span>
                <input type="date" [(ngModel)]="dataFim" (change)="loadGlosas()">
              </div>
              
              <div class="stats-grid">
                <div class="stat-card highlight">
                  <span class="stat-value">R$ {{ glosas()!.valorTotalEvitado | number:'1.2-2' }}</span>
                  <span class="stat-label">Valor Total Evitado</span>
                </div>
                <div class="stat-card">
                  <span class="stat-value">{{ glosas()!.totalExecucoes }}</span>
                  <span class="stat-label">Execuções</span>
                </div>
                <div class="stat-card">
                  <span class="stat-value">{{ glosas()!.totalArquivosProcessados }}</span>
                  <span class="stat-label">Arquivos Processados</span>
                </div>
                <div class="stat-card">
                  <span class="stat-value">{{ glosas()!.totalCorrecoes }}</span>
                  <span class="stat-label">Correções Realizadas</span>
                </div>
              </div>
              
              <div class="media-card">
                <span class="label">Média por Execução:</span>
                <span class="value">R$ {{ glosas()!.mediaPorExecucao | number:'1.2-2' }}</span>
              </div>
            </div>
          }
          
          <!-- Efetividade -->
          @if (activeTab === 'efetividade') {
            <div class="report-efetividade">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>Código</th>
                    <th>Nome</th>
                    <th>Categoria</th>
                    <th>Aplicações</th>
                    <th>Glosas Evitadas</th>
                    <th>Efetividade</th>
                  </tr>
                </thead>
                <tbody>
                  @for (regra of efetividade(); track regra.codigo) {
                    <tr>
                      <td class="code">{{ regra.codigo }}</td>
                      <td>{{ regra.nome }}</td>
                      <td>
                        <span class="badge" [class]="regra.categoria.toLowerCase()">
                          {{ regra.categoria }}
                        </span>
                      </td>
                      <td class="number">{{ regra.totalAplicacoes }}</td>
                      <td class="number">{{ regra.totalGlosasEvitadas }}</td>
                      <td>
                        <div class="progress-bar">
                          <div class="progress" [style.width.%]="regra.taxaEfetividade"></div>
                          <span class="percent">{{ regra.taxaEfetividade }}%</span>
                        </div>
                      </td>
                    </tr>
                  }
                </tbody>
              </table>
            </div>
          }
          
          <!-- Resumo Mensal -->
          @if (activeTab === 'mensal') {
            <div class="report-mensal">
              <div class="filters-row">
                <select [(ngModel)]="anoSelecionado" (change)="loadResumo()">
                  @for (ano of anos; track ano) {
                    <option [value]="ano">{{ ano }}</option>
                  }
                </select>
              </div>
              
              <table class="data-table">
                <thead>
                  <tr>
                    <th>Mês</th>
                    <th>Execuções</th>
                    <th>Arquivos</th>
                    <th>Correções</th>
                    <th>Valor Economizado</th>
                    <th>Taxa Sucesso</th>
                  </tr>
                </thead>
                <tbody>
                  @for (mes of resumoMensal(); track mes.mes) {
                    <tr>
                      <td>{{ mes.mesNome }}</td>
                      <td class="number">{{ mes.totalExecucoes }}</td>
                      <td class="number">{{ mes.totalArquivos }}</td>
                      <td class="number">{{ mes.totalCorrecoes }}</td>
                      <td class="money">R$ {{ mes.valorEconomizado | number:'1.2-2' }}</td>
                      <td>
                        <span class="badge" [class.success]="mes.taxaSucesso >= 90">
                          {{ mes.taxaSucesso }}%
                        </span>
                      </td>
                    </tr>
                  }
                </tbody>
                <tfoot>
                  <tr>
                    <td><strong>Total</strong></td>
                    <td class="number"><strong>{{ getTotalExecucoes() }}</strong></td>
                    <td class="number"><strong>{{ getTotalArquivos() }}</strong></td>
                    <td class="number"><strong>{{ getTotalCorrecoes() }}</strong></td>
                    <td class="money"><strong>R$ {{ getTotalEconomizado() | number:'1.2-2' }}</strong></td>
                    <td></td>
                  </tr>
                </tfoot>
              </table>
            </div>
          }
        }
      </main>
    </div>
  `,
  styles: [`
    .page-container {
      min-height: 100vh;
      background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
      color: #fff;
    }
    
    .page-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 20px 40px;
      background: rgba(0, 0, 0, 0.2);
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .header-left { display: flex; align-items: center; gap: 20px; }
    .back-btn {
      color: rgba(255, 255, 255, 0.6);
      text-decoration: none;
      padding: 8px 12px;
      border-radius: 8px;
      transition: all 0.2s;
    }
    .back-btn:hover { background: rgba(255, 255, 255, 0.1); color: #fff; }
    .page-header h1 { margin: 0; font-size: 1.5rem; }
    .header-right { display: flex; align-items: center; gap: 15px; }
    .user-info { color: rgba(255, 255, 255, 0.7); }
    .btn-logout {
      padding: 8px 16px;
      border-radius: 8px;
      border: 1px solid rgba(255, 255, 255, 0.3);
      background: transparent;
      color: #fff;
      cursor: pointer;
    }
    
    .tabs {
      display: flex;
      gap: 5px;
      padding: 20px 40px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .tab {
      padding: 12px 24px;
      border: none;
      background: rgba(255, 255, 255, 0.05);
      color: rgba(255, 255, 255, 0.6);
      border-radius: 10px 10px 0 0;
      cursor: pointer;
      transition: all 0.2s;
    }
    
    .tab:hover { background: rgba(255, 255, 255, 0.1); }
    .tab.active {
      background: rgba(0, 217, 255, 0.2);
      color: #00d9ff;
      border-bottom: 2px solid #00d9ff;
    }
    
    .content { padding: 30px 40px; }
    
    .filters-row {
      display: flex;
      align-items: center;
      gap: 15px;
      margin-bottom: 30px;
    }
    
    .filters-row input, .filters-row select {
      padding: 12px;
      border-radius: 10px;
      border: 1px solid rgba(255, 255, 255, 0.1);
      background: rgba(255, 255, 255, 0.05);
      color: #fff;
    }
    
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 20px;
      margin-bottom: 30px;
    }
    
    .stat-card {
      background: rgba(255, 255, 255, 0.05);
      border-radius: 16px;
      padding: 25px;
      text-align: center;
      border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .stat-card.highlight {
      background: linear-gradient(135deg, rgba(0, 217, 255, 0.2) 0%, rgba(0, 168, 204, 0.2) 100%);
      border-color: rgba(0, 217, 255, 0.3);
    }
    
    .stat-value {
      display: block;
      font-size: 2rem;
      font-weight: 700;
      color: #00d9ff;
    }
    
    .stat-label {
      color: rgba(255, 255, 255, 0.6);
      font-size: 0.9rem;
    }
    
    .media-card {
      background: rgba(255, 255, 255, 0.03);
      padding: 20px;
      border-radius: 12px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    
    .media-card .value {
      font-size: 1.5rem;
      font-weight: 600;
      color: #00e676;
    }
    
    .data-table {
      width: 100%;
      border-collapse: collapse;
      background: rgba(255, 255, 255, 0.03);
      border-radius: 12px;
      overflow: hidden;
    }
    
    .data-table th {
      background: rgba(0, 0, 0, 0.3);
      padding: 15px;
      text-align: left;
      font-weight: 600;
    }
    
    .data-table td {
      padding: 15px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .data-table tfoot td {
      background: rgba(0, 0, 0, 0.2);
    }
    
    .code { font-family: monospace; color: #00d9ff; }
    .number { text-align: right; }
    .money { text-align: right; color: #00e676; }
    
    .badge {
      padding: 4px 10px;
      border-radius: 20px;
      font-size: 0.8rem;
    }
    
    .badge.success { background: rgba(0, 230, 118, 0.2); color: #00e676; }
    
    .progress-bar {
      background: rgba(255, 255, 255, 0.1);
      border-radius: 10px;
      height: 24px;
      position: relative;
      overflow: hidden;
    }
    
    .progress {
      background: linear-gradient(90deg, #00d9ff, #00e676);
      height: 100%;
      border-radius: 10px;
    }
    
    .percent {
      position: absolute;
      right: 10px;
      top: 50%;
      transform: translateY(-50%);
      font-size: 0.8rem;
      font-weight: 600;
    }
    
    .loading {
      text-align: center;
      padding: 60px;
      color: rgba(255, 255, 255, 0.5);
    }
  `]
})
export class RelatoriosComponent implements OnInit {
  private relatoriosService = inject(RelatoriosService);
  private authService = inject(AuthService);
  
  currentUser = this.authService.currentUser;
  isLoading = this.relatoriosService.isLoading;
  
  activeTab: 'glosas' | 'efetividade' | 'mensal' = 'glosas';
  
  // Filtros
  dataInicio = '';
  dataFim = '';
  anoSelecionado = new Date().getFullYear();
  anos = Array.from({ length: 5 }, (_, i) => new Date().getFullYear() - i);
  
  // Data
  glosas = signal<RelatorioGlosasEvitadas | null>(null);
  efetividade = signal<RegraEfetividade[]>([]);
  resumoMensal = signal<ResumoMensal[]>([]);
  
  ngOnInit(): void {
    this.loadGlosas();
  }
  
  loadGlosas(): void {
    const filtro: any = {};
    if (this.dataInicio) filtro.dataInicio = new Date(this.dataInicio);
    if (this.dataFim) filtro.dataFim = new Date(this.dataFim);
    
    this.relatoriosService.getGlosasEvitadas(filtro).subscribe(data => {
      this.glosas.set(data);
    });
  }
  
  loadEfetividade(): void {
    this.relatoriosService.getRegrasEfetividade().subscribe(data => {
      this.efetividade.set(data);
    });
  }
  
  loadResumo(): void {
    this.relatoriosService.getResumoMensal(this.anoSelecionado).subscribe(data => {
      this.resumoMensal.set(data);
    });
  }
  
  getTotalExecucoes(): number {
    return this.resumoMensal().reduce((sum, m) => sum + m.totalExecucoes, 0);
  }
  
  getTotalArquivos(): number {
    return this.resumoMensal().reduce((sum, m) => sum + m.totalArquivos, 0);
  }
  
  getTotalCorrecoes(): number {
    return this.resumoMensal().reduce((sum, m) => sum + m.totalCorrecoes, 0);
  }
  
  getTotalEconomizado(): number {
    return this.resumoMensal().reduce((sum, m) => sum + m.valorEconomizado, 0);
  }
  
  logout(): void {
    this.authService.logout();
  }
}
