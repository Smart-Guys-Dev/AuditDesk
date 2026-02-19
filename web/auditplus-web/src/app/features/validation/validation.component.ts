import { Component, inject, OnInit, signal } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { ValidationService, ValidationResult, PreviewResult, ValidationStats, AplicarResult, HashResult } from '../../core/services/validation.service';

@Component({
  selector: 'app-validation',
  standalone: true,
  imports: [],
  template: `
    <div class="validation-page">
      <div class="page-title">
        <h1>Validação de XMLs</h1>
      </div>
      
      <main class="content">
        <!-- Stats Cards -->
        @if (stats()) {
          <div class="stats-grid">
            <div class="stat-card">
              <span class="stat-icon">📋</span>
              <div>
                <span class="stat-value">{{ stats()!.regrasAtivas }}</span>
                <span class="stat-label">Regras Ativas</span>
              </div>
            </div>
            <div class="stat-card">
              <span class="stat-icon">📁</span>
              <div>
                <span class="stat-value">{{ stats()!.arquivosProcessados }}</span>
                <span class="stat-label">Arquivos Processados</span>
              </div>
            </div>
            <div class="stat-card">
              <span class="stat-icon">✅</span>
              <div>
                <span class="stat-value">{{ stats()!.totalCorrecoes }}</span>
                <span class="stat-label">Correções Aplicadas</span>
              </div>
            </div>
          </div>
        }
        
        <!-- Action Panel -->
        <div class="action-panel">
          <h2>Processar Lote</h2>
          
          @if (!resultado()) {
            <div class="action-content">
              <!-- Drag & Drop Zone -->
              <div 
                class="drop-zone"
                [class.drag-over]="isDragOver()"
                (dragover)="onDragOver($event)"
                (dragleave)="onDragLeave($event)"
                (drop)="onDrop($event)"
                (click)="fileInput.click()"
              >
                <input 
                  type="file" 
                  #fileInput
                  multiple
                  accept=".zip,.051,.xml"
                  (change)="onFileSelected($event)"
                  style="display: none"
                >
                @if (isUploading()) {
                  <span class="spinner"></span>
                  <p>Enviando arquivos...</p>
                } @else if (uploadedFiles().length > 0) {
                  <span class="upload-icon">✅</span>
                  <p>{{ uploadedFiles().length }} arquivo(s) carregado(s)</p>
                  <ul class="file-list">
                    @for (arquivo of uploadedFiles(); track arquivo) {
                      <li>📦 {{ arquivo }}</li>
                    }
                  </ul>
                } @else {
                  <span class="upload-icon">📂</span>
                  <p>Arraste arquivos <strong>.zip</strong>, <strong>.051</strong> ou <strong>.xml</strong> aqui</p>
                  <span class="hint">ou clique para selecionar</span>
                }
              </div>
              
              <!-- ID e Processar -->
              <div class="input-group">
                <input 
                  type="number" 
                  placeholder="ID da Execução"
                  [value]="execucaoId()"
                  (input)="setExecucaoId($event)"
                  #execIdInput
                >
                <button 
                  class="btn-process"
                  [disabled]="isProcessing() || uploadedFiles().length === 0"
                  (click)="processar()"
                >
                  @if (isProcessing()) {
                    <span class="spinner-sm"></span> Processando...
                  } @else {
                    ▶️ Processar XMLs
                  }
                </button>
              </div>
            </div>
          } @else {
            <!-- Resultado -->
            <div class="resultado" [class.success]="resultado()!.sucesso" [class.error]="!resultado()!.sucesso">
              <h3>
                @if (resultado()!.sucesso) {
                  ✅ Processamento Concluído!
                } @else {
                  ❌ Erro no Processamento
                }
              </h3>
              <p>{{ resultado()!.mensagem }}</p>
              
              <div class="resultado-stats">
                <div class="resultado-stat">
                  <span class="value">{{ resultado()!.totalArquivos }}</span>
                  <span class="label">Total</span>
                </div>
                <div class="resultado-stat success">
                  <span class="value">{{ resultado()!.arquivosModificados }}</span>
                  <span class="label">Modificados</span>
                </div>
                <div class="resultado-stat">
                  <span class="value">{{ resultado()!.totalCorrecoes }}</span>
                  <span class="label">Correções</span>
                </div>
              </div>
              
              @if (resultado()!.erros.length > 0) {
                <div class="erros">
                  <h4>Erros:</h4>
                  <ul>
                    @for (erro of resultado()!.erros; track erro) {
                      <li>{{ erro }}</li>
                    }
                  </ul>
                </div>
              }
              
              <div class="resultado-actions">
                <button class="btn-secondary" (click)="novoProcessamento()">
                  🔄 Novo Processamento
                </button>
                <button class="btn-primary" (click)="verPreview()">
                  👁️ Ver Detalhes
                </button>
              </div>
            </div>
          }
        </div>
        
        <!-- Preview Section -->
        @if (preview()) {
          <div class="preview-section">
            <h2>Detalhes das Correções</h2>
            
            @for (arquivo of preview()!.arquivos; track arquivo.id) {
              <div class="arquivo-card">
                <div class="arquivo-header">
                  <span class="arquivo-nome">📄 {{ arquivo.nome }}</span>
                  <span class="arquivo-status" [class]="arquivo.status.toLowerCase()">
                    {{ arquivo.status }}
                  </span>
                  <span class="arquivo-count">{{ arquivo.regrasAplicadas }} regra(s)</span>
                </div>
                
                @if (arquivo.correcoes.length > 0) {
                  <table class="correcoes-table">
                    <thead>
                      <tr>
                        <th>Regra</th>
                        <th>Elemento</th>
                        <th>Antes</th>
                        <th>Depois</th>
                      </tr>
                    </thead>
                    <tbody>
                      @for (corr of arquivo.correcoes; track corr.regra) {
                        <tr>
                          <td><code>{{ corr.regra }}</code></td>
                          <td><code>{{ corr.elemento }}</code></td>
                          <td class="antes">{{ corr.antes || '-' }}</td>
                          <td class="depois">{{ corr.depois || '-' }}</td>
                        </tr>
                      }
                    </tbody>
                  </table>
                }
              </div>
            }
            
            <!-- Action Buttons -->
            <div class="preview-actions">
              <button 
                class="btn-apply"
                [disabled]="isApplying()"
                (click)="confirmarAplicacao()"
              >
                @if (isApplying()) {
                  <span class="spinner-sm"></span> Aplicando...
                } @else {
                  ✅ Aplicar Correções
                }
              </button>
              <button 
                class="btn-export"
                [disabled]="!aplicacaoResultado()"
                (click)="exportarZip()"
              >
                📦 Exportar ZIP
              </button>
              <button 
                class="btn-hash"
                [disabled]="!aplicacaoResultado() || isCalculatingHash()"
                (click)="recalcularHash()"
              >
                @if (isCalculatingHash()) {
                  <span class="spinner-sm"></span> Calculando...
                } @else {
                  🔐 Recalcular Hash
                }
              </button>
              <button 
                class="btn-ptu"
                [disabled]="!hashResultado()"
                (click)="exportarZipPtu()"
              >
                📤 Exportar PTU
              </button>
            </div>
            
            <!-- Aplicação Resultado -->
            @if (aplicacaoResultado()) {
              <div class="aplicacao-resultado" [class.success]="aplicacaoResultado()!.sucesso">
                <h3>
                  @if (aplicacaoResultado()!.sucesso) {
                    ✅ Correções Aplicadas com Sucesso!
                  } @else {
                    ⚠️ Correções Aplicadas com Erros
                  }
                </h3>
                <div class="aplicacao-stats">
                  <div class="aplicacao-stat">
                    <span class="value">{{ aplicacaoResultado()!.arquivosAplicados }}</span>
                    <span class="label">Arquivos Corrigidos</span>
                  </div>
                  <div class="aplicacao-stat">
                    <span class="value">{{ aplicacaoResultado()!.totalArquivos }}</span>
                    <span class="label">Total</span>
                  </div>
                </div>
              </div>
            }
            
            <!-- Hash Resultado -->
            @if (hashResultado()) {
              <div class="hash-resultado" [class.success]="hashResultado()!.sucesso">
                <h3>🔐 Hash Atualizado</h3>
                <div class="hash-list">
                  @for (h of hashResultado()!.hashes; track h.arquivo) {
                    <div class="hash-item">
                      <span class="hash-arquivo">📄 {{ h.arquivo }}</span>
                      <code class="hash-value">{{ h.hash }}</code>
                    </div>
                  }
                </div>
              </div>
            }
          </div>
        }
        
        <!-- Confirmation Modal -->
        @if (showConfirmModal()) {
          <div class="modal-overlay" (click)="cancelarAplicacao()">
            <div class="modal-content" (click)="$event.stopPropagation()">
              <h3>⚠️ Confirmar Aplicação</h3>
              <p>Você está prestes a aplicar <strong>{{ preview()!.totalCorrecoes }}</strong> correções em <strong>{{ preview()!.totalArquivos }}</strong> arquivos.</p>
              <p class="modal-warning">Um backup será criado automaticamente.</p>
              <div class="modal-actions">
                <button class="btn-secondary" (click)="cancelarAplicacao()">Cancelar</button>
                <button class="btn-confirm" (click)="aplicar()">Confirmar e Aplicar</button>
              </div>
            </div>
          </div>
        }
        
        <!-- Top Regras -->
        @if (stats()?.topRegras?.length) {
          <div class="top-regras">
            <h2>Regras Mais Aplicadas</h2>
            <div class="regras-list">
              @for (regra of stats()!.topRegras; track regra.codigo; let i = $index) {
                <div class="regra-item">
                  <span class="regra-rank">#{{ i + 1 }}</span>
                  <span class="regra-codigo">{{ regra.codigo }}</span>
                  <span class="regra-count">{{ regra.totalAplicacoes }}x</span>
                </div>
              }
            </div>
          </div>
        }
      </main>
    </div>
  `,
  styles: [`
    .validation-page {
      padding: var(--ap-page-padding);
    }

    .page-title h1 {
      font-size: 1.8rem;
      font-weight: 700;
      margin: 0 0 24px;
    }

    .content { max-width: 1200px; margin: 0 auto; }
    
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 20px;
      margin-bottom: 30px;
    }
    
    .stat-card {
      background: rgba(255, 255, 255, 0.05);
      border-radius: 15px;
      padding: 20px;
      display: flex;
      align-items: center;
      gap: 15px;
    }
    
    .stat-icon { font-size: 2rem; }
    .stat-value { display: block; font-size: 1.8rem; font-weight: 700; }
    .stat-label { color: rgba(255, 255, 255, 0.6); font-size: 0.9rem; }
    
    .action-panel {
      background: rgba(255, 255, 255, 0.05);
      border-radius: 20px;
      padding: 30px;
      margin-bottom: 30px;
    }
    
    .action-panel h2 { margin: 0 0 20px; }
    
    /* Drop Zone Styles */
    .drop-zone {
      border: 2px dashed rgba(255, 255, 255, 0.3);
      border-radius: 15px;
      padding: 40px 20px;
      text-align: center;
      cursor: pointer;
      transition: all 0.3s ease;
      margin-bottom: 20px;
      background: rgba(0, 0, 0, 0.1);
    }
    
    .drop-zone:hover {
      border-color: #00d9ff;
      background: rgba(0, 217, 255, 0.05);
    }
    
    .drop-zone.drag-over {
      border-color: #00e676;
      background: rgba(0, 230, 118, 0.1);
      transform: scale(1.02);
    }
    
    .upload-icon {
      font-size: 3rem;
      display: block;
      margin-bottom: 15px;
    }
    
    .drop-zone p {
      margin: 0 0 10px;
      color: rgba(255, 255, 255, 0.8);
    }
    
    .drop-zone .hint {
      font-size: 0.85rem;
      color: rgba(255, 255, 255, 0.5);
    }
    
    .file-list {
      list-style: none;
      padding: 0;
      margin: 15px 0 0;
      text-align: left;
      max-height: 120px;
      overflow-y: auto;
    }
    
    .file-list li {
      padding: 5px 10px;
      background: rgba(0, 0, 0, 0.2);
      border-radius: 5px;
      margin-bottom: 5px;
      font-size: 0.9rem;
    }
    
    .spinner {
      display: inline-block;
      width: 40px;
      height: 40px;
      border: 3px solid rgba(255, 255, 255, 0.2);
      border-top-color: #00d9ff;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }
    
    .input-group {
      display: flex;
      gap: 15px;
    }
    
    .input-group input {
      flex: 1;
      max-width: 200px;
      padding: 15px 20px;
      border-radius: 10px;
      border: 1px solid rgba(255, 255, 255, 0.2);
      background: rgba(0, 0, 0, 0.2);
      color: #fff;
      font-size: 1rem;
    }
    
    .btn-process {
      padding: 15px 30px;
      border-radius: 10px;
      border: none;
      background: linear-gradient(135deg, #00d9ff 0%, #00a8cc 100%);
      color: #fff;
      font-weight: 600;
      font-size: 1rem;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 10px;
    }
    
    .btn-process:disabled {
      opacity: 0.7;
      cursor: not-allowed;
    }
    
    .spinner-sm {
      width: 16px;
      height: 16px;
      border: 2px solid rgba(255, 255, 255, 0.3);
      border-top-color: #fff;
      border-radius: 50%;
      animation: spin 1s linear infinite;
    }
    
    @keyframes spin { to { transform: rotate(360deg); } }
    
    .resultado {
      padding: 25px;
      border-radius: 15px;
      animation: fadeIn 0.5s;
    }
    
    .resultado.success { background: rgba(0, 230, 118, 0.1); border: 1px solid rgba(0, 230, 118, 0.3); }
    .resultado.error { background: rgba(255, 82, 82, 0.1); border: 1px solid rgba(255, 82, 82, 0.3); }
    
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(10px); }
      to { opacity: 1; transform: translateY(0); }
    }
    
    .resultado h3 { margin: 0 0 10px; }
    .resultado p { margin: 0 0 20px; color: rgba(255, 255, 255, 0.8); }
    
    .resultado-stats {
      display: flex;
      gap: 30px;
      margin-bottom: 20px;
    }
    
    .resultado-stat {
      text-align: center;
    }
    
    .resultado-stat .value {
      display: block;
      font-size: 2rem;
      font-weight: 700;
    }
    
    .resultado-stat.success .value { color: #00e676; }
    
    .resultado-stat .label {
      color: rgba(255, 255, 255, 0.6);
    }
    
    .erros {
      background: rgba(255, 82, 82, 0.1);
      padding: 15px;
      border-radius: 10px;
      margin-bottom: 20px;
    }
    
    .erros h4 { margin: 0 0 10px; color: #ff5252; }
    .erros ul { margin: 0; padding-left: 20px; }
    .erros li { color: rgba(255, 255, 255, 0.8); }
    
    .resultado-actions {
      display: flex;
      gap: 15px;
    }
    
    .btn-secondary {
      padding: 12px 24px;
      border-radius: 10px;
      border: 1px solid rgba(255, 255, 255, 0.3);
      background: transparent;
      color: #fff;
      cursor: pointer;
    }
    
    .btn-primary {
      padding: 12px 24px;
      border-radius: 10px;
      border: none;
      background: linear-gradient(135deg, #00d9ff 0%, #00a8cc 100%);
      color: #fff;
      font-weight: 600;
      cursor: pointer;
    }
    
    .preview-section {
      background: rgba(255, 255, 255, 0.03);
      border-radius: 20px;
      padding: 30px;
      margin-bottom: 30px;
    }
    
    .preview-section h2 { margin: 0 0 20px; }
    
    .arquivo-card {
      background: rgba(255, 255, 255, 0.05);
      border-radius: 12px;
      padding: 20px;
      margin-bottom: 15px;
    }
    
    .arquivo-header {
      display: flex;
      align-items: center;
      gap: 15px;
      margin-bottom: 15px;
    }
    
    .arquivo-nome { font-weight: 600; }
    
    .arquivo-status {
      padding: 4px 12px;
      border-radius: 20px;
      font-size: 0.8rem;
    }
    
    .arquivo-status.corrigido { background: rgba(0, 230, 118, 0.2); color: #00e676; }
    .arquivo-status.validado { background: rgba(0, 217, 255, 0.2); color: #00d9ff; }
    
    .arquivo-count {
      margin-left: auto;
      color: rgba(255, 255, 255, 0.6);
    }
    
    .correcoes-table {
      width: 100%;
      border-collapse: collapse;
    }
    
    .correcoes-table th,
    .correcoes-table td {
      padding: 10px;
      text-align: left;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .correcoes-table th {
      color: rgba(255, 255, 255, 0.6);
      font-weight: 500;
    }
    
    .correcoes-table code {
      background: rgba(0, 0, 0, 0.3);
      padding: 2px 6px;
      border-radius: 4px;
      font-size: 0.85rem;
    }
    
    .antes { color: #ff5252; }
    .depois { color: #00e676; }
    
    .top-regras {
      background: rgba(255, 255, 255, 0.03);
      border-radius: 20px;
      padding: 30px;
    }
    
    .top-regras h2 { margin: 0 0 20px; }
    
    .regras-list {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    
    .regra-item {
      display: flex;
      align-items: center;
      gap: 15px;
      padding: 15px;
      background: rgba(255, 255, 255, 0.05);
      border-radius: 10px;
    }
    
    .regra-rank {
      width: 30px;
      height: 30px;
      border-radius: 50%;
      background: linear-gradient(135deg, #00d9ff 0%, #00a8cc 100%);
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      font-size: 0.9rem;
    }
    
    .regra-codigo {
      flex: 1;
      font-family: monospace;
    }
    
    .regra-count {
      color: #00e676;
      font-weight: 600;
    }
    
    /* Preview Actions */
    .preview-actions {
      display: flex;
      gap: 15px;
      margin-top: 25px;
      padding-top: 25px;
      border-top: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .btn-apply {
      padding: 15px 30px;
      border-radius: 10px;
      border: none;
      background: linear-gradient(135deg, #00e676 0%, #00c853 100%);
      color: #fff;
      font-weight: 600;
      font-size: 1rem;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 10px;
    }
    
    .btn-apply:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }
    
    .btn-export {
      padding: 15px 30px;
      border-radius: 10px;
      border: none;
      background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
      color: #fff;
      font-weight: 600;
      font-size: 1rem;
      cursor: pointer;
    }
    
    .btn-export:disabled {
      opacity: 0.4;
      cursor: not-allowed;
    }
    
    /* Aplicação Resultado */
    .aplicacao-resultado {
      margin-top: 20px;
      padding: 20px;
      border-radius: 12px;
      background: rgba(0, 230, 118, 0.1);
      border: 1px solid rgba(0, 230, 118, 0.3);
    }
    
    .aplicacao-resultado h3 { margin: 0 0 15px; }
    
    .aplicacao-stats {
      display: flex;
      gap: 30px;
    }
    
    .aplicacao-stat { text-align: center; }
    .aplicacao-stat .value {
      display: block;
      font-size: 1.8rem;
      font-weight: 700;
      color: #00e676;
    }
    .aplicacao-stat .label { color: rgba(255, 255, 255, 0.6); }
    
    /* Hash Button */
    .btn-hash {
      padding: 15px 30px;
      border-radius: 10px;
      border: none;
      background: linear-gradient(135deg, #9c27b0 0%, #7b1fa2 100%);
      color: #fff;
      font-weight: 600;
      font-size: 1rem;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 10px;
    }
    
    .btn-hash:disabled {
      opacity: 0.4;
      cursor: not-allowed;
    }
    
    /* PTU Export Button */
    .btn-ptu {
      padding: 15px 30px;
      border-radius: 10px;
      border: none;
      background: linear-gradient(135deg, #2e7d32 0%, #1b5e20 100%);
      color: #fff;
      font-weight: 600;
      font-size: 1rem;
      cursor: pointer;
    }
    
    .btn-ptu:disabled {
      opacity: 0.4;
      cursor: not-allowed;
    }
    
    /* Hash Resultado */
    .hash-resultado {
      margin-top: 20px;
      padding: 20px;
      border-radius: 12px;
      background: rgba(156, 39, 176, 0.1);
      border: 1px solid rgba(156, 39, 176, 0.3);
    }
    
    .hash-resultado h3 { margin: 0 0 15px; color: #ce93d8; }
    
    .hash-list {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    
    .hash-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 10px;
      background: rgba(0, 0, 0, 0.2);
      border-radius: 8px;
    }
    
    .hash-arquivo { color: rgba(255, 255, 255, 0.8); }
    
    .hash-value {
      background: rgba(156, 39, 176, 0.2);
      padding: 4px 12px;
      border-radius: 6px;
      font-family: monospace;
      font-size: 0.85rem;
      color: #ce93d8;
    }
    
    /* Modal */
    .modal-overlay {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.8);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 1000;
    }
    
    .modal-content {
      background: #1e1e2e;
      border-radius: 20px;
      padding: 30px;
      max-width: 450px;
      width: 90%;
      animation: modalIn 0.3s ease-out;
    }
    
    @keyframes modalIn {
      from { transform: scale(0.9); opacity: 0; }
      to { transform: scale(1); opacity: 1; }
    }
    
    .modal-content h3 { margin: 0 0 15px; font-size: 1.4rem; }
    .modal-content p { margin: 0 0 10px; color: rgba(255, 255, 255, 0.8); }
    .modal-warning { color: #ff9800 !important; font-size: 0.9rem; }
    
    .modal-actions {
      display: flex;
      gap: 15px;
      margin-top: 25px;
      justify-content: flex-end;
    }
    
    .btn-confirm {
      padding: 12px 24px;
      border-radius: 10px;
      border: none;
      background: linear-gradient(135deg, #00e676 0%, #00c853 100%);
      color: #fff;
      font-weight: 600;
      cursor: pointer;
    }
  `]
})
export class ValidationComponent implements OnInit {
  private validationService = inject(ValidationService);
  private router = inject(Router);
  private route = inject(ActivatedRoute);
  
