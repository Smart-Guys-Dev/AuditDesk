import { Component, inject, OnInit, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { RegrasService } from '../../core/services/regras.service';
import { AuthService } from '../../core/services/auth.service';
import { Regra, RegraCreate, RuleCategory, RuleGroup } from '../../core/models/regra.model';

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
        
        <button class="btn-add" (click)="openAddModal()">
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
                    <button class="btn-icon" title="Editar" (click)="openEditModal(regra)">✏️</button>
                    <button class="btn-icon" title="Excluir" (click)="deleteRegra(regra)">🗑️</button>
                  </td>
                </tr>
              }
            </tbody>
          </table>
        }
      </div>
      
      <!-- Modal Add/Edit -->
      @if (showModal) {
        <div class="modal-overlay" (click)="closeModal()">
          <div class="modal-content" (click)="$event.stopPropagation()">
            <div class="modal-header">
              <h2>{{ editingRegra ? 'Editar Regra' : 'Nova Regra' }}</h2>
              <button class="modal-close" (click)="closeModal()">×</button>
            </div>
            
            <form (ngSubmit)="saveRegra()" class="modal-form">
              <div class="form-row">
                <label>Código *</label>
                <input type="text" [(ngModel)]="formData.codigo" name="codigo" required [disabled]="!!editingRegra">
              </div>
              
              <div class="form-row">
                <label>Nome *</label>
                <input type="text" [(ngModel)]="formData.nome" name="nome" required>
              </div>
              
              <div class="form-row">
                <label>Descrição</label>
                <textarea [(ngModel)]="formData.descricao" name="descricao" rows="3"></textarea>
              </div>
              
              <div class="form-grid">
                <div class="form-row">
                  <label>Categoria</label>
                  <select [(ngModel)]="formData.categoria" name="categoria">
                    <option value="GLOSA_GUIA">Glosa Guia</option>
                    <option value="GLOSA_ITEM">Glosa Item</option>
                    <option value="VALIDACAO">Validação</option>
                    <option value="OTIMIZACAO">Otimização</option>
                  </select>
                </div>
                
                <div class="form-row">
                  <label>Grupo</label>
                  <select [(ngModel)]="formData.grupo" name="grupo">
                    <option value="DATAS">Datas</option>
                    <option value="VALORES">Valores</option>
                    <option value="PRESTADOR">Prestador</option>
                    <option value="DUPLICIDADES">Duplicidades</option>
                    <option value="EQUIPE_PROF">Equipe Prof</option>
                    <option value="OUTROS">Outros</option>
                  </select>
                </div>
              </div>
              
              <div class="form-row">
                <label>Prioridade (menor = maior prioridade)</label>
                <input type="number" [(ngModel)]="formData.prioridade" name="prioridade" min="1" max="999">
              </div>
              
              <div class="modal-actions">
                <button type="button" class="btn-cancel" (click)="closeModal()">Cancelar</button>
                <button type="submit" class="btn-save">{{ editingRegra ? 'Salvar' : 'Criar' }}</button>
              </div>
            </form>
          </div>
        </div>
      }
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
    
    .toolbar {
      display: flex;
      gap: 20px;
      padding: 20px 40px;
      align-items: center;
      flex-wrap: wrap;
    }
    
    .search-box { flex: 1; min-width: 200px; }
    
    .search-box input {
      width: 100%;
      padding: 12px 16px;
      border-radius: 10px;
      border: 1px solid rgba(255, 255, 255, 0.1);
      background: rgba(255, 255, 255, 0.05);
      color: #fff;
      font-size: 1rem;
    }
    
    .filters { display: flex; gap: 10px; }
    
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
    
    .btn-add:hover { transform: translateY(-2px); }
    
    .stats-bar {
      padding: 10px 40px;
      display: flex;
      gap: 30px;
      color: rgba(255, 255, 255, 0.6);
      font-size: 0.9rem;
    }
    
    .table-container { padding: 0 40px 40px; }
    
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
    
    .data-table tr:hover { background: rgba(255, 255, 255, 0.02); }
    .data-table tr.inactive { opacity: 0.5; }
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
    
    /* Modal */
    .modal-overlay {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.7);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 1000;
    }
    
    .modal-content {
      background: linear-gradient(145deg, #1e2a45 0%, #16213e 100%);
      border-radius: 20px;
      padding: 30px;
      width: 100%;
      max-width: 500px;
      border: 1px solid rgba(255, 255, 255, 0.1);
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
    }
    
    .modal-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 25px;
    }
    
    .modal-header h2 { margin: 0; font-size: 1.4rem; }
    
    .modal-close {
      background: none;
      border: none;
      color: #fff;
      font-size: 2rem;
      cursor: pointer;
      opacity: 0.6;
    }
    
    .modal-close:hover { opacity: 1; }
    
    .modal-form { display: flex; flex-direction: column; gap: 20px; }
    
    .form-row { display: flex; flex-direction: column; gap: 8px; }
    
    .form-row label {
      font-size: 0.9rem;
      color: rgba(255, 255, 255, 0.7);
    }
    
    .form-row input,
    .form-row select,
    .form-row textarea {
      padding: 12px;
      border-radius: 10px;
      border: 1px solid rgba(255, 255, 255, 0.1);
      background: rgba(255, 255, 255, 0.05);
      color: #fff;
      font-size: 1rem;
    }
    
    .form-row input:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
    
    .form-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 15px;
    }
    
    .modal-actions {
      display: flex;
      gap: 15px;
      justify-content: flex-end;
      margin-top: 10px;
    }
    
    .btn-cancel {
      padding: 12px 24px;
      border-radius: 10px;
      border: 1px solid rgba(255, 255, 255, 0.2);
      background: transparent;
      color: #fff;
      cursor: pointer;
    }
    
    .btn-save {
      padding: 12px 24px;
      border-radius: 10px;
      border: none;
      background: linear-gradient(135deg, #00d9ff 0%, #00a8cc 100%);
      color: #fff;
      font-weight: 600;
      cursor: pointer;
    }
    
    .btn-save:hover { transform: translateY(-1px); }
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
  
  showModal = false;
  editingRegra: Regra | null = null;
  
  formData = {
    codigo: '',
    nome: '',
    descricao: '',
    categoria: 'VALIDACAO' as RuleCategory,
    grupo: 'OUTROS' as RuleGroup,
    prioridade: 100
  };
  
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
  
  openAddModal(): void {
    this.editingRegra = null;
    this.formData = {
      codigo: '',
      nome: '',
      descricao: '',
      categoria: 'VALIDACAO',
      grupo: 'OUTROS',
      prioridade: 100
    };
    this.showModal = true;
  }
  
  openEditModal(regra: Regra): void {
    this.editingRegra = regra;
    this.formData = {
      codigo: regra.codigo,
      nome: regra.nome,
      descricao: regra.descricao || '',
      categoria: regra.categoria,
      grupo: regra.grupo,
      prioridade: regra.prioridade
    };
    this.showModal = true;
  }
  
  closeModal(): void {
    this.showModal = false;
    this.editingRegra = null;
  }
  
  saveRegra(): void {
    if (this.editingRegra) {
      // Atualizar
      const updated: Regra = {
        ...this.editingRegra,
        nome: this.formData.nome,
        descricao: this.formData.descricao,
        categoria: this.formData.categoria,
        grupo: this.formData.grupo,
        prioridade: this.formData.prioridade
      };
      this.regrasService.update(this.editingRegra.id, updated).subscribe(success => {
        if (success) {
          this.closeModal();
          this.regrasService.loadAll().subscribe();
        }
      });
    } else {
      // Criar
      const newRegra: RegraCreate = {
        codigo: this.formData.codigo,
        nome: this.formData.nome,
        descricao: this.formData.descricao,
        categoria: this.formData.categoria,
        grupo: this.formData.grupo,
        prioridade: this.formData.prioridade,
        ativo: true
      };
      this.regrasService.create(newRegra).subscribe(created => {
        if (created) {
          this.closeModal();
        }
      });
    }
  }
  
  deleteRegra(regra: Regra): void {
    if (confirm(`Tem certeza que deseja excluir a regra "${regra.codigo}"?`)) {
      this.regrasService.delete(regra.id).subscribe();
    }
  }
  
  logout(): void {
    this.authService.logout();
  }
}
