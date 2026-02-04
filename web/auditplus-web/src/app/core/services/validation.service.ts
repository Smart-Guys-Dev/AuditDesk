import { Injectable, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, catchError, of, tap } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface ValidationResult {
  execucaoId: number;
  sucesso: boolean;
  mensagem: string;
  totalArquivos: number;
  arquivosModificados: number;
  totalCorrecoes: number;
  erros: string[];
}

export interface PreviewResult {
  execucaoId: number;
  totalArquivos: number;
  totalCorrecoes: number;
  arquivos: ArquivoPreview[];
}

export interface ArquivoPreview {
  id: number;
  nome: string;
  status: string;
  regrasAplicadas: number;
  correcoes: CorrecaoPreview[];
}

export interface CorrecaoPreview {
  regra: string;
  elemento: string;
  antes: string;
  depois: string;
  acao: string;
}

export interface ValidationStats {
  totalRegras: number;
  regrasAtivas: number;
  totalCorrecoes: number;
  arquivosProcessados: number;
  topRegras: { codigo: string; totalAplicacoes: number }[];
}

export interface ValidationRule {
  id: number;
  codigo: string;
  descricao: string;
  grupo: string;
  categoria: string;
  impacto: string;
  prioridade: number;
  totalAplicacoes: number;
  ativo: boolean;
}

export interface UploadResult {
  sucesso: boolean;
  totalArquivos: number;
  arquivos: string[];
  erros: string[];
  pastaUpload: string;
}

@Injectable({
  providedIn: 'root'
})
export class ValidationService {
  private readonly apiUrl = `${environment.apiUrl}/validation`;
  private http = inject(HttpClient);
  
  private isProcessingSignal = signal<boolean>(false);
  readonly isProcessing = this.isProcessingSignal.asReadonly();
  
  private isUploadingSignal = signal<boolean>(false);
  readonly isUploading = this.isUploadingSignal.asReadonly();
  
  private uploadedFilesSignal = signal<string[]>([]);
  readonly uploadedFiles = this.uploadedFilesSignal.asReadonly();
  
  /**
   * Faz upload de arquivos ZIP/XML
   */
  uploadArquivos(arquivos: File[]): Observable<UploadResult | null> {
    this.isUploadingSignal.set(true);
    
    const formData = new FormData();
    arquivos.forEach(arquivo => {
      formData.append('arquivos', arquivo, arquivo.name);
    });
    
    return this.http.post<UploadResult>(`${this.apiUrl}/upload`, formData).pipe(
      tap(result => {
        this.isUploadingSignal.set(false);
        if (result?.arquivos) {
          this.uploadedFilesSignal.set(result.arquivos);
        }
      }),
      catchError(error => {
        console.error('Erro no upload:', error);
        this.isUploadingSignal.set(false);
        return of(null);
      })
    );
  }
  
  /**
   * Processa um lote de arquivos
   */
  processarLote(execucaoId: number): Observable<ValidationResult | null> {
    this.isProcessingSignal.set(true);
    
    return this.http.post<ValidationResult>(`${this.apiUrl}/processar/${execucaoId}`, {}).pipe(
      tap(() => this.isProcessingSignal.set(false)),
      catchError(error => {
        console.error('Erro ao processar:', error);
        this.isProcessingSignal.set(false);
        return of(null);
      })
    );
  }
  
  /**
   * Preview das correções
   */
  getPreview(execucaoId: number): Observable<PreviewResult | null> {
    return this.http.get<PreviewResult>(`${this.apiUrl}/preview/${execucaoId}`).pipe(
      catchError(() => of(null))
    );
  }
  
  /**
   * Lista regras de validação
   */
  getRegras(): Observable<ValidationRule[]> {
    return this.http.get<ValidationRule[]>(`${this.apiUrl}/regras`).pipe(
      catchError(() => of([]))
    );
  }
  
  /**
   * Estatísticas de validação
   */
  getStats(): Observable<ValidationStats | null> {
    return this.http.get<ValidationStats>(`${this.apiUrl}/stats`).pipe(
      catchError(() => of(null))
    );
  }
  
  /**
   * Aplica as correções definitivamente (com backup)
   */
  aplicarCorrecoes(execucaoId: number): Observable<AplicarResult | null> {
    this.isProcessingSignal.set(true);
    
    return this.http.post<AplicarResult>(`${this.apiUrl}/aplicar/${execucaoId}`, {}).pipe(
      tap(() => this.isProcessingSignal.set(false)),
      catchError(error => {
        console.error('Erro ao aplicar correções:', error);
        this.isProcessingSignal.set(false);
        return of(null);
      })
    );
  }
  
  /**
   * Exporta XMLs corrigidos como ZIP
   */
  exportarZip(execucaoId: number): void {
    const url = `${this.apiUrl}/export/${execucaoId}`;
    window.open(url, '_blank');
  }
  
  /**
   * Recalcula o hash MD5 dos XMLs corrigidos (lógica PTU)
   */
  recalcularHash(execucaoId: number): Observable<HashResult | null> {
    this.isProcessingSignal.set(true);
    
    return this.http.post<HashResult>(`${this.apiUrl}/hash/${execucaoId}`, {}).pipe(
      tap(() => this.isProcessingSignal.set(false)),
      catchError(error => {
        console.error('Erro ao recalcular hash:', error);
        this.isProcessingSignal.set(false);
        return of(null);
      })
    );
  }
  
  /**
   * Exporta XMLs corrigidos em formato PTU (cada XML em ZIP separado)
   */
  exportarZipPtu(execucaoId: number): void {
    const url = `${this.apiUrl}/export-ptu/${execucaoId}`;
    window.open(url, '_blank');
  }
}

export interface AplicarResult {
  execucaoId: number;
  arquivosAplicados: number;
  totalArquivos: number;
  pastaBackup: string;
  pastaCorrigidos: string;
  erros: string[];
  sucesso: boolean;
}

export interface HashResult {
  execucaoId: number;
  arquivosProcessados: number;
  totalArquivos: number;
  hashes: HashInfo[];
  erros: string[];
  sucesso: boolean;
}

export interface HashInfo {
  arquivo: string;
  hash: string;
}

