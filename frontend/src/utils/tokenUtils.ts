import { jwtDecode } from 'jwt-decode';

interface TokenPayload {
  exp: number;
  sub: string;
  [key: string]: any;
}

export const isTokenExpired = (token: string): boolean => {
  try {
    const decoded = jwtDecode<TokenPayload>(token);
    const currentTime = Date.now() / 1000;
    return decoded.exp < currentTime;
  } catch (error) {
    console.error('토큰 디코딩 오류:', error);
    return true; // 디코딩 실패 시 만료된 것으로 처리
  }
};

export const getTokenExpirationTime = (token: string): Date | null => {
  try {
    const decoded = jwtDecode<TokenPayload>(token);
    return new Date(decoded.exp * 1000);
  } catch (error) {
    console.error('토큰 디코딩 오류:', error);
    return null;
  }
};

export const getTimeUntilExpiration = (token: string): number => {
  try {
    const decoded = jwtDecode<TokenPayload>(token);
    const currentTime = Date.now() / 1000;
    return Math.max(0, decoded.exp - currentTime);
  } catch (error) {
    console.error('토큰 디코딩 오류:', error);
    return 0;
  }
};

export const clearUserData = (): void => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_email');
    localStorage.removeItem('user_nickname');
    // 스토리지 변경 이벤트를 발생시켜 헤더를 업데이트합니다.
    window.dispatchEvent(new Event("storage"));
  }
};

export const checkAndHandleTokenExpiration = (): boolean => {
  if (typeof window === 'undefined') return false;
  
  const token = localStorage.getItem('access_token');
  
  if (!token) {
    return false;
  }

  if (isTokenExpired(token)) {
    console.log('토큰이 만료되었습니다. 자동 로그아웃합니다.');
    clearUserData();
    return true; // 만료됨
  }

  return false; // 만료되지 않음
};

// 토큰 만료 1시간 전에 경고를 표시하는 함수
export const shouldShowExpirationWarning = (token: string): boolean => {
  const timeUntilExpiration = getTimeUntilExpiration(token);
  const oneHourInSeconds = 60 * 60; // 1시간
  
  return timeUntilExpiration > 0 && timeUntilExpiration <= oneHourInSeconds;
}; 