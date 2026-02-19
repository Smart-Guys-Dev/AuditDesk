import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ToastService } from './toast.service';

@Component({
  selector: 'app-toast',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="toast-container">
      @for (toast of toastService.toasts(); track toast.id) {
        <div class="toast toast-{{ toast.type }}" (click)="toastService.dismiss(toast.id)">
          <span class="toast-icon">
            @switch (toast.type) {
              @case ('success') { ✓ }
              @case ('error') { ✕ }
              @case ('warning') { ⚠ }
              @case ('info') { ℹ }
            }
          </span>
          <span class="toast-message">{{ toast.message }}</span>
          <button class="toast-close" (click)="$event.stopPropagation(); toastService.dismiss(toast.id)">×</button>
        </div>
      }
    </div>
  `,
  styles: [`
    .toast-container {
      position: fixed;
      top: 20px;
      right: 20px;
      z-index: 9999;
      display: flex;
      flex-direction: column;
      gap: 10px;
      max-width: 420px;
    }

    .toast {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 14px 20px;
      border-radius: 12px;
      color: #fff;
      font-size: 0.9rem;
      font-weight: 500;
      cursor: pointer;
      animation: slideIn 0.3s ease-out;
      backdrop-filter: blur(12px);
      border: 1px solid rgba(255,255,255,0.15);
      box-shadow: 0 8px 32px rgba(0,0,0,0.25);
    }

    .toast-success {
      background: linear-gradient(135deg, rgba(16,185,129,0.92), rgba(5,150,105,0.92));
    }
    .toast-error {
      background: linear-gradient(135deg, rgba(239,68,68,0.92), rgba(185,28,28,0.92));
    }
    .toast-warning {
      background: linear-gradient(135deg, rgba(245,158,11,0.92), rgba(217,119,6,0.92));
    }
    .toast-info {
      background: linear-gradient(135deg, rgba(59,130,246,0.92), rgba(37,99,235,0.92));
    }

    .toast-icon {
      font-size: 1.2rem;
      flex-shrink: 0;
    }

    .toast-message {
      flex: 1;
      line-height: 1.4;
    }

    .toast-close {
      background: none;
      border: none;
      color: rgba(255,255,255,0.7);
      font-size: 1.3rem;
      cursor: pointer;
      padding: 0 4px;
      flex-shrink: 0;
      transition: color 0.2s;
    }
    .toast-close:hover {
      color: #fff;
    }

    @keyframes slideIn {
      from {
        transform: translateX(100%);
        opacity: 0;
      }
      to {
        transform: translateX(0);
        opacity: 1;
      }
    }
  `]
})
export class ToastComponent {
  toastService = inject(ToastService);
}
