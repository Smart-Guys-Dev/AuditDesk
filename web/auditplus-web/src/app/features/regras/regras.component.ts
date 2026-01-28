import { Component, inject, OnInit, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { RegrasService } from '../../core/services/regras.service';
import { AuthService } from '../../core/services/auth.service';
import { Regra, RuleCategory, RuleGroup } from '../../core/models/regra.model';

@Component({
  selector: 'app-regras',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  template: `
    <div class="page-container">
      <!-- Header -->
      <header class="page-header">
        <div class="header-left">
          <a routerLink="/dashboard" class="back-btn">← Dashboard</a>
          <h1>📋 Regras de Auditoria</h1>
        </div>
        <div class="header-right">
          <span class="user-info">{{ currentUser()?.fullName }}</span>
          <button class="btn-logout" (click)="logout()">Sair</button>
        </div>
      </header>
      
      <!-- Toolbar -->
      <div class="toolbar">
        <div class="search-box">
          <input 
            type="text" 
            [(ngModel)]="searchTerm"
            placeholder="🔍 Buscar regras..."
          >
        </div>
        
        <div class="filters">
          <select [(ngModel)]="filterCategoria">
            <option value="">Todas Categorias</option>
            <option value="GLOSA_GUIA">Glosa Guia</option>
            <option value="GLOSA_ITEM">Glosa Item</option>
            <option value="VALIDACAO">Validação</option>
            <option value="OTIMIZACAO">Otimização</option>
          </select>
          
          <select [(ngModel)]="filterAtivo">
            <option value="">Todas</option>
            <option value="true">Ativas</option>
            <option value="false">Inativas</option>
          </select>
        </div>
        
        <button class="btn-add" (click)="showAddModal = true">
          + Nova Regra
        </button>
      </div>
      
      <!-- Stats -->
      <div class="stats-bar">
        <span>Total: {{ regras().length }}</span>
        <span>Ativas: {{ regrasAtivas() }}</span>
        <span>Filtradas: {{ regrasFiltradas().length }}</span>
      </div>
      
      <!-- Table -->
      <div class="table-container">
        @if (isLoading()) {
          <div class="loading">Carregando...</div>
        } @else if (regrasFiltradas().length === 0) {
          <div class="empty">Nenhuma regra encontrada</div>
        } @else {
          <table class="data-table">
            <thead>
              <tr>
                <th>Código</th>
                <th>Nome</th>
                <th>Categoria</th>
                <th>Grupo</th>
                <th>Prioridade</th>
                <th>Status</th>
                <th>Ações</th>
              </tr>
            </thead>
            <tbody>
              @for (regra of regrasFiltradas(); track regra.id) {
                <tr [class.inactive]="!regra.ativo">
                  <td class="code">{{ regra.codigo }}</td>
                  <td>{{ regra.nome }}</td>
                  <td>
                    <span class="badge" [class]="getCategoriaClass(regra.categoria)">
                      {{ regra.categoria }}
                    </span>
                  </td>
                  <td>{{ regra.grupo }}</td>
                  <td class="priority">{{ regra.prioridade }}</td>
                  <td>
                    <button 
                      class="status-toggle"
                      [class.active]="regra.ativo"
                      (click)="toggleRegra(regra)"
                    >
                      {{ regra.ativo ? '✓ Ativa' : '✗ Inativa' }}
                    </button>
                  </td>
                  <td class="actions">
                    <button class="btn-icon" title="Editar" (click)="editRegra(regra)">✏️</button>
                    <button class="btn-icon" title="Excluir" (click)="deleteRegra(regra)">🗑️</button>
                  </td>
                </tr>
              }
            </tbody>
          </table>
        }
      </div>
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
    
    .header-left {
      display: flex;
      align-items: center;
      gap: 20px;
    }
    
    .back-btn {
      color: rgba(255, 255, 255, 0.6);
      text-decoration: none;
      padding: 8px 12px;
      border-radius: 8px;
      transition: all 0.2s;
    }
    
    .back-btn:hover {
      background: rgba(255, 255, 255, 0.1);
      color: #fff;
    }
    
    .page-header h1 { margin: 0; font-size: 1.5rem; }
    
    .header-right {
      display: flex;
      align-items: center;
      gap: 15px;
    }
    
    .user-info { color: rgba(255, 255, 255, 0.7); }
    
    .btn-logout {
      padding: 8px 16px;
      border-radius: 8px;
      border: 1px solid rgba(255, 255, 255, 0.3);
      background: transparent;
      color: #fff;
      cursor: pointer;
    }
    
    .toolbar {
      display: flex;
      gap: 20px;
      padding: 20px 40px;
      align-items: center;
      flex-wrap: wrap;
    }
    
    .search-box {
      flex: 1;
      min-width: 200px;
    }
    
    .search-box input {
      width: 100%;
      padding: 12px 16px;
      border-radius: 10px;
      border: 1px solid rgba(255, 255, 255, 0.1);
      background: rgba(255, 255, 255, 0.05);
      color: #fff;
      font-size: 1rem;
    }
    
    .filters {
      display: flex;
      gap: 10px;
    }
    
    .filters select {
      padding: 12px;
      border-radius: 10px;
      border: 1px solid rgba(255, 255, 255, 0.1);
      background: rgba(255, 255, 255, 0.05);
      color: #fff;
    }
    
    .btn-add {
      padding: 12px 24px;
      border-radius: 10px;
      border: none;
      background: linear-gradient(135deg, #00d9ff 0%, #00a8cc 100%);
      color: #fff;
      font-weight: 600;
      cursor: pointer;
      transition: transform 0.2s;
    }
    
    .btn-add:hover {
      transform: translateY(-2px);
    }
    
    .stats-bar {
      padding: 10px 40px;
      display: flex;
      gap: 30px;
      color: rgba(255, 255, 255, 0.6);
      font-size: 0.9rem;
    }
    
    .table-container {
      padding: 0 40px 40px;
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
      color: rgba(255, 255, 255, 0.8);
    }
    
    .data-table td {
      padding: 15px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .data-table tr:hover {
      background: rgba(255, 255, 255, 0.02);
    }
    
    .data-table tr.inactive {
      opacity: 0.5;
    }
    
    .code { font-family: monospace; color: #00d9ff; }
    .priority { text-align: center; }
    
    .badge {
      padding: 4px 10px;
      border-radius: 20px;
      font-size: 0.8rem;
      font-weight: 500;
    }
    
    .badge.glosa-guia { background: rgba(255, 82, 82, 0.2); color: #ff5252; }
    .badge.glosa-item { background: rgba(255, 152, 0, 0.2); color: #ff9800; }
    .badge.validacao { background: rgba(0, 230, 118, 0.2); color: #00e676; }
    .badge.otimizacao { background: rgba(0, 217, 255, 0.2); color: #00d9ff; }
    
    .status-toggle {
      padding: 6px 12px;
      border-radius: 20px;
      border: none;
      cursor: pointer;
      font-size: 0.85rem;
      transition: all 0.2s;
    }
    
    .status-toggle.active {
      background: rgba(0, 230, 118, 0.2);
      color: #00e676;
    }
    
    .status-toggle:not(.active) {
      background: rgba(255, 255, 255, 0.1);
      color: rgba(255, 255, 255, 0.5);
    }
    
    .actions { display: flex; gap: 8px; }
    
    .btn-icon {
      background: none;
      border: none;
      font-size: 1.1rem;
      cursor: pointer;
      padding: 5px;
      opacity: 0.7;
      transition: opacity 0.2s;
    }
    
    .btn-icon:hover { opacity: 1; }
    
    .loading, .empty {
      text-align: center;
      padding: 60px;
      color: rgba(255, 255, 255, 0.5);
    }
  `]
})
export class RegrasComponent implements OnInit {
  private regrasService = inject(RegrasService);
  private authService = inject(AuthService);
  
