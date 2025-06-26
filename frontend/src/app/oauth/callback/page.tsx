'use client';

import React, { useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import {
  Container,
  Paper,
  Typography,
  Box,
  CircularProgress,
  Alert
} from '@mui/material';
import apiClient from '../../../utils/apiClient';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function OAuthCallbackPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    const handleCallback = async () => {
      const code = searchParams.get('code');
      const error = searchParams.get('error');

      if (error) {
        setError('카카오 로그인에 실패했습니다.');
        setLoading(false);
        return;
      }

      if (!code) {
        setError('인가 코드가 없습니다.');
        setLoading(false);
        return;
      }

      try {
        const response = await apiClient.get(`/api/v1/auth/kakao/callback?code=${code}`);
        
        // 토큰 및 사용자 정보 저장
        localStorage.setItem('access_token', response.data.access_token);
        if (response.data.user) {
          localStorage.setItem('user_email', response.data.user.email);
          localStorage.setItem('user_nickname', response.data.user.full_name);
        }
        
        // 스토리지 변경 이벤트를 발생시켜 헤더를 업데이트합니다.
        window.dispatchEvent(new Event("storage"));

        // 홈페이지로 리다이렉트
        router.push('/');
      } catch (error: any) {
        console.error('OAuth callback error:', error);
        setError(error.response?.data?.detail || '로그인 처리 중 오류가 발생했습니다.');
        setLoading(false);
      }
    };

    handleCallback();
  }, [searchParams, router]);

  if (loading) {
    return (
      <Container maxWidth="sm">
        <Box sx={{ mt: 8, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <Paper elevation={3} sx={{ p: 4, textAlign: 'center' }}>
            <CircularProgress sx={{ mb: 2 }} />
            <Typography variant="h6">
              로그인 처리 중...
            </Typography>
          </Paper>
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="sm">
        <Box sx={{ mt: 8 }}>
          <Paper elevation={3} sx={{ p: 4 }}>
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
            <Typography variant="body1" align="center">
              <button onClick={() => router.push('/login')}>
                로그인 페이지로 돌아가기
              </button>
            </Typography>
          </Paper>
        </Box>
      </Container>
    );
  }

  return null;
} 