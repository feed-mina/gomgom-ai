'use client';

import React, { useState } from 'react';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Divider,
  Alert
} from '@mui/material';
import axios from 'axios';
import { useRouter } from 'next/navigation';
import { LoginFormData } from '../../types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function LoginPage() {
  const router = useRouter();
  const [formData, setFormData] = useState<LoginFormData>({
    email: '',
    password: ''
  });
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const formDataToSend = new FormData();
      formDataToSend.append('username', formData.email);
      formDataToSend.append('password', formData.password);

      const response = await axios.post(`${API_BASE_URL}/api/v1/auth/login`, formDataToSend, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });

      localStorage.setItem('access_token', response.data.access_token);
      router.push('/');
    } catch (error: any) {
      setError(error.response?.data?.detail || '로그인에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleKakaoLogin = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/v1/auth/kakao/login`);
      window.location.href = response.data.auth_url;
    } catch (error) {
      setError('카카오 로그인 URL을 가져오는데 실패했습니다.');
    }
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ mt: 8, mb: 4 }}>
        <Paper elevation={3} sx={{ p: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom align="center">
            로그인
          </Typography>
          
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="이메일"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleInputChange}
              margin="normal"
              required
            />
            <TextField
              fullWidth
              label="비밀번호"
              name="password"
              type="password"
              value={formData.password}
              onChange={handleInputChange}
              margin="normal"
              required
            />
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
              disabled={loading}
            >
              {loading ? '로그인 중...' : '로그인'}
            </Button>
          </form>

          <Divider sx={{ my: 2 }}>또는</Divider>

          <Button
            fullWidth
            variant="outlined"
            onClick={handleKakaoLogin}
            sx={{
              backgroundColor: '#FEE500',
              color: '#000',
              borderColor: '#FEE500',
              '&:hover': {
                backgroundColor: '#FDD835',
                borderColor: '#FDD835'
              }
            }}
          >
            카카오로 로그인
          </Button>

          <Box sx={{ mt: 2, textAlign: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              계정이 없으신가요?{' '}
              <Button
                variant="text"
                onClick={() => router.push('/register')}
                sx={{ p: 0, minWidth: 'auto' }}
              >
                회원가입
              </Button>
            </Typography>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
} 