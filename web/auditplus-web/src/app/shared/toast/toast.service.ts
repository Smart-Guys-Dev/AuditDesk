import { Injectable, signal } from '@angular/core';

export interface Toast {
  id: number;
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  duration: number;
}

@Injectable({
  providedIn: 'root'
})
export class ToastService {
  private counter = 0;
  private toastsSignal = signal<Toast[]>([]);
  readonly toasts = this.toastsSignal.asReadonly();

  success(message: string, duration = 4000): void {
    this.addToast('success', message, duration);
  }

  error(message: string, duration = 6000): void {
    this.addToast('error', message, duration);
  }

  warning(message: string, duration = 5000): void {
    this.addToast('warning', message, duration);
  }

  info(message: string, duration = 4000): void {
    this.addToast('info', message, duration);
  }

  dismiss(id: number): void {
    this.toastsSignal.update(list => list.filter(t => t.id !== id));
  }

  private addToast(type: Toast['type'], message: string, duration: number): void {
    const id = ++this.counter;
    this.toastsSignal.update(list => [...list, { id, type, message, duration }]);
    setTimeout(() => this.dismiss(id), duration);
  }
}
