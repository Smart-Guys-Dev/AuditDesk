import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="login-container">
      <div class="login-card">
        <div class="login-header">
          <h1>🔒 AuditPlus</h1>
          <p>Sistema de Auditoria TISS</p>
        </div>
        
        <form (ngSubmit)="onSubmit()" class="login-form">
          @if (error()) {
            <div class="error-message">
              {{ error() }}
            </div>
          }
          
          <div class="form-group">
            <label for="username">Usuário</label>
            <input 
              type="text" 
              id="username"
              [(ngModel)]="username" 
              name="username"
              placeholder="Digite seu usuário"
              required
              [disabled]="isLoading()"
            >
          </div>
          
          <div class="form-group">
            <label for="password">Senha</label>
            <input 
              type="password" 
              id="password"
              [(ngModel)]="password" 
              name="password"
              placeholder="Digite sua senha"
              required
              [disabled]="isLoading()"
            >
          </div>
          
          <button 
            type="submit" 
            class="btn-login"
            [disabled]="isLoading() || !username || !password"
          >
            @if (isLoading()) {
              <span class="spinner"></span> Entrando...
            } @else {
              Entrar
            }
          </button>
        </form>
        
        <div class="login-footer">
          <small>AuditPlus Web v1.0</small>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .login-container {
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
      padding: 20px;
    }
    
    .login-card {
      background: rgba(255, 255, 255, 0.05);
      backdrop-filter: blur(10px);
      border-radius: 20px;
      padding: 40px;
      width: 100%;
      max-width: 400px;
      box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5);
      border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .login-header {
      text-align: center;
      margin-bottom: 30px;
    }
    
    .login-header h1 {
      font-size: 2rem;
      color: #fff;
      margin: 0 0 10px 0;
    }
    
    .login-header p {
      color: rgba(255, 255, 255, 0.6);
      margin: 0;
    }
    
    .login-form {
      display: flex;
      flex-direction: column;
      gap: 20px;
    }
    
    .form-group {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    
    .form-group label {
      color: rgba(255, 255, 255, 0.8);
      font-size: 0.9rem;
    }
    
    .form-group input {
      padding: 15px;
      border-radius: 10px;
      border: 1px solid rgba(255, 255, 255, 0.1);
      background: rgba(255, 255, 255, 0.05);
      color: #fff;
      font-size: 1rem;
      transition: all 0.3s ease;
    }
    
    .form-group input:focus {
      outline: none;
      border-color: #00d9ff;
      box-shadow: 0 0 0 3px rgba(0, 217, 255, 0.2);
    }
    
    .form-group input::placeholder {
      color: rgba(255, 255, 255, 0.3);
    }
    
    .btn-login {
      padding: 15px;
      border-radius: 10px;
      border: none;
      background: linear-gradient(135deg, #00d9ff 0%, #00a8cc 100%);
      color: #fff;
      font-size: 1rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.3s ease;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
    }
    
    .btn-login:hover:not(:disabled) {
      transform: translateY(-2px);
      box-shadow: 0 10px 30px rgba(0, 217, 255, 0.3);
    }
    
    .btn-login:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }
    
    .spinner {
      width: 20px;
      height: 20px;
      border: 2px solid transparent;
      border-top-color: #fff;
      border-radius: 50%;
      animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
      to { transform: rotate(360deg); }
    }
    
    .error-message {
      background: rgba(255, 82, 82, 0.2);
      border: 1px solid rgba(255, 82, 82, 0.5);
      color: #ff5252;
      padding: 12px;
      border-radius: 8px;
      text-align: center;
      font-size: 0.9rem;
    }
    
    .login-footer {
      text-align: center;
      margin-top: 30px;
      color: rgba(255, 255, 255, 0.4);
    }
  `]
})
export class LoginComponent {
  private authService = inject(AuthService);
  private router = inject(Router);
  private route = inject(ActivatedRoute);
  
  username = '';
  password = '';
  error = signal<string | null>(null);
  isLoading = this.authService.isLoading;
  
  onSubmit(): void {
    this.error.set(null);
    
    this.authService.login({ username: this.username, password: this.password })
      .subscribe(response => {
        if (response) {
          const returnUrl = this.route.snapshot.queryParams['returnUrl'] || '/dashboard';
          this.router.navigate([returnUrl]);
        } else {
          this.error.set('Usuário ou senha inválidos');
        }
      });
  }
}
