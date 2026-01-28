import { Injectable, inject, signal, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, tap, catchError, of } from 'rxjs';
import { environment } from '../../../environments/environment';
import { User, LoginRequest, LoginResponse, RegisterRequest } from '../models/user.model';

const TOKEN_KEY = 'auditplus_token';
const USER_KEY = 'auditplus_user';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly apiUrl = `${environment.apiUrl}/auth`;
  
  // Signals para estado reativo
  private currentUserSignal = signal<User | null>(this.loadUserFromStorage());
  private isLoadingSignal = signal<boolean>(false);
  
  // Computed values
  readonly currentUser = this.currentUserSignal.asReadonly();
  readonly isAuthenticated = computed(() => !!this.currentUserSignal());
  readonly isAdmin = computed(() => this.currentUserSignal()?.role === 'ADMIN');
  readonly isLoading = this.isLoadingSignal.asReadonly();
  
  private http = inject(HttpClient);
  private router = inject(Router);
  
  constructor() {
    // Verificar token expirado ao iniciar
    this.checkTokenExpiration();
  }
  
  /**
   * Realiza login do usuário
   */
  login(credentials: LoginRequest): Observable<LoginResponse | null> {
    this.isLoadingSignal.set(true);
    
    return this.http.post<LoginResponse>(`${this.apiUrl}/login`, credentials).pipe(
      tap(response => {
        this.saveToken(response.token);
        this.saveUser({
          id: 0, // API não retorna ID no login, será obtido via /me
          username: response.username,
          fullName: response.fullName,
          role: response.role
        });
        this.isLoadingSignal.set(false);
      }),
      catchError(error => {
        console.error('Erro no login:', error);
        this.isLoadingSignal.set(false);
        return of(null);
      })
    );
  }
  
  /**
   * Registra novo usuário (apenas admin)
   */
  register(data: RegisterRequest): Observable<User | null> {
    return this.http.post<User>(`${this.apiUrl}/register`, data).pipe(
      catchError(error => {
        console.error('Erro no registro:', error);
        return of(null);
      })
    );
  }
  
  /**
   * Obtém dados completos do usuário autenticado
   */
  getCurrentUser(): Observable<User | null> {
    return this.http.get<User>(`${this.apiUrl}/me`).pipe(
      tap(user => {
        this.saveUser(user);
      }),
      catchError(error => {
        console.error('Erro ao obter usuário:', error);
        return of(null);
      })
    );
  }
  
  /**
   * Realiza logout
   */
  logout(): void {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    this.currentUserSignal.set(null);
    this.router.navigate(['/login']);
  }
  
  /**
   * Retorna o token JWT armazenado
   */
  getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY);
  }
  
  /**
   * Salva o token no localStorage
   */
  private saveToken(token: string): void {
    localStorage.setItem(TOKEN_KEY, token);
  }
  
  /**
   * Salva dados do usuário no localStorage e signal
   */
  private saveUser(user: User): void {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
    this.currentUserSignal.set(user);
  }
  
  /**
   * Carrega usuário do localStorage
   */
  private loadUserFromStorage(): User | null {
    const userJson = localStorage.getItem(USER_KEY);
    if (userJson) {
      try {
        return JSON.parse(userJson);
      } catch {
        return null;
      }
    }
    return null;
  }
  
  /**
   * Verifica se o token expirou
   */
  private checkTokenExpiration(): void {
    const token = this.getToken();
    if (!token) return;
    
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const exp = payload.exp * 1000; // converter para ms
      
      if (Date.now() >= exp) {
        console.log('Token expirado, fazendo logout');
        this.logout();
      }
    } catch {
      this.logout();
    }
  }
}