  isProcessing = this.validationService.isProcessing;
  
  execucaoId = signal<number>(0);
  resultado = signal<ValidationResult | null>(null);
  preview = signal<PreviewResult | null>(null);
  stats = signal<ValidationStats | null>(null);
  
  // New signals for apply/export
  isApplying = signal<boolean>(false);
  aplicacaoResultado = signal<AplicarResult | null>(null);
  showConfirmModal = signal<boolean>(false);
  
  // Hash signals
  isCalculatingHash = signal<boolean>(false);
  hashResultado = signal<HashResult | null>(null);
  
  // Upload signals
  isDragOver = signal<boolean>(false);
  isUploading = this.validationService.isUploading;
  uploadedFiles = this.validationService.uploadedFiles;
  
  ngOnInit(): void {
    this.loadStats();
    
    // Check for execucaoId in query params
    const id = this.route.snapshot.queryParams['execucaoId'];
    if (id) {
      this.execucaoId.set(parseInt(id, 10));
    }
  }
  
  loadStats(): void {
    this.validationService.getStats().subscribe(stats => {
      this.stats.set(stats);
    });
  }
  
  setExecucaoId(event: Event): void {
    const input = event.target as HTMLInputElement;
    this.execucaoId.set(parseInt(input.value, 10) || 0);
  }
  
