export interface RelatorioGlosasEvitadas {
  dataInicio: Date;
  dataFim: Date;
  totalExecucoes: number;
  totalArquivosProcessados: number;
  totalCorrecoes: number;
  valorTotalEvitado: number;
  mediaPorExecucao: number;
}

export interface RegraEfetividade {
  codigo: string;
  nome: string;
  categoria: string;
  totalAplicacoes: number;
  totalGlosasEvitadas: number;
  taxaEfetividade: number;
}

export interface ResumoMensal {
  mes: number;
  mesNome: string;
  totalExecucoes: number;
  totalArquivos: number;
  totalCorrecoes: number;
  valorEconomizado: number;
  taxaSucesso: number;
}

export interface FiltroRelatorio {
  dataInicio?: Date;
  dataFim?: Date;
  ano?: number;
}
