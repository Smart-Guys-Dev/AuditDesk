import { Component, inject, OnInit, signal, computed } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RegrasService } from '../../core/services/regras.service';
import { Regra, RegraCreate, RuleCategory, RuleGroup } from '../../core/models/regra.model';

@Component({
  selector: 'app-regras',
  standalone: true,
  imports: [FormsModule],
  template: `
    <div class="regras-page">
      <div class="page-title">
        <h1>Regras de Auditoria</h1>
      </div>
      
      <!-- Toolbar -->
      <div class="toolbar">
        <div class="search-box">
          <input 
            type="text" 
            [ngModel]="searchTerm()"
            (ngModelChange)="searchTerm.set($event)"
            placeholder="Buscar regras..."
          >
        </div>
        
        <div class="filters">
          <select [ngModel]="filterCategoria()" (ngModelChange)="filterCategoria.set($event)">
            <option value="">Todas Categorias</option>
            <option value="GLOSA_GUIA">Glosa Guia</option>
            <option value="GLOSA_ITEM">Glosa Item</option>
            <option value="VALIDACAO">Validação</option>
            <option value="OTIMIZACAO">Otimização</option>
          </select>
          
          <select [ngModel]="filterAtivo()" (ngModelChange)="filterAtivo.set($event)">
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
    .regras-page {
      padding: var(--ap-page-padding);
    }

    .page-title h1 {
      font-size: 1.8rem;
      font-weight: 700;
      margin: 0 0 24px;
    }

    .toolbar {
      display: flex;
      gap: 16px;
      margin-bottom: 16px;
      align-items: center;
      flex-wrap: wrap;
    }

    .search-box { flex: 1; min-width: 200px; }

    .search-box input {
      width: 100%;
      padding: 12px 16px;
      border-radius: var(--ap-radius-md);
      border: 1px solid var(--ap-border);
      background: var(--ap-bg-input);
      color: var(--ap-text-primary);
      font-size: 1rem;
    }

    .search-box input:focus { outline: none; border-color: var(--ap-cyan); }

    .filters { display: flex; gap: 10px; }

    .filters select {
      padding: 12px;
      border-radius: var(--ap-radius-md);
      border: 1px solid var(--ap-border);
      background: var(--ap-bg-input);
      color: var(--ap-text-primary);
    }

    .btn-add {
      padding: 12px 24px;
      border-radius: var(--ap-radius-md);
      border: none;
      background: var(--ap-gradient-accent);
      color: #fff;
      font-weight: 600;
      cursor: pointer;
      transition: transform var(--ap-transition-fast);
    }

    .btn-add:hover { transform: translateY(-2px); }

    .stats-bar {
      padding: 8px 0;
      display: flex;
      gap: 24px;
      color: var(--ap-text-muted);
      font-size: 0.85rem;
      margin-bottom: 16px;
    }

    .table-container { margin-bottom: 40px; }
    .priority { text-align: center; }
    .actions { display: flex; gap: 8px; }

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
      color: var(--ap-green);
    }

    .status-toggle:not(.active) {
      background: rgba(255, 255, 255, 0.1);
      color: var(--ap-text-muted);
    }

    .modal-form { display: flex; flex-direction: column; gap: 20px; }

    .btn-cancel {
      padding: 12px 24px;
      border-radius: var(--ap-radius-md);
      border: 1px solid var(--ap-border-medium);
      background: transparent;
      color: #fff;
      cursor: pointer;
    }

    .btn-save {
      padding: 12px 24px;
      border-radius: var(--ap-radius-md);
      border: none;
      background: var(--ap-gradient-accent);
      color: #fff;
      font-weight: 600;
      cursor: pointer;
      transition: transform var(--ap-transition-fast);
    }

    .btn-save:hover { transform: translateY(-1px); }
  `]
})
export class RegrasComponent implements OnInit {
  private regrasService = inject(RegrasService);
  
  regras = this.regrasService.regras;
  isLoading = this.regrasService.isLoading;
  
  searchTerm = signal('');
  filterCategoria = signal('');
  filterAtivo = signal('');
  
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
    
    const term = this.searchTerm();
    if (term) {
      const lowerTerm = term.toLowerCase();
      result = result.filter(r => 
        r.codigo.toLowerCase().includes(lowerTerm) ||
        r.nome.toLowerCase().includes(lowerTerm)
      );
    }
    
    const cat = this.filterCategoria();
    if (cat) {
      result = result.filter(r => r.categoria === cat);
    }
    
    const ativo = this.filterAtivo();
    if (ativo !== '') {
      const isAtivo = ativo === 'true';
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
}
