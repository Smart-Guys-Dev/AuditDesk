import { Injectable, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap, catchError, of, map } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Regra, RegraCreate, RuleCategory, RuleGroup } from '../models/regra.model';

@Injectable({
  providedIn: 'root'
})
export class RegrasService {
  private readonly apiUrl = `${environment.apiUrl}/regras`;
  private http = inject(HttpClient);
  
  // Signal para estado reativo das regras
  private regrasSignal = signal<Regra[]>([]);
  private isLoadingSignal = signal<boolean>(false);
  
  readonly regras = this.regrasSignal.asReadonly();
  readonly isLoading = this.isLoadingSignal.asReadonly();
  
  /**
   * Carrega todas as regras
   */
  loadAll(): Observable<Regra[]> {
    this.isLoadingSignal.set(true);
    return this.http.get<Regra[]>(this.apiUrl).pipe(
      tap(regras => {
        this.regrasSignal.set(regras);
        this.isLoadingSignal.set(false);
      }),
      catchError(error => {
        console.error('Erro ao carregar regras:', error);
        this.isLoadingSignal.set(false);
        return of([]);
      })
    );
  }
  
  /**
   * Carrega apenas regras ativas
   */
  loadAtivas(): Observable<Regra[]> {
    return this.http.get<Regra[]>(`${this.apiUrl}/ativas`);
  }
  
  /**
   * Busca regra por ID
   */
  getById(id: number): Observable<Regra | null> {
    return this.http.get<Regra>(`${this.apiUrl}/${id}`).pipe(
      catchError(() => of(null))
    );
  }
  
  /**
   * Busca regra por código
   */
  getByCodigo(codigo: string): Observable<Regra | null> {
    return this.http.get<Regra>(`${this.apiUrl}/codigo/${codigo}`).pipe(
      catchError(() => of(null))
    );
  }
  
  /**
   * Busca regras por categoria
   */
  getByCategoria(categoria: RuleCategory): Observable<Regra[]> {
    return this.http.get<Regra[]>(`${this.apiUrl}/categoria/${categoria}`);
  }
  
  /**
   * Busca regras por grupo
   */
  getByGrupo(grupo: RuleGroup): Observable<Regra[]> {
    return this.http.get<Regra[]>(`${this.apiUrl}/grupo/${grupo}`);
  }
  
  /**
   * Cria nova regra
   */
  create(regra: RegraCreate): Observable<Regra | null> {
    return this.http.post<Regra>(this.apiUrl, regra).pipe(
      tap(created => {
        this.regrasSignal.update(list => [...list, created]);
      }),
      catchError(error => {
        console.error('Erro ao criar regra:', error);
        return of(null);
      })
    );
  }
  
  /**
   * Atualiza regra existente
   */
  update(id: number, regra: Regra): Observable<boolean> {
    return this.http.put(`${this.apiUrl}/${id}`, regra).pipe(
      map(() => {
        this.regrasSignal.update(list => 
          list.map(r => r.id === id ? regra : r)
        );
        return true;
      }),
      catchError(error => {
        console.error('Erro ao atualizar regra:', error);
        return of(false);
      })
    );
  }
  
  /**
   * Remove regra
   */
  delete(id: number): Observable<boolean> {
    return this.http.delete(`${this.apiUrl}/${id}`).pipe(
      map(() => {
        this.regrasSignal.update(list => list.filter(r => r.id !== id));
        return true;
      }),
      catchError(error => {
        console.error('Erro ao excluir regra:', error);
        return of(false);
      })
    );
  }
  
  /**
   * Alterna status ativo/inativo
   */
  toggle(id: number): Observable<{ativo: boolean} | null> {
    return this.http.patch<{ativo: boolean}>(`${this.apiUrl}/${id}/toggle`, {}).pipe(
      tap(result => {
        if (result) {
          this.regrasSignal.update(list =>
            list.map(r => r.id === id ? {...r, ativo: result.ativo} : r)
          );
        }
      }),
      catchError(error => {
        console.error('Erro ao alternar regra:', error);
        return of(null);
      })
    );
  }
}
