import axios from 'axios';
import { checkAndHandleTokenExpiration } from './tokenUtils';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// axios 인스턴스 생성
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

// 요청 인터셉터 - 토큰을 헤더에 추가
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      // 토큰 만료 체크
      const isExpired = checkAndHandleTokenExpiration();
      if (isExpired) {
        // 토큰이 만료된 경우 요청을 취소
        return Promise.reject(new Error('Token expired'));
      }
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 응답 인터셉터 - 401 에러 처리
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // 401 에러 시 토큰 만료로 간주하고 로그아웃 처리
      console.log('API 요청에서 401 에러 발생. 자동 로그아웃합니다.');
      checkAndHandleTokenExpiration();
      
      // 로그인 페이지로 리다이렉트
      if (typeof window !== 'undefined') {
        window.location.href = '/';
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient; 