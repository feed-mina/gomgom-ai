'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import {
  Container,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  Chip,
  CircularProgress,
  Alert
} from '@mui/material';
import KakaoShare from '../../components/KakaoShare';
import Image from 'next/image';
import LoadingFallback from '../../components/LoadingFallback';

interface Restaurant {
  name: string;
  description?: string;
  category?: string;
  keywords?: string[];
  logo_url?: string;
  review_avg?: string;
  address?: string;
  id?: string;
  categories?: string;
}

interface RecommendResult {
  result: {
    store: string;
    description: string;
    category: string;
    keywords: string[];
    logo_url: string;
    // 필요한 필드 추가
  };
  address: string;
  restaurants: Restaurant[];
}

// 추천 결과 처리 컴포넌트
function RecommendResultContent() {
  const searchParams = useSearchParams();
  const [result, setResult] = useState<RecommendResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    const fetchResult = async () => {
      try {
        const text = searchParams.get('text');
        const lat = searchParams.get('lat');
        const lng = searchParams.get('lng');
        const types = searchParams.get('types');

        if (!text || !lat || !lng || !types) {
          setError('필수 파라미터가 누락되었습니다.');
          setLoading(false);
          return;
        }

        const url = `/api/v1/recommend_result?text=${text}&lat=${lat}&lng=${lng}&mode=recommend&rand=${Date.now()}`;
        const response = await fetch(url);
        if (!response.ok) {
          throw new Error('추천 결과를 가져오는데 실패했습니다.');
        }

        const data = await response.json();
        setResult(data.result || data);
      } catch (err) {
        setError(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.');
      } finally {
        setLoading(false);
      }
    };

    fetchResult();
  }, [searchParams]);

  if (loading) {
    return (
      <Container maxWidth="md">
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 8 }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="md">
        <Box sx={{ mt: 8 }}>
          <Alert severity="error">{error}</Alert>
        </Box>
      </Container>
    );
  }

  if (!result) {
    return (
      <Container maxWidth="md">
        <Box sx={{ mt: 8 }}>
          <Alert severity="warning">추천 결과가 없습니다.</Alert>
        </Box>
      </Container>
    );
  }

  // restaurant info 추출
  const restaurant = result.restaurants && result.restaurants.length > 0 ? result.restaurants[0] : null;
  const logoUrl = restaurant && restaurant.logo_url ? restaurant.logo_url : '/image/default_store_logo.png';
  const reviewAvg = restaurant && restaurant.review_avg ? restaurant.review_avg : null;
  const address = restaurant && restaurant.address ? restaurant.address : result.address;
  const storeName = (restaurant && restaurant.name) || result.result?.store || '';

  const shareTitle = `🍽️ ${storeName} 추천!`;
  const shareDescription = `${result.result?.description || ''}\n\n📍 ${address}\n🏷️ ${result.result?.category || ''}`;

  return (
    <Container maxWidth="md">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          🎉 추천 결과
        </Typography>

        <Paper elevation={3} sx={{ p: 4, mt: 3 }}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Image
                  src={logoUrl}
                  alt="가게 로고"
                  width={60}
                  height={60}
                  style={{
                    objectFit: 'cover',
                    borderRadius: 8,
                    marginRight: 16,
                    background: '#f5f5f5'
                  }}
                  onError={(e) => { (e.target as HTMLImageElement).src = '/image/default_store_logo.png'; }}
                />
                <Box>
                  <Typography variant="h5" component="h2" gutterBottom>
                    {storeName}
                  </Typography>
                  {reviewAvg && (
                    <Typography variant="body2" color="text.secondary">
                      ⭐ 리뷰 평점: {reviewAvg}
                    </Typography>
                  )}
                </Box>
              </Box>

              <Typography variant="body1" color="text.secondary" paragraph>
                {result.result?.description || ''}
              </Typography>

              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle1" gutterBottom>
                  카테고리:
                </Typography>
                <Chip 
                  label={result.result?.category || ''} 
                  color="primary" 
                  variant="outlined"
                />
              </Box>

              {result.result?.keywords && result.result.keywords.length > 0 && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    키워드:
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {result.result.keywords.map((keyword, index) => (
                      <Chip 
                        key={index} 
                        label={keyword} 
                        size="small" 
                        variant="outlined"
                      />
                    ))}
                  </Box>
                </Box>
              )}

              <Box sx={{ mt: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography variant="subtitle1" gutterBottom>
                  📍 위치:
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {address}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Paper>

        {/* 카카오 공유 버튼 */}
        <KakaoShare
          title={shareTitle}
          description={shareDescription}
          buttonText="🍽️ 카카오톡으로 추천 공유하기"
        />

        {/* 다시 추천받기 버튼 */}
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
          <button
            style={{
              background: '#ffe066',
              color: '#333',
              border: 'none',
              borderRadius: 8,
              padding: '12px 28px',
              fontSize: 16,
              fontWeight: 600,
              cursor: 'pointer',
              boxShadow: '0 2px 8px rgba(0,0,0,0.07)'
            }}
            onClick={() => window.location.reload()}
          >
            🔄 다시 추천받기
          </button>
        </Box>
      </Box>
    </Container>
  );
}

// 메인 페이지 컴포넌트
export default function RecommendResultPage() {
  return (
    <Suspense fallback={<LoadingFallback message="추천 결과를 불러오는 중..." variant="simple" />}>
      <RecommendResultContent />
    </Suspense>
  );
} 