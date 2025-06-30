'use client';

import React, { useEffect, useState, Suspense, useCallback } from 'react';
import styled from '@emotion/styled';
import { useRouter, useSearchParams } from 'next/navigation';
import apiClient from '@/utils/apiClient';
import {
  Box,
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

const Card = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  max-width: 30rem;
  margin: auto;
  background: white;
  border-radius: 1.25rem;
  box-shadow: 0 0.25rem 0.625rem rgba(0,0,0,0.1);
  padding: 1.875rem;
  text-align: center;

  h3 {
    color: #BEA397;
    margin: 1rem 0;
    font-size: 1.2rem;
    
    @media (max-width: 768px) {
      font-size: 1rem;
    }
  }

  p {
    font-size: 1.125rem;
    margin: 0.625rem 0;
    
    @media (max-width: 768px) {
      font-size: 1rem;
    }
  }
  
  @media (max-width: 768px) {
    padding: 1.5rem;
    border-radius: 1rem;
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
  const [results, setResults] = useState<any[]>([]); // 추천 결과 배열
  const [currentIndex, setCurrentIndex] = useState(0); // 현재 인덱스
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
      setResult(data); // result/result.restaurants 등 기존 호환
      setResults(data.results || (data.result ? [data.result] : []));
      setCurrentIndex(0);
      setCurrentAddress(data.result?.address || '');
      setIsLoading(false);
    } catch (err: any) {
      setError(err.message || '추천 결과를 불러오지 못했습니다.');
      setIsLoading(false);
    }
  }, [text, lat, lng, types, dummy]);

  useEffect(() => {
    loadResult();
  }, [loadResult]);

  const handleRetry = () => {
    if (results.length > 0) {
      setCurrentIndex((prev) => (prev + 1) % results.length);
    }
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
          <Alert severity="error">{error}</Alert>
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

  // 화면에 표시할 추천 결과
  const currentResult = results[currentIndex] || result?.result || {};

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
              {text}와 어울리고 ,
            </div>
          )}
          <h3>{currentResult.store}</h3>
          <p><strong>{currentResult.description}</strong></p>
          <Address>{currentResult.address || currentAddress}</Address>
            <ResultImage
              src="/image/rabbit_chef_body2.png"
              alt="토끼"
              width={200}
              height={200}
            />
          {/* 기타 정보 표시 */}
          {currentResult.logo_url && (
            <StoreLogo src={currentResult.logo_url} alt="store logo" width={80} height={80} />
          )}
          <InfoText>
            {text && text !== '===' && (
              <div><span style={{fontWeight: 'bold', color: '#6B4E71'}}>입력 텍스트:</span> {text}</div>
            )}
            <div><span style={{fontWeight: 'bold', color: '#6B4E71'}}>카테고리:</span> {currentResult.category}</div>
            <div><span style={{fontWeight: 'bold', color: '#6B4E71'}}>키워드:</span> {currentResult.keywords?.join(', ')}</div>
          </InfoText>
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
              boxShadow: '0 2px 8px rgba(0,0,0,0.07)',
              marginTop: '1rem'
            }}
            onClick={handleRetry}
          >
            🔄 다시 추천받기
          </button>
        </Card>
        <KakaoShare
          title={currentResult.store ? `🍔 ${currentResult.store} 추천!` : '추천 결과'}
          description={currentResult.description || ''}
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