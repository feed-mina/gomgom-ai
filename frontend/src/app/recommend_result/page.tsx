'use client';

import React, { useEffect, useState, Suspense, useCallback } from 'react';
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
  store: string;
  description: string;
  category: string;
  keywords: string[];
  logo_url: string;
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

const Address = styled.p`
  font-weight: bold;
  font-size: 1rem;
  color: #222;
  @media (max-width: 768px) {
    font-size: 0.9rem;
  }
`;

const SideInfo = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  align-content: center;
  align-items: center;
  height: 15rem;
  h2 {
    font-size: 1.5rem;
    color: #333;
    @media (max-width: 768px) {
      font-size: 1.2rem;
    }
  }
`;

const ResultImage = styled(Image)`
  width: 7rem;
  height: 7rem;
  @media (max-width: 768px) {
    width: 10rem;
    height: 10rem;
  }
`;

const InfoText = styled.div`
  font-weight: 700;
  display: flex;
  flex-direction: column;
  align-items: center;
  background-color: #FFE8EE;
  border-radius: 0.75rem;
  padding: 1rem;
  box-shadow: 0 0.125rem 0.25rem rgba(0,0,0,0.1);
  div {
    font-size: 1.1rem;
    margin-bottom: 0.5rem;
    line-height: 1.4;
    @media (max-width: 768px) {
      font-size: 1rem;
    }
  }
  @media (max-width: 768px) {
    padding: 1.5rem;
    margin-bottom: 1.5rem;
  }
`;

const StoreLogo = styled(Image)`
  margin-top: 1rem;
  border-radius: 0.5rem;
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
  const dummy = searchParams.get('dummy') || '';

  const loadResult = useCallback(async () => {
    try {
      const response = await apiClient.get('/api/v1/recommend_result/', {
        params: { text, lat, lng, types, dummy }
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
      console.log('[loadResult]data.address', data.address);
      console.log('[loadResult]data.store', data.store);
      console.log('[loadResult]data.description', data.description);
      console.log('[loadResult]data.category', data.category);
      console.log('[loadResult]data.keywords', data.keywords);
      console.log('[loadResult]data.logo_url', data.logo_url);
      console.log('[loadResult]restaurants address', data.restaurants?.[0]?.address);
    } catch (error) {
      console.error('결과 로딩 실패:', error);
      setResult(null);
      setCurrentAddress('주소 정보를 가져올 수 없습니다');
    } finally {
      setIsLoading(false);
    }
  }, [text, lat, lng, types, dummy]);

  useEffect(() => {
    if (text && lat && lng && types) {
      loadResult();
    }
  }, [text, lat, lng, types, dummy, loadResult]);

  const handleRetry = () => {
    const params = new URLSearchParams(window.location.search);
    params.set('dummy', Date.now().toString());
    window.location.search = params.toString();
  };

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

  const storeName = (restaurant && restaurant.name) || result?.store || '';


  console.log('storeName', storeName);
  const shareTitle = `🍽️ ${result?.store || ''} 추천!`;
  const shareDescription = text
    ? `${text}랑 관련되어 있는 음식은 ...`
    : `당신에게 어울리는 추천 결과입니다!`;

  return (
    <Container>
      <Main>
        <Heading>
          <h2>당신에게 딱 맞는 음식은?</h2>
        </Heading>
        <Card>
          <h3>오늘의 추천 가게</h3>
          {text && text !== '===' && (
            <div style={{ marginBottom: '0.5rem', fontWeight: 500 }}>
              {text}랑 어울리고 ,
            </div>
          )}
          <h3>{storeName}</h3>
          <p><strong>{result?.description}</strong></p>
          <div>{address}</div>
          <div>
            <Image
              src="/image/rabbit_chef_body2.png"
              alt="토끼"
              width={200}
              height={200}
            />
            <div style={{
              fontWeight: 700,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              backgroundColor: '#FFE8EE',
              borderRadius: '0.75rem',
              padding: '1rem',
              boxShadow: '0 0.125rem 0.25rem rgba(0,0,0,0.1)',
              marginTop: '1rem',
            }}>
              {text && text !== '===' && (
                <div><span style={{fontWeight: 'bold', color: '#6B4E71'}}>입력 텍스트:</span> {text}</div>
              )}
              <div><span style={{fontWeight: 'bold', color: '#6B4E71'}}>카테고리:</span> {result?.category || ''}</div>
              <div><span style={{fontWeight: 'bold', color: '#6B4E71'}}>키워드:</span> {result?.keywords?.join(', ') || ''}</div>
              <Image
                src={result?.logo_url || '/image/default_store_logo.png'}
                alt="추천 가게 로고"
                width={100}
                height={100}
                style={{ marginTop: '1rem', borderRadius: '0.5rem' }}
              />
            </div>
          </div>
        </Card>
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
        <KakaoShare
          title={shareTitle}
          description={shareDescription}
          buttonText="🍽️ 카카오톡으로 추천 공유하기"
        />
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