import { Component, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { UploadService } from '../../core/services/upload.service';
import { UploadResult, ArquivoInfo } from '../../core/models/upload.model';

@Component({
  selector: 'app-upload',
  standalone: true,
  imports: [],
  template: `
    <div class="upload-page">
      <div class="page-title">
        <h1>Upload de XMLs</h1>
      </div>
      
      <main class="content">
        @if (!resultado()) {
          <!-- Upload Zone -->
          <div 
            class="upload-zone"
            [class.dragging]="isDragging()"
            (dragover)="onDragOver($event)"
            (dragleave)="onDragLeave($event)"
            (drop)="onDrop($event)"
          >
            @if (isUploading()) {
              <div class="upload-progress">
                <div class="spinner"></div>
                <p>Enviando arquivos...</p>
                <div class="progress-bar">
                  <div class="progress" [style.width.%]="progress()"></div>
                </div>
                <span class="percent">{{ progress() }}%</span>
              </div>
            } @else {
              <div class="upload-icon">📁</div>
              <h2>Arraste os XMLs aqui</h2>
              <p>ou clique para selecionar</p>
              <input 
                type="file" 
                multiple 
                accept=".xml"
                (change)="onFileSelected($event)"
                #fileInput
              >
              <button class="btn-select" (click)="fileInput.click()">
                Selecionar Arquivos
              </button>
            }
          </div>
          
          <!-- Selected Files -->
          @if (selectedFiles().length > 0 && !isUploading()) {
            <div class="selected-files">
              <h3>Arquivos Selecionados ({{ selectedFiles().length }})</h3>
              <ul>
                @for (file of selectedFiles(); track file.name) {
                  <li>
                    <span class="file-icon">📄</span>
                    <span class="file-name">{{ file.name }}</span>
                    <span class="file-size">{{ formatSize(file.size) }}</span>
                    <button class="btn-remove" (click)="removeFile(file)">×</button>
                  </li>
                }
              </ul>
              <div class="actions">
                <button class="btn-clear" (click)="clearFiles()">Limpar</button>
                <button class="btn-upload" (click)="upload()">
                  📤 Iniciar Upload
                </button>
              </div>
            </div>
          }
        } @else {
          <!-- Resultado -->
          <div class="resultado">
            <div class="resultado-header">
              <h2>✅ Upload Concluído!</h2>
              <p>Lote: <strong>{{ resultado()!.loteId }}</strong></p>
            </div>
            
            <div class="stats-grid">
              <div class="stat-card success">
                <span class="value">{{ resultado()!.arquivosAceitos }}</span>
                <span class="label">Aceitos</span>
              </div>
              <div class="stat-card error">
                <span class="value">{{ resultado()!.arquivosRejeitados }}</span>
                <span class="label">Rejeitados</span>
              </div>
              <div class="stat-card total">
                <span class="value">{{ resultado()!.totalArquivos }}</span>
                <span class="label">Total</span>
              </div>
            </div>
            
            <div class="arquivos-lista">
              <h3>Arquivos Processados</h3>
              <table>
                <thead>
                  <tr>
                    <th>Arquivo</th>
                    <th>Tamanho</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  @for (arq of resultado()!.arquivos; track arq.nome) {
                    <tr [class]="arq.status.toLowerCase()">
                      <td>{{ arq.nome }}</td>
                      <td>{{ formatSize(arq.tamanho) }}</td>
                      <td>
                        <span class="status-badge" [class]="arq.status.toLowerCase()">
                          {{ arq.status }}
                        </span>
                        @if (arq.motivo) {
                          <small>{{ arq.motivo }}</small>
                        }
                      </td>
                    </tr>
                  }
                </tbody>
              </table>
            </div>
            
            <div class="resultado-actions">
              <button class="btn-new" (click)="novoUpload()">
                📤 Novo Upload
              </button>
              <button class="btn-process" (click)="processarLote()">
                ▶️ Processar Lote
              </button>
            </div>
          </div>
        }
      </main>
    </div>
  `,
  styles: [`
    .upload-page {
      padding: var(--ap-page-padding);
    }

    .page-title h1 {
      font-size: 1.8rem;
      font-weight: 700;
      margin: 0 0 24px;
    }

    .content { max-width: 900px; margin: 0 auto; }
    
    .upload-zone {
      border: 3px dashed rgba(255, 255, 255, 0.2);
      border-radius: 20px;
      padding: 60px;
      text-align: center;
      transition: all 0.3s;
      cursor: pointer;
      position: relative;
    }
    
    .upload-zone:hover,
    .upload-zone.dragging {
      border-color: #00d9ff;
      background: rgba(0, 217, 255, 0.05);
    }
    
    .upload-zone input[type="file"] {
      display: none;
    }
    
    .upload-icon { font-size: 4rem; margin-bottom: 20px; }
    .upload-zone h2 { margin: 0 0 10px; font-weight: 500; }
    .upload-zone p { color: rgba(255, 255, 255, 0.5); margin: 0 0 20px; }
    
    .btn-select {
      padding: 12px 30px;
      border-radius: 10px;
      border: none;
      background: linear-gradient(135deg, #00d9ff 0%, #00a8cc 100%);
      color: #fff;
      font-weight: 600;
      cursor: pointer;
      font-size: 1rem;
    }
    
    .upload-progress {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 15px;
    }
    
    .spinner {
      width: 50px;
      height: 50px;
      border: 4px solid rgba(255, 255, 255, 0.2);
      border-top-color: #00d9ff;
      border-radius: 50%;
      animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
      to { transform: rotate(360deg); }
    }
    
    .progress-bar {
      width: 100%;
      max-width: 300px;
      height: 8px;
      background: rgba(255, 255, 255, 0.1);
      border-radius: 10px;
      overflow: hidden;
    }
    
    .progress {
      height: 100%;
      background: linear-gradient(90deg, #00d9ff, #00e676);
      transition: width 0.3s;
    }
    
    .selected-files {
      margin-top: 30px;
      background: rgba(255, 255, 255, 0.05);
      border-radius: 15px;
      padding: 25px;
    }
    
    .selected-files h3 { margin: 0 0 20px; }
    
    .selected-files ul {
      list-style: none;
      padding: 0;
      margin: 0;
    }
    
    .selected-files li {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 10px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .file-icon { font-size: 1.2rem; }
    .file-name { flex: 1; }
    .file-size { color: rgba(255, 255, 255, 0.5); font-size: 0.9rem; }
    
    .btn-remove {
      background: rgba(255, 82, 82, 0.2);
      color: #ff5252;
      border: none;
      width: 24px;
      height: 24px;
      border-radius: 50%;
      cursor: pointer;
    }
    
    .actions {
      display: flex;
      gap: 15px;
      justify-content: flex-end;
      margin-top: 20px;
    }
    
    .btn-clear {
      padding: 12px 24px;
      border-radius: 10px;
      border: 1px solid rgba(255, 255, 255, 0.2);
      background: transparent;
      color: #fff;
      cursor: pointer;
    }
    
    .btn-upload {
      padding: 12px 30px;
      border-radius: 10px;
      border: none;
      background: linear-gradient(135deg, #00e676 0%, #00c853 100%);
      color: #fff;
      font-weight: 600;
      cursor: pointer;
    }
    
    /* Resultado */
    .resultado { animation: fadeIn 0.5s; }
    
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(20px); }
      to { opacity: 1; transform: translateY(0); }
    }
    
    .resultado-header {
      text-align: center;
      margin-bottom: 30px;
    }
    
    .resultado-header h2 { color: #00e676; margin-bottom: 10px; }
    
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 20px;
      margin-bottom: 30px;
    }
    
    .stat-card {
      background: rgba(255, 255, 255, 0.05);
      border-radius: 15px;
      padding: 25px;
      text-align: center;
    }
    
    .stat-card .value {
      display: block;
      font-size: 2.5rem;
      font-weight: 700;
    }
    
    .stat-card.success .value { color: #00e676; }
    .stat-card.error .value { color: #ff5252; }
    .stat-card.total .value { color: #00d9ff; }
    
    .stat-card .label {
      color: rgba(255, 255, 255, 0.6);
    }
    
    .arquivos-lista {
      background: rgba(255, 255, 255, 0.03);
      border-radius: 15px;
      padding: 25px;
      margin-bottom: 20px;
    }
    
    .arquivos-lista h3 { margin: 0 0 20px; }
    
    .arquivos-lista table {
      width: 100%;
      border-collapse: collapse;
    }
    
    .arquivos-lista th,
    .arquivos-lista td {
      padding: 12px;
      text-align: left;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .status-badge {
      padding: 4px 10px;
      border-radius: 20px;
      font-size: 0.8rem;
    }
    
    .status-badge.aceito { background: rgba(0, 230, 118, 0.2); color: #00e676; }
    .status-badge.rejeitado { background: rgba(255, 82, 82, 0.2); color: #ff5252; }
    .status-badge.erro { background: rgba(255, 152, 0, 0.2); color: #ff9800; }
    
    .resultado-actions {
      display: flex;
      gap: 15px;
      justify-content: center;
    }
    
    .btn-new {
      padding: 15px 30px;
      border-radius: 10px;
      border: 1px solid rgba(255, 255, 255, 0.2);
      background: transparent;
      color: #fff;
      cursor: pointer;
      font-size: 1rem;
    }
    
    .btn-process {
      padding: 15px 40px;
      border-radius: 10px;
      border: none;
      background: linear-gradient(135deg, #00d9ff 0%, #00a8cc 100%);
      color: #fff;
      font-weight: 600;
      cursor: pointer;
      font-size: 1rem;
    }
  `]
})
export class UploadComponent {
  private uploadService = inject(UploadService);
  private router = inject(Router);
  
  isUploading = this.uploadService.isUploading;
  progress = this.uploadService.progress;
  
  isDragging = signal(false);
  selectedFiles = signal<File[]>([]);
  resultado = signal<UploadResult | null>(null);
  
  onDragOver(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging.set(true);
  }
  
  onDragLeave(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging.set(false);
  }
  
  onDrop(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging.set(false);
    
    const files = event.dataTransfer?.files;
    if (files) {
      this.addFiles(Array.from(files));
    }
  }
  
  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files) {
      this.addFiles(Array.from(input.files));
    }
  }
  
  addFiles(files: File[]): void {
    const xmlFiles = files.filter(f => f.name.endsWith('.xml'));
    const current = this.selectedFiles();
    this.selectedFiles.set([...current, ...xmlFiles]);
  }
  
  removeFile(file: File): void {
    this.selectedFiles.update(files => files.filter(f => f !== file));
  }
  
  clearFiles(): void {
    this.selectedFiles.set([]);
  }
  
  upload(): void {
    const files = this.selectedFiles();
    if (files.length === 0) return;
    
    this.uploadService.uploadFiles(files).subscribe(result => {
      if (result) {
        this.resultado.set(result);
        this.selectedFiles.set([]);
      }
    });
  }
  
  novoUpload(): void {
    this.resultado.set(null);
  }
  
  processarLote(): void {
    const result = this.resultado();
    if (!result) return;
    
    this.router.navigate(['/validation'], {
      queryParams: { execucaoId: result.execucaoId }
    });
  }
  
  formatSize(bytes: number): string {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  }
}
