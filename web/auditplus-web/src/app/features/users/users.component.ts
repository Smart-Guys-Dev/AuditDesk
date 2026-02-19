import { Component, inject, OnInit, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { UsersService, UserResponse, CreateUserRequest, UpdateUserRequest } from '../../core/services/users.service';
import { ToastService } from '../../shared/toast/toast.service';

@Component({
  selector: 'app-users',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="users-page">
      <div class="page-header">
        <div>
          <h1>Gerenciamento de Usuários</h1>
          <p class="subtitle">Administre os usuários do sistema</p>
        </div>
        <button class="btn-primary" (click)="openCreateModal()">
          <span>+</span> Novo Usuário
        </button>
      </div>

      <!-- Search -->
      <div class="search-bar">
        <input 
          type="text" 
          placeholder="Buscar por nome, username ou email..." 
          [ngModel]="searchTerm()" 
          (ngModelChange)="searchTerm.set($event)"
          class="search-input"
        />
      </div>

      <!-- Users Table -->
      <div class="table-container">
        @if (usersService.isLoading()) {
          <div class="loading">Carregando...</div>
        } @else {
          <table class="users-table">
            <thead>
              <tr>
                <th>Usuário</th>
                <th>Nome</th>
                <th>Email</th>
                <th>Perfil</th>
                <th>Último Login</th>
                <th>Ações</th>
              </tr>
            </thead>
            <tbody>
              @for (user of filteredUsers(); track user.id) {
                <tr>
                  <td>
                    <span class="username">{{ user.username }}</span>
                  </td>
                  <td>{{ user.fullName }}</td>
                  <td>{{ user.email }}</td>
                  <td>
                    <span class="badge badge-{{ user.role.toLowerCase() }}">{{ user.role }}</span>
                  </td>
                  <td>{{ user.lastLoginAt ? (user.lastLoginAt | date:'dd/MM/yyyy HH:mm') : 'Nunca' }}</td>
                  <td class="actions">
                    <button class="btn-icon" title="Editar" (click)="openEditModal(user)">✏️</button>
                    <button class="btn-icon" title="Alternar ativo" (click)="toggleUser(user)">
                      {{ user.role === 'Admin' ? '🔒' : '🔄' }}
                    </button>
                    <button class="btn-icon" title="Desbloquear" (click)="unlockUser(user)">🔓</button>
                  </td>
                </tr>
              } @empty {
                <tr><td colspan="6" class="empty">Nenhum usuário encontrado</td></tr>
              }
            </tbody>
          </table>
        }
      </div>

      <!-- Create/Edit Modal -->
      @if (showModal()) {
        <div class="modal-overlay" (click)="closeModal()">
          <div class="modal" (click)="$event.stopPropagation()">
            <div class="modal-header">
              <h2>{{ editingUser() ? 'Editar Usuário' : 'Novo Usuário' }}</h2>
              <button class="modal-close" (click)="closeModal()">×</button>
            </div>
            <form (ngSubmit)="saveUser()" class="modal-form">
              @if (!editingUser()) {
                <div class="form-group">
                  <label>Username</label>
                  <input type="text" [(ngModel)]="formData.username" name="username" required />
                </div>
                <div class="form-group">
                  <label>Senha</label>
                  <input type="password" [(ngModel)]="formData.password" name="password" required />
                  <small>Mín. 8 caracteres, maiúscula, minúscula, dígito e especial</small>
                </div>
              }
              <div class="form-group">
                <label>Nome Completo</label>
                <input type="text" [(ngModel)]="formData.fullName" name="fullName" required />
              </div>
              <div class="form-group">
                <label>Email</label>
                <input type="email" [(ngModel)]="formData.email" name="email" required />
              </div>
              <div class="form-group">
                <label>Perfil</label>
                <select [(ngModel)]="formData.role" name="role">
                  <option value="Admin">Admin</option>
                  <option value="Auditor">Auditor</option>
                  <option value="Viewer">Viewer</option>
                </select>
              </div>
              <div class="modal-actions">
                <button type="button" class="btn-secondary" (click)="closeModal()">Cancelar</button>
                <button type="submit" class="btn-primary">Salvar</button>
              </div>
            </form>
          </div>
        </div>
      }
    </div>
  `,
  styles: [`
    .users-page {
      padding: 0;
    }

    .page-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
    }

    .page-header h1 {
      font-size: 1.6rem;
      font-weight: 700;
      color: var(--text-primary, #f1f5f9);
      margin: 0;
    }

    .subtitle {
      color: var(--text-secondary, #94a3b8);
      font-size: 0.9rem;
      margin: 4px 0 0;
    }

    .btn-primary {
      background: linear-gradient(135deg, var(--primary, #6366f1), var(--primary-dark, #4f46e5));
      color: white;
      border: none;
      padding: 10px 20px;
      border-radius: 10px;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 8px;
      transition: all 0.2s;
    }
    .btn-primary:hover {
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
    }

    .search-bar {
      margin-bottom: 20px;
    }

    .search-input {
      width: 100%;
      padding: 12px 16px;
      border-radius: 10px;
      border: 1px solid var(--border, rgba(148, 163, 184, 0.15));
      background: var(--surface, rgba(30, 41, 59, 0.5));
      color: var(--text-primary, #f1f5f9);
      font-size: 0.9rem;
      outline: none;
      transition: border-color 0.2s;
    }
    .search-input:focus {
      border-color: var(--primary, #6366f1);
    }
    .search-input::placeholder {
      color: var(--text-secondary, #94a3b8);
    }

    .table-container {
      background: var(--surface, rgba(30, 41, 59, 0.5));
      border-radius: 14px;
      border: 1px solid var(--border, rgba(148, 163, 184, 0.1));
      overflow: hidden;
    }

    .users-table {
      width: 100%;
      border-collapse: collapse;
    }

    .users-table th {
      text-align: left;
      padding: 14px 16px;
      font-size: 0.8rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--text-secondary, #94a3b8);
      border-bottom: 1px solid var(--border, rgba(148, 163, 184, 0.1));
    }

    .users-table td {
      padding: 14px 16px;
      font-size: 0.9rem;
      color: var(--text-primary, #f1f5f9);
      border-bottom: 1px solid var(--border, rgba(148, 163, 184, 0.05));
    }

    .users-table tr:hover td {
      background: rgba(99, 102, 241, 0.05);
    }

    .username {
      font-weight: 600;
      color: var(--primary, #6366f1);
    }

    .badge {
      padding: 4px 10px;
      border-radius: 6px;
      font-size: 0.75rem;
      font-weight: 600;
      text-transform: uppercase;
    }
    .badge-admin { background: rgba(239, 68, 68, 0.15); color: #f87171; }
    .badge-auditor { background: rgba(99, 102, 241, 0.15); color: #818cf8; }
    .badge-viewer { background: rgba(16, 185, 129, 0.15); color: #34d399; }

    .actions {
      display: flex;
      gap: 6px;
    }

    .btn-icon {
      background: none;
      border: 1px solid var(--border, rgba(148, 163, 184, 0.15));
      border-radius: 8px;
      padding: 6px 10px;
      cursor: pointer;
      font-size: 0.85rem;
      transition: all 0.2s;
    }
    .btn-icon:hover {
      background: rgba(99, 102, 241, 0.1);
      border-color: var(--primary, #6366f1);
    }

    .empty, .loading {
      text-align: center;
      padding: 40px;
      color: var(--text-secondary, #94a3b8);
    }

    /* Modal */
    .modal-overlay {
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.6);
      backdrop-filter: blur(4px);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 1000;
    }

    .modal {
      background: var(--bg-card, #1e293b);
      border-radius: 16px;
      border: 1px solid var(--border, rgba(148, 163, 184, 0.15));
      width: 100%;
      max-width: 480px;
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
    }

    .modal-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 20px 24px;
      border-bottom: 1px solid var(--border, rgba(148, 163, 184, 0.1));
    }

    .modal-header h2 {
      margin: 0;
      font-size: 1.2rem;
      color: var(--text-primary, #f1f5f9);
    }

    .modal-close {
      background: none;
      border: none;
      color: var(--text-secondary, #94a3b8);
      font-size: 1.5rem;
      cursor: pointer;
    }

    .modal-form {
      padding: 24px;
    }

    .form-group {
      margin-bottom: 18px;
    }

    .form-group label {
      display: block;
      font-size: 0.85rem;
      font-weight: 600;
      color: var(--text-secondary, #94a3b8);
      margin-bottom: 6px;
    }

    .form-group input, .form-group select {
      width: 100%;
      padding: 10px 14px;
      border-radius: 8px;
      border: 1px solid var(--border, rgba(148, 163, 184, 0.15));
      background: var(--surface, rgba(15, 23, 42, 0.5));
      color: var(--text-primary, #f1f5f9);
      font-size: 0.9rem;
      outline: none;
      transition: border-color 0.2s;
      box-sizing: border-box;
    }
    .form-group input:focus, .form-group select:focus {
      border-color: var(--primary, #6366f1);
    }

    .form-group small {
      display: block;
      margin-top: 4px;
      font-size: 0.75rem;
      color: var(--text-secondary, #94a3b8);
    }

    .modal-actions {
      display: flex;
      gap: 12px;
      justify-content: flex-end;
      margin-top: 24px;
    }

    .btn-secondary {
      background: transparent;
      border: 1px solid var(--border, rgba(148, 163, 184, 0.2));
      color: var(--text-secondary, #94a3b8);
      padding: 10px 20px;
      border-radius: 10px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
    }
    .btn-secondary:hover {
      border-color: var(--text-secondary, #94a3b8);
      color: var(--text-primary, #f1f5f9);
    }
  `]
})
export class UsersComponent implements OnInit {
  usersService = inject(UsersService);
  private toast = inject(ToastService);

  searchTerm = signal('');
  showModal = signal(false);
  editingUser = signal<UserResponse | null>(null);

  formData: any = {
    username: '',
    password: '',
    fullName: '',
    email: '',
    role: 'Auditor'
  };

  filteredUsers = computed(() => {
    const term = this.searchTerm().toLowerCase();
    const users = this.usersService.users();
    if (!term) return users;
    return users.filter(u =>
      u.username.toLowerCase().includes(term) ||
      u.fullName.toLowerCase().includes(term) ||
      u.email.toLowerCase().includes(term)
    );
  });

  ngOnInit(): void {
    this.usersService.loadAll().subscribe();
  }

  openCreateModal(): void {
    this.editingUser.set(null);
    this.formData = { username: '', password: '', fullName: '', email: '', role: 'Auditor' };
    this.showModal.set(true);
  }

  openEditModal(user: UserResponse): void {
    this.editingUser.set(user);
    this.formData = { fullName: user.fullName, email: user.email, role: user.role };
    this.showModal.set(true);
  }

  closeModal(): void {
    this.showModal.set(false);
    this.editingUser.set(null);
  }

  saveUser(): void {
    const editing = this.editingUser();
    if (editing) {
      const req: UpdateUserRequest = {
        fullName: this.formData.fullName,
        email: this.formData.email,
        role: this.formData.role
      };
      this.usersService.update(editing.id, req).subscribe({
        next: () => {
          this.toast.success('Usuário atualizado com sucesso');
          this.closeModal();
          this.usersService.loadAll().subscribe();
        },
        error: (err) => this.toast.error(err?.error?.message || 'Erro ao atualizar')
      });
    } else {
      const req: CreateUserRequest = {
        username: this.formData.username,
        password: this.formData.password,
        fullName: this.formData.fullName,
        email: this.formData.email,
        role: this.formData.role
      };
      this.usersService.create(req).subscribe({
        next: () => {
          this.toast.success('Usuário criado com sucesso');
          this.closeModal();
        },
        error: (err) => this.toast.error(err?.error?.message || 'Erro ao criar usuário')
      });
    }
  }

  toggleUser(user: UserResponse): void {
    this.usersService.toggle(user.id).subscribe({
      next: (result) => {
        this.toast.success(`Usuário ${result?.isActive ? 'ativado' : 'desativado'}`);
        this.usersService.loadAll().subscribe();
      },
      error: (err) => this.toast.error(err?.error?.message || 'Erro ao alternar')
    });
  }

  unlockUser(user: UserResponse): void {
    this.usersService.unlock(user.id).subscribe({
      next: () => {
        this.toast.success('Conta desbloqueada');
        this.usersService.loadAll().subscribe();
      },
      error: (err) => this.toast.error(err?.error?.message || 'Erro ao desbloquear')
    });
  }
}