  regras = this.regrasService.regras;
  isLoading = this.regrasService.isLoading;
  currentUser = this.authService.currentUser;
  
  searchTerm = '';
  filterCategoria = '';
  filterAtivo = '';
  showAddModal = false;
  
  regrasAtivas = computed(() => this.regras().filter(r => r.ativo).length);
  
  regrasFiltradas = computed(() => {
    let result = this.regras();
    
    if (this.searchTerm) {
      const term = this.searchTerm.toLowerCase();
      result = result.filter(r => 
        r.codigo.toLowerCase().includes(term) ||
        r.nome.toLowerCase().includes(term)
      );
    }
    
    if (this.filterCategoria) {
      result = result.filter(r => r.categoria === this.filterCategoria);
    }
    
    if (this.filterAtivo !== '') {
      const isAtivo = this.filterAtivo === 'true';
      result = result.filter(r => r.ativo === isAtivo);
    }
    
    return result;
  });
  
  ngOnInit(): void {
    this.regrasService.loadAll().subscribe();
  }
  
  getCategoriaClass(categoria: RuleCategory): string {
    return categoria.toLowerCase().replace('_', '-');
  }
  
  toggleRegra(regra: Regra): void {
    this.regrasService.toggle(regra.id).subscribe();
  }
  
  editRegra(regra: Regra): void {
    // TODO: Abrir modal de edição
    console.log('Editar:', regra);
  }
  
  deleteRegra(regra: Regra): void {
    if (confirm(`Excluir regra ${regra.codigo}?`)) {
      this.regrasService.delete(regra.id).subscribe();
    }
  }
  
  logout(): void {
    this.authService.logout();
  }
}
