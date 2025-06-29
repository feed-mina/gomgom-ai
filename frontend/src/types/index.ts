export interface Restaurant {
  id: string;
  name: string;
  logo_url: string;
  categories: string[];
  review_avg: number;
  review_count: number;
  delivery_fee_to_display: {
    basic: string;
  };
  address: string;
  keywords?: string[];
}

export interface TestResult {
  store: string;
  description: string;
  category: string;
  keywords: string[];
  logo_url: string;
} 

export interface Location {
  lat: number;
  lng: number;
}

export interface Question {
  q: string;
  a: {
    answer: string;
    type: string;
  }[];
}

export interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user?: User;
}

export interface KakaoAuthResponse {
  auth_url: string;
}

export interface LoginFormData {
  email: string;
  password: string;
}

export interface RegisterFormData {
  email: string;
  password: string;
  full_name: string;
}

export interface ApiResponse<T = any> {
  data?: T;
  error?: string;
  message?: string;
} 