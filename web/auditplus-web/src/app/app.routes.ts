import { Routes } from '@angular/router';
import { authGuard, guestGuard } from './core/guards/auth.guard';

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'dashboard',
    pathMatch: 'full'
  },
  {
    path: 'login',
    loadComponent: () => import('./features/login/login.component').then(m => m.LoginComponent),
    canActivate: [guestGuard]
  },
  {
    // All authenticated routes wrapped in Layout
    path: '',
    loadComponent: () => import('./shared/layout/layout.component').then(m => m.LayoutComponent),
    canActivate: [authGuard],
    children: [
      {
        path: 'dashboard',
        loadComponent: () => import('./features/dashboard/dashboard.component').then(m => m.DashboardComponent)
      },
      {
        path: 'regras',
        loadComponent: () => import('./features/regras/regras.component').then(m => m.RegrasComponent)
      },
      {
        path: 'upload',
        loadComponent: () => import('./features/upload/upload.component').then(m => m.UploadComponent)
      },
      {
        path: 'validation',
        loadComponent: () => import('./features/validation/validation.component').then(m => m.ValidationComponent)
      },
      {
        path: 'relatorios',
        loadComponent: () => import('./features/relatorios/relatorios.component').then(m => m.RelatoriosComponent)
      },
      {
        path: 'users',
        loadComponent: () => import('./features/users/users.component').then(m => m.UsersComponent)
      }
    ]
  },
  {
    path: '**',
    redirectTo: 'dashboard'
  }
];
