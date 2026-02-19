import { Injectable, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap, catchError, of, map } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface UserResponse {
  id: number;
  username: string;
  fullName: string;
  email: string;
  role: string;
  lastLoginAt: string | null;
}

export interface CreateUserRequest {
  username: string;
  password: string;
  fullName: string;
  email: string;
  role: string;
}

export interface UpdateUserRequest {
  fullName: string;
  email: string;
  role: string;
}

@Injectable({
  providedIn: 'root'
})
export class UsersService {
  private readonly apiUrl = `${environment.apiUrl}/users`;
  private http = inject(HttpClient);

  private usersSignal = signal<UserResponse[]>([]);
  private isLoadingSignal = signal<boolean>(false);

  readonly users = this.usersSignal.asReadonly();
  readonly isLoading = this.isLoadingSignal.asReadonly();

  loadAll(): Observable<UserResponse[]> {
    this.isLoadingSignal.set(true);
    return this.http.get<UserResponse[]>(this.apiUrl).pipe(
      tap(users => {
        this.usersSignal.set(users);
        this.isLoadingSignal.set(false);
      }),
      catchError(error => {
        console.error('Erro ao carregar usuários:', error);
        this.isLoadingSignal.set(false);
        return of([]);
      })
    );
  }

  create(request: CreateUserRequest): Observable<UserResponse | null> {
    return this.http.post<UserResponse>(this.apiUrl, request).pipe(
      tap(user => {
        this.usersSignal.update(list => [...list, user]);
      }),
      catchError(error => {
        console.error('Erro ao criar usuário:', error);
        throw error;
      })
    );
  }

  update(id: number, request: UpdateUserRequest): Observable<boolean> {
    return this.http.put(`${this.apiUrl}/${id}`, request).pipe(
      map(() => {
        this.usersSignal.update(list =>
          list.map(u => u.id === id ? { ...u, ...request } : u)
        );
        return true;
      }),
      catchError(error => {
        console.error('Erro ao atualizar usuário:', error);
        throw error;
      })
    );
  }

  toggle(id: number): Observable<{ isActive: boolean } | null> {
    return this.http.patch<{ isActive: boolean }>(`${this.apiUrl}/${id}/toggle`, {}).pipe(
      catchError(error => {
        console.error('Erro ao alternar usuário:', error);
        throw error;
      })
    );
  }

  unlock(id: number): Observable<{ message: string } | null> {
    return this.http.patch<{ message: string }>(`${this.apiUrl}/${id}/unlock`, {}).pipe(
      catchError(error => {
        console.error('Erro ao desbloquear usuário:', error);
        throw error;
      })
    );
  }
}
