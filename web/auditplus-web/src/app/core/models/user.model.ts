export interface User {
  id: number;
  username: string;
  fullName: string;
  email?: string;
  role: string;
  lastLoginAt?: Date;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  token: string;
  username: string;
  fullName: string;
  role: string;
  expiresAt: Date;
}

export interface RegisterRequest {
  username: string;
  password: string;
  fullName: string;
  email?: string;
  role?: string;
}
