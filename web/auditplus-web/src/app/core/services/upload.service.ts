import { Injectable, inject, signal } from '@angular/core';
import { HttpClient, HttpEventType } from '@angular/common/http';
import { Observable, tap, catchError, of, map } from 'rxjs';
import { environment } from '../../../environments/environment';
import { UploadResult, Lote } from '../models/upload.model';

@Injectable({
  providedIn: 'root'
})
export class UploadService {
  private readonly apiUrl = `${environment.apiUrl}/upload`;
  private http = inject(HttpClient);
  
  private isUploadingSignal = signal<boolean>(false);
  private progressSignal = signal<number>(0);
  
  readonly isUploading = this.isUploadingSignal.asReadonly();
  readonly progress = this.progressSignal.asReadonly();
  
  /**
   * Upload de arquivos XML
   */
  uploadFiles(files: File[]): Observable<UploadResult | null> {
    this.isUploadingSignal.set(true);
    this.progressSignal.set(0);
    
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file, file.name);
    });
    
    return this.http.post<UploadResult>(this.apiUrl, formData, {
      reportProgress: true,
      observe: 'events'
    }).pipe(
      map(event => {
        if (event.type === HttpEventType.UploadProgress && event.total) {
          this.progressSignal.set(Math.round(100 * event.loaded / event.total));
          return null;
        }
        if (event.type === HttpEventType.Response) {
          this.isUploadingSignal.set(false);
          this.progressSignal.set(100);
          return event.body as UploadResult;
        }
        return null;
      }),
      catchError(error => {
        console.error('Erro no upload:', error);
        this.isUploadingSignal.set(false);
        this.progressSignal.set(0);
        return of(null);
      })
    );
  }
  
  /**
   * Listar lotes
   */
  getLotes(): Observable<Lote[]> {
    return this.http.get<Lote[]>(`${this.apiUrl}/lotes`).pipe(
      catchError(() => of([]))
    );
  }
  
  /**
   * Detalhes de um lote
   */
  getLote(id: number): Observable<Lote | null> {
    return this.http.get<Lote>(`${this.apiUrl}/lotes/${id}`).pipe(
      catchError(() => of(null))
    );
  }
}
