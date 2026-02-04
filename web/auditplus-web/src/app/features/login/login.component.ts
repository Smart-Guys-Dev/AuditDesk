import { Component, inject, signal, AfterViewInit, ElementRef, ViewChild } from '@angular/core';
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
      
      <!-- LADO ESQUERDO: Branding -->
      <aside class="branding-side">
        <!-- Decoração de fundo -->
        <div class="bg-decoration">
          <div class="circle circle-1"></div>
          <div class="circle circle-2"></div>
          <div class="circle circle-3"></div>
        </div>
        
        <!-- Conteúdo do branding -->
        <div class="branding-content">

          <!-- Ícone do App (Logo Vetorial Personalizado) -->
          <!-- Ícone do App (Logo Ribbon A+) -->
          <div class="app-icon-3d">
          <div class="app-icon-3d">
            <img src="logo-auditplus-new.png" alt="Logo AuditPlus" class="app-icon-img">
          </div>
          </div>
          
          <!-- Nome e tagline -->
          <h1 class="app-name">AuditPlus</h1>
          <p class="app-tagline">Sistema de Auditoria Automatizada</p>
        </div>
        
        <!-- Footer do lado verde (Powered + Crédito) -->
        <div class="branding-footer">
          <div class="powered-badge">
            <svg class="badge-icon" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
            </svg>
            Powered by Unimed Campo Grande
          </div>
          <div class="developer-credit">
            Desenvolvido por <strong>Pedro Freitas</strong>
          </div>
        </div>
      </aside>
      
      <!-- LADO DIREITO: Login -->
      <main class="login-side">
        <div class="login-wrapper">
          
          <!-- Card de Login -->
          <div class="login-content">
            
            <!-- Step 1: Usuário -->
            @if (step() === 1) {
              <div class="step">
                <h2>Bem-vindo de volta!</h2>
                <p class="subtitle">Por favor, <span class="highlight-text">insira suas credenciais para acessar.</span></p>
                
                @if (error()) {
                  <div class="error-message">
                    <svg class="error-icon" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
                    </svg>
                    {{ error() }}
                  </div>
                }
                
                <div class="form-group">
                  <label for="usuario">Usuário*</label>
                  <input 
                    type="text" 
                    id="usuario"
                    #usernameInput
                    [(ngModel)]="username"
                    placeholder="usuario.exemplo"
                    (keydown.enter)="nextStep()"
                    autocomplete="username"
                  >
                </div>
                
                <button 
                  class="btn-primary"
                  (click)="nextStep()"
                  [disabled]="!username.trim()"
                >
                  Continuar
                  <svg class="arrow-icon" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 4l-1.41 1.41L16.17 11H4v2h12.17l-5.58 5.59L12 20l8-8z"/>
                  </svg>
                </button>
                <div class="signup-link">
                  <a href="#">Não tem uma conta? <strong>Cadastre-se</strong></a>
                </div>
              </div>
            }
            
            <!-- Step 2: Senha -->
            @if (step() === 2) {
              <div class="step">
                <button class="btn-back" (click)="prevStep()">
                  <svg class="back-icon" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/>
                  </svg>
                  Voltar
                </button>
                
                <h2>Bem-vindo de volta!</h2>
                <p class="subtitle">Insira sua senha para continuar.</p>
                
                <div class="user-info">
                  <div class="user-avatar">{{ username.charAt(0).toUpperCase() }}</div>
                  <span class="user-name">{{ username }}</span>
                </div>
                
                @if (error()) {
                  <div class="error-message">
                    <svg class="error-icon" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
                    </svg>
                    {{ error() }}
                  </div>
                }
                
                <div class="form-group">
                  <label for="senha">Senha*</label>
                  <div class="input-wrapper">
                    <input 
                      [type]="showPassword() ? 'text' : 'password'"
                      id="senha"
                      #passwordInput
                      [(ngModel)]="password"
                      placeholder="••••••••"
                      (keydown.enter)="onSubmit()"
                      [disabled]="isLoading()"
                      autocomplete="current-password"
                    >
                    <button class="toggle-password" type="button" (click)="togglePassword()" tabindex="-1">
                      @if (showPassword()) {
                        <svg viewBox="0 0 24 24" fill="currentColor">
                          <path d="M12 7c2.76 0 5 2.24 5 5 0 .65-.13 1.26-.36 1.83l2.92 2.92c1.51-1.26 2.7-2.89 3.43-4.75-1.73-4.39-6-7.5-11-7.5-1.4 0-2.74.25-3.98.7l2.16 2.16C10.74 7.13 11.35 7 12 7zM2 4.27l2.28 2.28.46.46C3.08 8.3 1.78 10.02 1 12c1.73 4.39 6 7.5 11 7.5 1.55 0 3.03-.3 4.38-.84l.42.42L19.73 22 21 20.73 3.27 3 2 4.27zM7.53 9.8l1.55 1.55c-.05.21-.08.43-.08.65 0 1.66 1.34 3 3 3 .22 0 .44-.03.65-.08l1.55 1.55c-.67.33-1.41.53-2.2.53-2.76 0-5-2.24-5-5 0-.79.2-1.53.53-2.2zm4.31-.78l3.15 3.15.02-.16c0-1.66-1.34-3-3-3l-.17.01z"/>
                        </svg>
                      } @else {
                        <svg viewBox="0 0 24 24" fill="currentColor">
                          <path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/>
                        </svg>
                      }
                    </button>
                  </div>
                </div>
                
                <div class="options">
                  <label class="checkbox-container">
                    <input type="checkbox" [(ngModel)]="rememberMe">
                    <span class="checkmark"></span>
                    Manter conectado
                  </label>
                </div>
                
                <button 
                  class="btn-primary btn-login"
                  (click)="onSubmit()"
                  [disabled]="isLoading() || !password"
                >
                  @if (isLoading()) {
                    <span class="spinner"></span>
                    Entrando...
                  } @else {
                    Acessar Sistema
                    <svg class="arrow-icon" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M12 4l-1.41 1.41L16.17 11H4v2h12.17l-5.58 5.59L12 20l8-8z"/>
                    </svg>
                  }
                </button>
                
                <a href="#" class="forgot-password">Esqueci minha senha</a>
              </div>
            }
          </div>
          
          <!-- Footer -->
          <footer class="login-footer">
            <img src="unimed-logo.png" alt="Unimed Campo Grande" class="unimed-logo-footer">
            <span>© 2026 Unimed Campo Grande. Todos os direitos reservados.</span>
          </footer>
        </div>
      </main>
      
    </div>
  `,
  styles: [`
    /* ===== RESET & VARIÁVEIS ===== */
    :host {
      display: block;
      font-family: 'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
      --unimed-green: #00995D;
      --unimed-green-dark: #007A4B;
      --unimed-green-light: #00B36B;
      --unimed-orange: #FF6B00;
    }
    
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }
    
    /* ===== CONTAINER SPLIT ===== */
    .login-container {
      display: flex;
      min-height: 100vh;
    }
    
    /* ===== LADO ESQUERDO: BRANDING ===== */
    .branding-side {
      flex: 1;
      background: linear-gradient(135deg, var(--unimed-green) 0%, var(--unimed-green-dark) 100%);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 40px;
      position: relative;
      overflow: hidden;
    }
    
    /* Decoração de fundo */
    .bg-decoration {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
    }
    
    .circle {
      position: absolute;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.04);
    }
    
    .circle-1 {
      width: 400px;
      height: 400px;
      top: -100px;
      right: -100px;
      animation: float 20s ease-in-out infinite;
    }
    
    .circle-2 {
      width: 300px;
      height: 300px;
      bottom: -50px;
      left: -80px;
      animation: float 15s ease-in-out infinite reverse;
    }
    
    .circle-3 {
      width: 200px;
      height: 200px;
      top: 50%;
      left: 50%;
      animation: float 25s ease-in-out infinite 3s;
    }
    
    @keyframes float {
      0%, 100% { transform: translate(0, 0); }
      50% { transform: translate(-15px, 15px); }
    }
    
    /* Conteúdo do branding */
    .branding-content {
      z-index: 1;
      text-align: center;
      color: white;
    }
    
    .unimed-logo-text {
      margin-bottom: 50px;
      text-align: center;
    }
    
    .unimed-main {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
    }
    
    .unimed-text {
      font-size: 2rem;
      font-weight: 700;
      color: white;
      letter-spacing: 1px;
    }
    
    .unimed-tree {
      width: 35px;
      height: 35px;
    }
    
    .unimed-city {
      display: block;
      font-size: 0.95rem;
      color: rgba(255, 255, 255, 0.9);
      margin-top: 2px;
      font-weight: 500;
      letter-spacing: 0.5px;
    }
    
    /* Logo Vetorial Personalizado (Imagem) */
    .app-icon-3d {
      position: relative;
      margin: 0 auto 30px;
      width: 130px;
      height: 130px;
      filter: drop-shadow(0 15px 30px rgba(0,0,0,0.3));
      transition: transform 0.3s ease;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    
    .app-icon-3d:hover {
      transform: scale(1.05) translateY(-5px);
    }
    
    .app-icon-img {
      width: 100%;
      height: 100%;
      object-fit: contain;
      mix-blend-mode: screen; /* Faz o preto "sumir" no fundo verde */
      border-radius: 20px; /* Bordas suaves para integrar melhor */
    }
    
    .app-name {
      font-size: 2.5rem;
      font-weight: 700;
      margin-bottom: 10px;
      letter-spacing: -0.5px;
    }
    
    .app-tagline {
      font-size: 1.1rem;
      opacity: 0.9;
      font-weight: 400;
    }
    
    /* Footer do branding (Powered + Dev) */
    .branding-footer {
      position: absolute;
      bottom: 25px;
      left: 0;
      right: 0;
      text-align: center;
      z-index: 1;
    }
    
    .powered-badge {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: rgba(255, 255, 255, 0.15);
      padding: 10px 20px;
      border-radius: 30px;
      font-size: 0.9rem;
      backdrop-filter: blur(10px);
      margin-bottom: 10px;
    }
    
    .badge-icon {
      width: 18px;
      height: 18px;
    }
    
    .developer-credit {
      color: rgba(255, 255, 255, 0.5);
      font-size: 0.8rem;
    }
    
    .developer-credit strong {
      color: rgba(255, 255, 255, 0.75);
      font-weight: 600;
    }
    
    /* ===== LADO DIREITO: LOGIN ===== */
    .login-side {
      flex: 1;
      background: #fafbfc;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 40px;
    }
    
    .login-wrapper {
      width: 100%;
      max-width: 420px;
      display: flex;
      flex-direction: column;
      min-height: 100%;
    }
    
    .login-content {
      flex: 1;
      display: flex;
      flex-direction: column;
      justify-content: center;
    }
    
    /* Steps */
    .step {
      animation: slideIn 0.4s ease-out;
    }
    
    @keyframes slideIn {
      from {
        opacity: 0;
        transform: translateX(15px);
      }
      to {
        opacity: 1;
        transform: translateX(0);
      }
    }
    
    .step h2 {
      font-size: 1.8rem;
      font-weight: 700;
      color: #1a1a1a;
      margin-bottom: 8px;
    }
    
    .subtitle {
      color: #666;
      margin-bottom: 30px;
      font-size: 0.95rem;
    }
    
    .subtitle a {
      color: var(--unimed-green);
      text-decoration: none;
      font-weight: 500;
    }
    
    .subtitle a:hover {
      text-decoration: underline;
    }
    
    /* Form */
    .form-group {
      margin-bottom: 20px;
    }

    /* Highlighted text */
    .highlight-text {
      color: var(--unimed-green);
      font-weight: 500;
    }
    
    /* Signup link */
    .signup-link {
      text-align: center;
      margin-top: 15px;
      font-size: 0.9rem;
    }
    
    .signup-link a {
      color: var(--unimed-green);
      text-decoration: none;
    }
    
    .signup-link a:hover {
      text-decoration: underline;
    }
    
    .signup-link strong {
      font-weight: 700;
    }
    
    .form-group label {
      display: block;
      font-size: 0.9rem;
      font-weight: 500;
      color: #333;
      margin-bottom: 8px;
    }
    
    .form-group input,
    .input-wrapper input {
      width: 100%;
      padding: 14px 16px;
      border: 1.5px solid #e0e0e0;
      border-radius: 10px;
      font-size: 1rem;
      font-family: inherit;
      color: #333;
      background: #fff;
      transition: all 0.3s;
    }
    
    .form-group input:focus,
    .input-wrapper input:focus {
      outline: none;
      border-color: var(--unimed-green);
      box-shadow: 0 0 0 4px rgba(0, 153, 93, 0.1);
    }
    
    .form-group input::placeholder,
    .input-wrapper input::placeholder {
      color: #aaa;
    }
    
    .input-wrapper {
      position: relative;
    }
    
    .toggle-password {
      position: absolute;
      right: 12px;
      top: 50%;
      transform: translateY(-50%);
      background: none;
      border: none;
      cursor: pointer;
      padding: 6px;
      border-radius: 6px;
      transition: background 0.2s;
    }
    
    .toggle-password:hover {
      background: rgba(0, 0, 0, 0.05);
    }
    
    .toggle-password svg {
      width: 20px;
      height: 20px;
      color: #666;
    }
    
    /* Buttons */
    .btn-primary {
      width: 100%;
      padding: 14px 20px;
      border: none;
      border-radius: 10px;
      font-size: 1rem;
      font-weight: 600;
      font-family: inherit;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      transition: all 0.3s;
      background: var(--unimed-green);
      color: white;
    }
    
    .btn-primary:hover:not(:disabled) {
      background: var(--unimed-green-dark);
      transform: translateY(-1px);
      box-shadow: 0 4px 15px rgba(0, 153, 93, 0.3);
    }
    
    .btn-primary:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
    
    .arrow-icon {
      width: 18px;
      height: 18px;
      transition: transform 0.3s;
    }
    
    .btn-primary:hover .arrow-icon {
      transform: translateX(3px);
    }
    
    .btn-back {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      background: none;
      border: none;
      color: #666;
      cursor: pointer;
      font-size: 0.9rem;
      font-family: inherit;
      padding: 0;
      margin-bottom: 25px;
      transition: color 0.2s;
    }
    
    .btn-back:hover {
      color: var(--unimed-green);
    }
    
    .back-icon {
      width: 18px;
      height: 18px;
    }
    
    /* User info */
    .user-info {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 25px;
      padding: 14px;
      background: #fff;
      border-radius: 10px;
      border: 1px solid #e8e8e8;
    }
    
    .user-avatar {
      width: 44px;
      height: 44px;
      border-radius: 50%;
      background: linear-gradient(135deg, var(--unimed-green) 0%, var(--unimed-green-light) 100%);
      color: white;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.2rem;
      font-weight: 700;
    }
    
    .user-name {
      color: #333;
      font-weight: 600;
    }
    
    /* Options */
    .options {
      margin-bottom: 25px;
    }
    
    .checkbox-container {
      display: flex;
      align-items: center;
      gap: 10px;
      cursor: pointer;
      color: #555;
      font-size: 0.9rem;
    }
    
    .checkbox-container input {
      width: 18px;
      height: 18px;
      accent-color: var(--unimed-green);
      cursor: pointer;
    }
    
    /* Error */
    .error-message {
      background: #FFF5F5;
      border: 1px solid #FFCDD2;
      color: #D32F2F;
      padding: 12px 14px;
      border-radius: 10px;
      margin-bottom: 20px;
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 0.9rem;
    }
    
    .error-icon {
      width: 20px;
      height: 20px;
      flex-shrink: 0;
    }
    
    /* Forgot password */
    .forgot-password {
      display: block;
      text-align: center;
      color: var(--unimed-green);
      text-decoration: none;
      font-size: 0.9rem;
      margin-top: 20px;
      transition: color 0.2s;
    }
    
    .forgot-password:hover {
      text-decoration: underline;
    }
    
    /* Spinner */
    .spinner {
      width: 18px;
      height: 18px;
      border: 2px solid rgba(255, 255, 255, 0.3);
      border-top-color: #fff;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }
    
    @keyframes spin {
      to { transform: rotate(360deg); }
    }
    
    /* Footer */
    .login-footer {
      text-align: center;
      color: #999;
      font-size: 0.8rem;
      padding-top: 30px;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 12px;
    }
    
    .unimed-logo-footer {
      height: 40px;
      width: auto;
      opacity: 0.9;
    }
    
    /* ===== RESPONSIVO ===== */
    @media (max-width: 900px) {
      .login-container {
        flex-direction: column;
      }
      
      .branding-side {
        padding: 40px 30px;
        min-height: 40vh;
      }
      
      .unimed-logo {
        height: 40px;
        margin-bottom: 30px;
      }
      
      .app-icon {
        width: 70px;
        height: 70px;
        margin-bottom: 20px;
      }
      
      .icon-a {
        font-size: 2.2rem;
      }
      
      .app-name {
        font-size: 2rem;
      }
      
      .app-tagline {
        margin-bottom: 25px;
      }
      
      .login-side {
        padding: 30px 25px;
      }
      
      .developer-credit {
        position: relative;
        bottom: auto;
        margin-top: 25px;
      }
    }
    
    /* Acessibilidade */
    @media (prefers-reduced-motion: reduce) {
      *,
      *::before,
      *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
      }
    }
    
    button:focus-visible,
    input:focus-visible,
    a:focus-visible {
      outline: 3px solid var(--unimed-orange);
      outline-offset: 2px;
    }
  `]
})
export class LoginComponent implements AfterViewInit {
  private authService = inject(AuthService);
  private router = inject(Router);
  private route = inject(ActivatedRoute);
  
  @ViewChild('usernameInput') usernameInput!: ElementRef<HTMLInputElement>;
  @ViewChild('passwordInput') passwordInput!: ElementRef<HTMLInputElement>;
  
  username = '';
  password = '';
  rememberMe = false;
  step = signal(1);
  error = signal<string | null>(null);
  showPassword = signal(false);
  isLoading = this.authService.isLoading;
  
  ngAfterViewInit(): void {
    setTimeout(() => {
      this.usernameInput?.nativeElement?.focus();
    }, 300);
  }
  
  nextStep(): void {
    if (!this.username.trim()) return;
    this.error.set(null);
    this.step.set(2);
    
    setTimeout(() => {
      this.passwordInput?.nativeElement?.focus();
    }, 400);
  }
  
  prevStep(): void {
    this.error.set(null);
    this.step.set(1);
    this.password = '';
    
    setTimeout(() => {
      this.usernameInput?.nativeElement?.focus();
    }, 400);
  }
  
  togglePassword(): void {
    this.showPassword.set(!this.showPassword());
  }
  
  onSubmit(): void {
    if (!this.password) return;
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
