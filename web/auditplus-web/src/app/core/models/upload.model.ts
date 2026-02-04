export interface UploadResult {
  loteId: string;
  execucaoId: number;
  totalArquivos: number;
  arquivosAceitos: number;
  arquivosRejeitados: number;
  arquivos: ArquivoInfo[];
}

export interface ArquivoInfo {
  nome: string;
  tamanho: number;
  status: 'ACEITO' | 'REJEITADO' | 'ERRO';
  motivo?: string;
  caminho?: string;
}

export interface Lote {
  id: number;
  tipoOperacao: string;
  status: string;
  totalArquivos: number;
  arquivosSucesso: number;
  arquivosErro: number;
  dataInicio: Date;
  dataFim?: Date;
  totalCorrecoes: number;
  valorEconomizado: number;
}
