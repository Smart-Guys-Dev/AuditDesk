import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, catchError, of } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface DashboardStats {
  totalRegras: number;
  regrasAtivas: number;
  totalExecucoes: number;
  totalFaturas: number;
  execucoesSucesso: number;
  execucoesErro: number;
  totalArquivosProcessados: number;
  taxaSucesso: number;
  ultimaExecucao?: Date;
}

export interface RegrasPorCategoria {
  categoria: string;
  quantidade: number;
}

@Injectable({
  providedIn: 'root'
})
export class DashboardService {
  private readonly apiUrl = `${environment.apiUrl}/dashboard`;
  private http = inject(HttpClient);
  
  /**
   * Obtém estatísticas gerais
   */
  getStats(): Observable<DashboardStats> {
    return this.http.get<DashboardStats>(`${this.apiUrl}/stats`).pipe(
      catchError(error => {
        console.error('Erro ao carregar stats:', error);
        return of({
          totalRegras: 0,
          regrasAtivas: 0,
          totalExecucoes: 0,
          totalFaturas: 0,
          execucoesSucesso: 0,
          execucoesErro: 0,
          totalArquivosProcessados: 0,
          taxaSucesso: 0
        });
      })
    );
  }
  
  /**
   * Obtém regras agrupadas por categoria
   */
  getRegrasPorCategoria(): Observable<RegrasPorCategoria[]> {
    return this.http.get<RegrasPorCategoria[]>(`${this.apiUrl}/regras-por-categoria`).pipe(
      catchError(() => of([]))
    );
  }
}