  // Drag & Drop handlers
  onDragOver(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragOver.set(true);
  }
  
  onDragLeave(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragOver.set(false);
  }
  
  onDrop(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragOver.set(false);
    
    const files = event.dataTransfer?.files;
    if (files && files.length > 0) {
      this.uploadFiles(Array.from(files));
    }
  }
  
  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.uploadFiles(Array.from(input.files));
    }
  }
  
  uploadFiles(files: File[]): void {
    this.validationService.uploadArquivos(files).subscribe(result => {
      if (result?.sucesso) {
        console.log('Upload concluído:', result.arquivos);
      }
    });
  }
  
  processar(): void {
    const id = this.execucaoId();
    if (id <= 0) return;
    
    this.validationService.processarLote(id).subscribe(result => {
      this.resultado.set(result);
      if (result?.sucesso) {
        this.loadStats();
      }
    });
  }
  
  novoProcessamento(): void {
    this.resultado.set(null);
    this.preview.set(null);
    this.aplicacaoResultado.set(null);
  }
  
  verPreview(): void {
    const result = this.resultado();
    if (!result) return;
    
    this.validationService.getPreview(result.execucaoId).subscribe(preview => {
      this.preview.set(preview);
    });
  }
  
  // New methods for apply/export
  confirmarAplicacao(): void {
    this.showConfirmModal.set(true);
  }
  
  cancelarAplicacao(): void {
    this.showConfirmModal.set(false);
  }
  
  aplicar(): void {
    this.showConfirmModal.set(false);
    this.isApplying.set(true);
    
    const result = this.resultado();
    if (!result) return;
    
    this.validationService.aplicarCorrecoes(result.execucaoId).subscribe(aplicacao => {
      this.isApplying.set(false);
      this.aplicacaoResultado.set(aplicacao);
      if (aplicacao?.sucesso) {
        this.loadStats();
      }
    });
  }
  
  exportarZip(): void {
    const result = this.resultado();
    if (!result) return;
    
    this.validationService.exportarZip(result.execucaoId);
  }
  
  recalcularHash(): void {
    const result = this.resultado();
    if (!result) return;
    
    this.isCalculatingHash.set(true);
    
    this.validationService.recalcularHash(result.execucaoId).subscribe(hashResult => {
      this.isCalculatingHash.set(false);
      this.hashResultado.set(hashResult);
    });
  }
  
  exportarZipPtu(): void {
    const result = this.resultado();
    if (!result) return;
    
    this.validationService.exportarZipPtu(result.execucaoId);
  }
}
