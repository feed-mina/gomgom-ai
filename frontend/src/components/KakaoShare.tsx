'use client';

import React, { useEffect } from 'react';
import { Button, Box, Typography } from '@mui/material';
import { Share } from '@mui/icons-material';

declare global {
  interface Window {
    Kakao: any;
  }
}

interface KakaoShareProps {
  title: string;
  description: string;
  imageUrl?: string;
  url?: string;
  buttonText?: string;
}

export default function KakaoShare({ 
  title, 
  description, 
  imageUrl = '/image/logo.png',
  url = window.location.href,
  buttonText = "카카오톡으로 공유하기"
}: KakaoShareProps) {
  
  useEffect(() => {
    // 카카오 SDK 초기화
    if (typeof window !== 'undefined' && !window.Kakao.isInitialized()) {
      window.Kakao.init(process.env.NEXT_PUBLIC_KAKAO_APP_KEY || '2d22c7fa1d59eb77a5162a3948a0b6fe');
    }
  }, []);

  const handleShare = () => {
    if (typeof window !== 'undefined' && window.Kakao) {
      window.Kakao.Link.sendDefault({
        objectType: 'feed',
        content: {
          title: title,
          description: description,
          imageUrl: imageUrl,
          link: {
            mobileWebUrl: url,
            webUrl: url,
          },
        },
        buttons: [
          {
            title: '자세히 보기',
            link: {
              mobileWebUrl: url,
              webUrl: url,
            },
          },
        ],
      });
    } else {
      // 카카오 SDK가 로드되지 않은 경우 기본 공유
      const shareText = `${title}\n\n${description}\n\n${url}`;
      if (navigator.share) {
        navigator.share({
          title: title,
          text: description,
          url: url,
        });
      } else {
        // 클립보드에 복사
        navigator.clipboard.writeText(shareText).then(() => {
          alert('링크가 클립보드에 복사되었습니다!');
        });
      }
    }
  };

  return (
    <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
      <Button
        variant="contained"
        startIcon={<Share />}
        onClick={handleShare}
        sx={{
          backgroundColor: '#FEE500',
          color: '#000',
          '&:hover': {
            backgroundColor: '#FDD835'
          }
        }}
      >
        {buttonText}
      </Button>
    </Box>
  );
} 