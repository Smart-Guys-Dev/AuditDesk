import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';
import { AuthService } from '../services/auth.service';

/**
 * Interceptor funcional para tratamento de erros HTTP.
 * - 401 Unauthorized: token expirado ou inválido → logout + redirect para login
 * - 403 Forbidden: sem permissão → log + rethrow
 * - Outros erros: rethrow para tratamento local
 */
export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      // Não tratar erros em requests de login (evita loop infinito)
      if (req.url.includes('/auth/login')) {
        return throwError(() => error);
      }

      switch (error.status) {
        case 401:
          // Token expirado ou inválido — forçar logout
          console.warn('⚠️ 401 Unauthorized — sessão expirada');
          authService.logout();
          break;

        case 403:
          // Sem permissão para o recurso
          console.warn('⚠️ 403 Forbidden — acesso negado a:', req.url);
          router.navigate(['/dashboard']);
          break;

        case 0:
          // Erro de rede (servidor offline, CORS, etc)
          console.error('❌ Erro de rede — API inacessível');
          break;

        case 500:
          console.error('❌ Erro interno do servidor:', error.message);
          break;
      }

      return throwError(() => error);
    })
  );
};
