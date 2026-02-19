import { Component, inject, signal, computed } from '@angular/core';
import { Router, RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { ToastComponent } from '../toast/toast.component';

@Component({
  selector: 'app-layout',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive, ToastComponent],
  template: `
    <div class="layout" [class.sidebar-collapsed]="sidebarCollapsed()">
      <!-- Sidebar -->
      <aside class="sidebar">
        <div class="sidebar-header">
          <div class="logo-area">
            <div class="logo-icon">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
                <path d="M9 12l2 2 4-4" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M12 3a9 9 0 100 18 9 9 0 000-18z" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </div>
            @if (!sidebarCollapsed()) {
              <div class="logo-text">
                <span class="logo-name">AuditPlus</span>
                <span class="logo-version">v2.0</span>
              </div>
            }
          </div>
          <button class="collapse-btn" (click)="toggleSidebar()" [attr.aria-label]="sidebarCollapsed() ? 'Expandir menu' : 'Recolher menu'">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              @if (sidebarCollapsed()) {
                <path d="M9 18l6-6-6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              } @else {
                <path d="M15 18l-6-6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              }
            </svg>
          </button>
        </div>

        <nav class="sidebar-nav">
          <a routerLink="/dashboard" routerLinkActive="active" class="nav-item" [attr.title]="sidebarCollapsed() ? 'Dashboard' : null">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <rect x="3" y="3" width="7" height="7" rx="1.5" stroke="currentColor" stroke-width="2"/>
              <rect x="3" y="14" width="7" height="7" rx="1.5" stroke="currentColor" stroke-width="2"/>
              <rect x="14" y="3" width="7" height="7" rx="1.5" stroke="currentColor" stroke-width="2"/>
              <rect x="14" y="14" width="7" height="7" rx="1.5" stroke="currentColor" stroke-width="2"/>
            </svg>
            @if (!sidebarCollapsed()) { <span>Dashboard</span> }
          </a>

          <a routerLink="/regras" routerLinkActive="active" class="nav-item" [attr.title]="sidebarCollapsed() ? 'Regras' : null">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <rect x="9" y="3" width="6" height="4" rx="1" stroke="currentColor" stroke-width="2"/>
              <path d="M9 12h6M9 16h4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
            @if (!sidebarCollapsed()) { <span>Regras</span> }
          </a>

          <a routerLink="/upload" routerLinkActive="active" class="nav-item" [attr.title]="sidebarCollapsed() ? 'Upload' : null">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <polyline points="17,8 12,3 7,8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <line x1="12" y1="3" x2="12" y2="15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
            @if (!sidebarCollapsed()) { <span>Upload</span> }
          </a>

          <a routerLink="/validation" routerLinkActive="active" class="nav-item" [attr.title]="sidebarCollapsed() ? 'Validação' : null">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path d="M9 12l2 2 4-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" stroke="currentColor" stroke-width="2"/>
            </svg>
            @if (!sidebarCollapsed()) { <span>Validação</span> }
          </a>

          <a routerLink="/relatorios" routerLinkActive="active" class="nav-item" [attr.title]="sidebarCollapsed() ? 'Relatórios' : null">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path d="M18 20V10M12 20V4M6 20v-6" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            @if (!sidebarCollapsed()) { <span>Relatórios</span> }
          </a>

          @if (isAdmin()) {
            <a routerLink="/users" routerLinkActive="active" class="nav-item" [attr.title]="sidebarCollapsed() ? 'Usuários' : null">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path d="M16 21v-2a4 4 0 00-4-4H6a4 4 0 00-4 4v2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <circle cx="9" cy="7" r="4" stroke="currentColor" stroke-width="2"/>
                <path d="M22 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              @if (!sidebarCollapsed()) { <span>Usuários</span> }
            </a>
          }
        </nav>

        <div class="sidebar-footer">
          <div class="user-card" [class.collapsed]="sidebarCollapsed()">
            <div class="user-avatar">
              {{ userInitial() }}
            </div>
            @if (!sidebarCollapsed()) {
              <div class="user-details">
                <span class="user-name">{{ currentUser()?.fullName || currentUser()?.username }}</span>
                <span class="user-role">{{ currentUser()?.role }}</span>
              </div>
            }
          </div>
          <button class="logout-btn" (click)="logout()" [attr.title]="sidebarCollapsed() ? 'Sair' : null">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <polyline points="16,17 21,12 16,7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <line x1="21" y1="12" x2="9" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
            @if (!sidebarCollapsed()) { <span>Sair</span> }
          </button>
        </div>
      </aside>

      <!-- Main Content -->
      <main class="main-content">
        <router-outlet />
      </main>
      
      <!-- Toast Notifications -->
      <app-toast />
    </div>
  `,
  styles: [`
    .layout {
      display: flex;
      min-height: 100vh;
      background: var(--ap-gradient-bg);
    }

    /* --- Sidebar --- */
    .sidebar {
      width: var(--ap-sidebar-width);
      background: rgba(0, 0, 0, 0.3);
      backdrop-filter: blur(20px);
      border-right: 1px solid var(--ap-border);
      display: flex;
      flex-direction: column;
      transition: width var(--ap-transition-normal);
      position: fixed;
      top: 0;
      left: 0;
      bottom: 0;
      z-index: 100;
      overflow-x: hidden;
    }

    .sidebar-collapsed .sidebar {
      width: var(--ap-sidebar-collapsed-width);
    }

    /* Header */
    .sidebar-header {
      padding: 20px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid var(--ap-border);
      min-height: 72px;
    }

    .logo-area {
      display: flex;
      align-items: center;
      gap: 12px;
      overflow: hidden;
    }

    .logo-icon {
      width: 36px;
      height: 36px;
      min-width: 36px;
      border-radius: 10px;
      background: var(--ap-gradient-accent);
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
    }

    .logo-text {
      display: flex;
      flex-direction: column;
      white-space: nowrap;
    }

    .logo-name {
      font-weight: 700;
      font-size: 1.1rem;
      letter-spacing: -0.02em;
    }

    .logo-version {
      font-size: 0.7rem;
      color: var(--ap-text-muted);
      letter-spacing: 0.05em;
    }

    .collapse-btn {
      background: none;
      border: none;
      color: var(--ap-text-muted);
      cursor: pointer;
      padding: 6px;
      border-radius: 6px;
      transition: all var(--ap-transition-fast);
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .collapse-btn:hover {
      background: rgba(255, 255, 255, 0.1);
      color: var(--ap-text-primary);
    }

    /* Navigation */
    .sidebar-nav {
      flex: 1;
      padding: 16px 12px;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .nav-item {
      display: flex;
      align-items: center;
      gap: 14px;
      padding: 12px 14px;
      border-radius: var(--ap-radius-sm);
      color: var(--ap-text-secondary);
      transition: all var(--ap-transition-fast);
      white-space: nowrap;
      font-size: 0.95rem;
      font-weight: 500;
    }

    .nav-item:hover {
      background: rgba(255, 255, 255, 0.08);
      color: var(--ap-text-primary);
    }

    .nav-item.active {
      background: rgba(0, 217, 255, 0.12);
      color: var(--ap-cyan);
    }

    .nav-item.active svg {
      color: var(--ap-cyan);
    }

    .nav-item svg {
      min-width: 20px;
    }

    .sidebar-collapsed .nav-item {
      justify-content: center;
      padding: 12px;
    }

    /* Footer */
    .sidebar-footer {
      padding: 16px 12px;
      border-top: 1px solid var(--ap-border);
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .user-card {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 10px;
      border-radius: var(--ap-radius-sm);
      overflow: hidden;
    }

    .user-card.collapsed {
      justify-content: center;
      padding: 10px 0;
    }

    .user-avatar {
      width: 34px;
      height: 34px;
      min-width: 34px;
      border-radius: 50%;
      background: var(--ap-gradient-accent);
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      font-size: 0.85rem;
    }

    .user-details {
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }

    .user-name {
      font-size: 0.85rem;
      font-weight: 600;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .user-role {
      font-size: 0.7rem;
      color: var(--ap-text-muted);
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }

    .logout-btn {
      display: flex;
      align-items: center;
      gap: 14px;
      padding: 10px 14px;
      border-radius: var(--ap-radius-sm);
      border: none;
      background: none;
      color: var(--ap-text-muted);
      cursor: pointer;
      font-size: 0.9rem;
      transition: all var(--ap-transition-fast);
      width: 100%;
    }

    .logout-btn:hover {
      background: rgba(255, 82, 82, 0.12);
      color: var(--ap-red);
    }

    .sidebar-collapsed .logout-btn {
      justify-content: center;
      padding: 10px;
    }

    /* --- Main Content --- */
    .main-content {
      flex: 1;
      margin-left: var(--ap-sidebar-width);
      min-height: 100vh;
      transition: margin-left var(--ap-transition-normal);
    }

    .sidebar-collapsed .main-content {
      margin-left: var(--ap-sidebar-collapsed-width);
    }

    /* --- Responsive --- */
    @media (max-width: 768px) {
      .sidebar {
        width: var(--ap-sidebar-collapsed-width);
      }

      .main-content {
        margin-left: var(--ap-sidebar-collapsed-width);
      }
    }
  `]
})
export class LayoutComponent {
  private authService = inject(AuthService);
  private router = inject(Router);

  currentUser = this.authService.currentUser;
  sidebarCollapsed = signal(false);

  userInitial = computed(() => {
    const user = this.currentUser();
    if (!user) return '?';
    const name = user.fullName || user.username || '';
    return name.charAt(0).toUpperCase();
  });

  isAdmin = computed(() => {
    const user = this.currentUser();
    return user?.role === 'Admin';
  });

  toggleSidebar(): void {
    this.sidebarCollapsed.update(v => !v);
  }

  logout(): void {
    this.authService.logout();
  }
}
