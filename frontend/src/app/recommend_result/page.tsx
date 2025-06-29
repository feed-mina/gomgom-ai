'use client';

import { useEffect, useState, Suspense, useCallback } from 'react';
import styled from '@emotion/styled';
import { useRouter, useSearchParams } from 'next/navigation';
import apiClient from '@/utils/apiClient';
import {
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
import ErrorDisplay from '../../components/ErrorDisplay';


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

const Container = styled.div`
  min-height: 100vh;
  background-color: #FAF0D7;
`;

const Main = styled.main`
  max-width: 50rem;
  margin: 0 auto;
  padding: 2rem;
  
  @media (max-width: 768px) {
    padding: 1.5rem;
  }
`;

const Heading = styled.div`
  text-align: center;
  margin-bottom: 2rem;

  h2 {
    font-size: 2rem;
    color: #6B4E71;
    margin-bottom: 1rem;
    
    @media (max-width: 768px) {
      font-size: 1.5rem;
    }
  }
`;

// 추천 결과 처리 컴포넌트
function RecommendResultContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [result, setResult] = useState<RecommendResult | null>(null);
  const [currentAddress, setCurrentAddress] = useState<string>('로딩 중...');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const text = searchParams.get('text') || '';
  const lat = searchParams.get('lat') || '';
  const lng = searchParams.get('lng') || '';
  const types = searchParams.get('types') || '';

  // handleRetry는 먼저 선언
  const handleRetry = () => {
    const params = new URLSearchParams(window.location.search);
    params.set('dummy', Date.now().toString());
    window.location.search = params.toString();
  };

  // 모든 Hook은 최상단에서 호출
  const loadResult = useCallback(async () => {
    try {
      const response = await apiClient.get('/api/v1/recommend_result/', {
        params: { text, lat, lng, types }
      });
      const data = response.data;
      if (data.error) {
        throw new Error(data.detail || data.error);
      }
      if (!data || !data.result) {
        throw new Error('Invalid response format');
      }
      setResult(data.result);
      const address = data.restaurants && data.restaurants.length > 0
        ? data.restaurants[0].address
        : data.address || data.result?.address || '입력필요';
      setCurrentAddress(address);
      console.log('[loadResult]data.result.address', data.result?.address);
      console.log('[loadResult]data.result.store', data.result?.store);
      console.log('[loadResult]data.result.description', data.result?.description);
      console.log('[loadResult]data.result.category', data.result?.category);
      console.log('[loadResult]data.result.keywords', data.result?.keywords);
      console.log('[loadResult]data.result.logo_url', data.result?.logo_url);
      console.log('[loadResult]restaurants address', data.restaurants?.[0]?.address);
    } catch (error) {
      console.error('결과 로딩 실패:', error);
      if ((error as any)?.response) {
        console.error('서버 응답:', (error as any).response.data);
      }
      setResult(null);
      setCurrentAddress('주소 정보를 가져올 수 없습니다');
    } finally {
      setIsLoading(false);
    }
  }, [text, lat, lng, types]);

  useEffect(() => {
    if (text && lat && lng && types) {
      loadResult();
    }
  }, [text, lat, lng, types, loadResult]);

  // 조건부 렌더링은 Hook 호출 이후에만!
  if (!text || !lat || !lng || !types) {
    return (
      <Container>
        <Main>
          <ErrorDisplay 
            title="잘못된 접근입니다"
            message="필수 정보가 누락되었습니다. 홈으로 돌아가 다시 시도해주세요."
            onRetry={handleRetry}
            retryButtonText="다시 시도하기"
            homeButtonText="홈으로 돌아가기"
          />
        </Main>
      </Container>
    );
  }

  if (isLoading) {
    return (
      <Container>
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 8 }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (!result) {
    return (
      <Container>
        <Main>
          <ErrorDisplay 
            title="결과를 불러오는데 실패했습니다"
            message="네트워크 연결을 확인하거나 잠시 후 다시 시도해주세요.\n문제가 지속되면 다른 방법으로 시도해보세요."
            onRetry={handleRetry}
            retryButtonText="다시 시도하기"
            homeButtonText="홈으로 돌아가기"
          />
        </Main>
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <Box sx={{ mt: 8 }}>
          <Alert severity="error">{error}</Alert>
        </Box>
      </Container>
    );
  }

  console.log('result', result);

  // restaurant info 추출
  const restaurant = result.restaurants && result.restaurants.length > 0 ? result.restaurants[0] : null;

  console.log('restaurant', restaurant);

  const logoUrl = restaurant && restaurant.logo_url ? restaurant.logo_url : '/image/default_store_logo.png';

  console.log('logoUrl', logoUrl);


  const reviewAvg = restaurant && restaurant.review_avg ? restaurant.review_avg : null;

  console.log('reviewAvg', reviewAvg);

  const address = restaurant && restaurant.address ? restaurant.address : result.address;

  console.log('address', address);

  const storeName = (restaurant && restaurant.name) || result.result?.store || '';


  console.log('storeName', storeName);
  const shareTitle = `🍽️ ${storeName} 추천!`;
  const shareDescription = `${result.result?.description || ''}\n\n📍 ${address}\n🏷️ ${result.result?.category || ''}`;

  return (
    <Container>
      <Main>
    <Heading>
      <h2>당신에게 딱 맞는 음식은?</h2>
      </Heading>
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h3" gutterBottom align="center">
          오늘의 추천 가게: {storeName}
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
                  <Typography variant="h5" component="h4" gutterBottom>
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
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {(result.result?.category || '')
                    .split(',')
                    .map((cat, idx) => (
                      <Chip
                        key={idx}
                        label={cat.trim()}
                        color="primary"
                        variant="outlined"
                      />
                    ))}
                </Box>
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
                  📍 위치:{currentAddress}
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
            onClick={handleRetry}
          >
            🔄 다시 추천받기
          </button>
        </Box>
      </Box>
      </Main>
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