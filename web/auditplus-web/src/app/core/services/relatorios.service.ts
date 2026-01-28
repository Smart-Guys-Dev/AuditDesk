import { Injectable, inject, signal } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, catchError, of, tap } from 'rxjs';
import { environment } from '../../../environments/environment';
import { 
  RelatorioGlosasEvitadas, 
  RegraEfetividade, 
  ResumoMensal,
  FiltroRelatorio 
} from '../models/relatorio.model';

@Injectable({
  providedIn: 'root'
})
export class RelatoriosService {
  private readonly apiUrl = `${environment.apiUrl}/relatorios`;
  private http = inject(HttpClient);
  
  private isLoadingSignal = signal<boolean>(false);
  readonly isLoading = this.isLoadingSignal.asReadonly();
  
  /**
   * Relatório de glosas evitadas
   */
  getGlosasEvitadas(filtro?: FiltroRelatorio): Observable<RelatorioGlosasEvitadas | null> {
    this.isLoadingSignal.set(true);
    
    let params = new HttpParams();
    if (filtro?.dataInicio) {
      params = params.set('dataInicio', filtro.dataInicio.toISOString());
    }
    if (filtro?.dataFim) {
      params = params.set('dataFim', filtro.dataFim.toISOString());
    }
    
    return this.http.get<RelatorioGlosasEvitadas>(`${this.apiUrl}/glosas-evitadas`, { params }).pipe(
      tap(() => this.isLoadingSignal.set(false)),
      catchError(error => {
        console.error('Erro ao carregar relatório:', error);
        this.isLoadingSignal.set(false);
        return of(null);
      })
    );
  }
  
  /**
   * Relatório de efetividade das regras
   */
  getRegrasEfetividade(): Observable<RegraEfetividade[]> {
    this.isLoadingSignal.set(true);
    
    return this.http.get<RegraEfetividade[]>(`${this.apiUrl}/regras-efetividade`).pipe(
      tap(() => this.isLoadingSignal.set(false)),
      catchError(error => {
        console.error('Erro ao carregar efetividade:', error);
        this.isLoadingSignal.set(false);
        return of([]);
      })
    );
  }
  
  /**
   * Resumo mensal
   */
  getResumoMensal(ano?: number): Observable<ResumoMensal[]> {
    this.isLoadingSignal.set(true);
    
    let params = new HttpParams();
    if (ano) {
      params = params.set('ano', ano.toString());
    }
    
    return this.http.get<ResumoMensal[]>(`${this.apiUrl}/resumo-mensal`, { params }).pipe(
      tap(() => this.isLoadingSignal.set(false)),
      catchError(error => {
        console.error('Erro ao carregar resumo:', error);
        this.isLoadingSignal.set(false);
        return of([]);
      })
    );
  }
}
