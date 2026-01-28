export interface Regra {
  id: number;
  codigo: string;
  nome: string;
  descricao?: string;
  categoria: RuleCategory;
  grupo: RuleGroup;
  prioridade: number;
  ativo: boolean;
  logica?: string;
  createdAt: Date;
  updatedAt?: Date;
}

export type RuleCategory = 'GLOSA_GUIA' | 'GLOSA_ITEM' | 'VALIDACAO' | 'OTIMIZACAO';
export type RuleGroup = 'DATAS' | 'VALORES' | 'QUANTIDADES' | 'CODIGOS' | 'DUPLICIDADES' | 
                        'AUTORIZACAO' | 'BENEFICIARIO' | 'PRESTADOR' | 'TISS' | 'OUTROS';

export interface RegraCreate {
  codigo: string;
  nome: string;
  descricao?: string;
  categoria: RuleCategory;
  grupo: RuleGroup;
  prioridade: number;
  logica?: string;
}
