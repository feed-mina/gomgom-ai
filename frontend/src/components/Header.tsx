'use client';

import React, { useState, useEffect } from 'react';
import { AppBar, Toolbar, Typography, Button, Box, Avatar, Menu, MenuItem } from '@mui/material';
import { AccountCircle } from '@mui/icons-material';
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface User {
  email: string;
  full_name: string;
}

export default function Header() {
  const [user, setUser] = useState<User | null>(null);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const updateUser = () => {
      const token = localStorage.getItem('access_token');
      const email = localStorage.getItem('user_email');
      const nickname = localStorage.getItem('user_nickname');

      if (token && email && nickname) {
        setUser({ email: email, full_name: nickname });
      } else {
        setUser(null);
      }
      setLoading(false);
    };

    updateUser(); // 초기 로드 시 실행

    window.addEventListener('storage', updateUser); // 스토리지 변경 감지

    return () => {
      window.removeEventListener('storage', updateUser); // 클린업
    };
  }, []);

  const handleKakaoLogin = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/v1/auth/kakao/login`);
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

  return (
    <AppBar position="static" sx={{ backgroundColor: '#FFF0F5' }}>
      <Toolbar>
        <Typography 
          variant="h6" 
          component="div" 
          sx={{ flexGrow: 1, cursor: 'pointer', color: '#333' }}
          onClick={() => window.location.href = '/'}
        >
          GomGom AI
        </Typography>
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, minHeight: '36px' }}>
          {loading ? null : user ? (
            <>
              <Typography sx={{ color: '#333' }}>
                {user.full_name}님, 환영합니다!
              </Typography>
              <Button color="inherit" onClick={handleLogout} sx={{ color: '#333' }}>
                로그아웃
              </Button>
            </>
          ) : (
            <>
              {/* <Button color="inherit" onClick={() => window.location.href = '/login'}>
                로그인
              </Button> */}
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
  );
} 