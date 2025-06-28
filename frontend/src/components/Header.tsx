'use client';

import React, { useState, useEffect } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Menu,
  MenuItem,
  Snackbar,
  Alert
} from '@mui/material';
import apiClient from '../utils/apiClient';
import { User } from '../types';
import { checkAndHandleTokenExpiration, shouldShowExpirationWarning, getTimeUntilExpiration } from '../utils/tokenUtils';

export default function Header() {
  const [user, setUser] = useState<User | null>(null);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [loading, setLoading] = useState(true);
  const [showExpirationWarning, setShowExpirationWarning] = useState(false);
  const [expirationWarningMessage, setExpirationWarningMessage] = useState('');

  useEffect(() => {
    const updateUser = () => {
      const token = localStorage.getItem('access_token');
      const email = localStorage.getItem('user_email');
      const nickname = localStorage.getItem('user_nickname');

      if (token && email && nickname) {
        // 토큰 만료 체크
        const isExpired = checkAndHandleTokenExpiration();
        if (isExpired) {
          setUser(null);
          setLoading(false);
          return;
        }

        // 토큰 만료 경고 체크
        if (shouldShowExpirationWarning(token)) {
          setShowExpirationWarning(true);
          // 경고 메시지 설정
          const timeUntilExpiration = getTimeUntilExpiration(token);
          const hours = Math.floor(timeUntilExpiration / 3600);
          const minutes = Math.floor((timeUntilExpiration % 3600) / 60);
          
          if (hours > 0) {
            setExpirationWarningMessage(`로그인 세션이 ${hours}시간 ${minutes}분 후에 만료됩니다.`);
          } else {
            setExpirationWarningMessage(`로그인 세션이 ${minutes}분 후에 만료됩니다.`);
          }
        }

        setUser({ 
          id: 0, // 임시 ID
          email: email, 
          full_name: nickname,
          is_active: true,
          is_superuser: false,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        });
      } else {
        setUser(null);
      }
      setLoading(false);
    };

    updateUser(); // 초기 로드 시 실행

    window.addEventListener('storage', updateUser); // 스토리지 변경 감지

    // 토큰 만료 체크를 주기적으로 실행 (5분마다)
    const tokenCheckInterval = setInterval(() => {
      const token = localStorage.getItem('access_token');
      if (token) {
        const isExpired = checkAndHandleTokenExpiration();
        if (isExpired) {
          setUser(null);
        } else if (shouldShowExpirationWarning(token)) {
          setShowExpirationWarning(true);
          // 경고 메시지 업데이트
          const timeUntilExpiration = getTimeUntilExpiration(token);
          const hours = Math.floor(timeUntilExpiration / 3600);
          const minutes = Math.floor((timeUntilExpiration % 3600) / 60);
          
          if (hours > 0) {
            setExpirationWarningMessage(`로그인 세션이 ${hours}시간 ${minutes}분 후에 만료됩니다.`);
          } else {
            setExpirationWarningMessage(`로그인 세션이 ${minutes}분 후에 만료됩니다.`);
          }
        }
      }
    }, 5 * 60 * 1000); // 5분

    return () => {
      window.removeEventListener('storage', updateUser); // 클린업
      clearInterval(tokenCheckInterval);
    };
  }, []);

  const handleKakaoLogin = async () => {
    try {
      const response = await apiClient.get('/api/v1/auth/kakao/login');
      window.location.href = response.data.auth_url;
    } catch (error) {
      console.error('Failed to get Kakao login URL:', error);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_email');
    localStorage.removeItem('user_nickname');
    setUser(null);
    setAnchorEl(null);
    setShowExpirationWarning(false);
    // 스토리지 변경 이벤트를 발생시켜 헤더를 업데이트합니다.
    window.dispatchEvent(new Event("storage"));
    window.location.href = '/';
  };

  const handleMenu = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleCloseExpirationWarning = () => {
    setShowExpirationWarning(false);
  };

  return (
    <>
      <AppBar position="static" sx={{ backgroundColor: 'lightpink' }}>
        <Toolbar>
          <Typography 
            variant="h6" 
            component="div" 
            sx={{ flexGrow: 1, cursor: 'pointer', color: '#fff', 'fontWeight': 700 }}
            onClick={() => window.location.href = '/'}
          >
            GomGom AI
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, minHeight: '36px' }}>
            {loading ? null : user ? (
              <>
                <Typography sx={{ color: '#333', 'fontWeight': 700 }}>
                  {user.full_name}님, 환영합니다!
                </Typography>
                <Button color="inherit" onClick={handleLogout} sx={{ color: '#333', 'fontWeight': 700 }}>
                  로그아웃
                </Button>
              </>
            ) : (
              <>
                <Button 
                  color="inherit" 
                  variant="contained"
                  onClick={handleKakaoLogin}
                  sx={{ 
                    backgroundColor: '#FEE500', 
                    color: '#000',
                    '&:hover': {
                      backgroundColor: '#FDD835'
                    }
                  }}
                >
                  카카오 로그인
                </Button>
              </>
            )}
          </Box>
        </Toolbar>
      </AppBar>

      {/* 토큰 만료 경고 스낵바 */}
      <Snackbar
        open={showExpirationWarning}
        autoHideDuration={10000} // 10초 후 자동 숨김
        onClose={handleCloseExpirationWarning}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert 
          onClose={handleCloseExpirationWarning} 
          severity="warning" 
          sx={{ width: '100%' }}
        >
          {expirationWarningMessage}
        </Alert>
      </Snackbar>
    </>
  );
} 