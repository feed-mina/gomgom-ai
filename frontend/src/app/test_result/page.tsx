'use client';

import { useEffect, useState, Suspense, useCallback } from 'react';
import styled from '@emotion/styled';
import Image from 'next/image';
import { useRouter, useSearchParams } from 'next/navigation';

import {
  Box,
  CircularProgress,
  Alert
} from '@mui/material';
import Loading from '@/components/Loading';
import ErrorDisplay from '@/components/ErrorDisplay';
import type { TestResult } from '@/types';
import KakaoShare from '../../components/KakaoShare';
import apiClient from '@/utils/apiClient';


interface Restaurant {
  store: string;
  description?: string;
  category?: string;
  keywords?: string[];
  logo_url?: string;
  address?: string;
  review_avg?: number;
  categories?: string;
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

const Address = styled.p`
  font-weight: bold;
  font-size: 1rem;
  color: #222;
  
  @media (max-width: 768px) {
    font-size: 0.9rem;
  }
`;

const Result = styled.div`
  display: flex;
  align-items: center;
  gap: 2rem;
  margin-bottom: 2rem;
  
  @media (max-width: 768px) {
    flex-direction: column;
    gap: 1rem;
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

const ResultImage = styled(Image)`
  width: 7rem;
  height: 7rem;
  
  @media (max-width: 768px) {
    width: 10rem;
    height: 10rem;
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

const SelectedStore = styled.h3`
  font-size: 1.8rem;
  color: #6B4E71;
  margin-bottom: 0.5rem;
  
  @media (max-width: 768px) {
    font-size: 1.4rem;
  }
`;

const SelectedDescription = styled.p`
  font-size: 1.2rem;
  color: #666;
  
  @media (max-width: 768px) {
    font-size: 1rem;
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

const RetryButton = styled.button`
  background-color: #8CC0DE;
  color: white;
  padding: 1rem 2rem;
  border: none;
  border-radius: 0.5rem;
  font-size: 1.2rem;
  cursor: pointer;
  transition: background-color 0.3s;
  display: block;
  margin: 2rem auto 0;

  &:hover {
    background-color: #6BA8C6;
  }
  
  @media (max-width: 768px) {
    padding: 0.8rem 1.5rem;
    font-size: 1rem;
    margin: 1.5rem auto 0;
  }
`;

interface Restaurant {
  store: string;
  description?: string;
  category?: string;
  keywords?: string[];
  logo_url?: string;
  address?: string;
  review_avg?: number;
}

function TestResultContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [result, setResult] = useState<any | null>(null);
  const [results, setResults] = useState<any[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const text = searchParams.get('text') || '';
  const lat = searchParams.get('lat') || '';
  const lng = searchParams.get('lng') || '';
  const types = searchParams.get('types') || '';
  const dummy = searchParams.get('dummy') || '';

  const loadResult = useCallback(async () => {
    try {
      const response = await apiClient.get('/api/v1/test_result/', {
        params: { text, lat, lng, types, dummy }
      });
      const data = response.data;
      setResult(data);
      setResults(data.results || (data.result ? [data.result] : []));
      setCurrentIndex(0);
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

  // 화면에 표시할 추천 결과
  const currentResult = results[currentIndex] || result?.result || {};

  if (!lat || !lng || !types) {
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
    return <Loading />;
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
  const restaurant = results[currentIndex] || result?.result || {};

  console.log('restaurant', restaurant);

  const logoUrl = restaurant && restaurant.logo_url ? restaurant.logo_url : '/image/default_store_logo.png';

  console.log('logoUrl', logoUrl);

  const reviewAvg = restaurant && restaurant.review_avg ? restaurant.review_avg : null;

  console.log('reviewAvg', reviewAvg);

  const address = restaurant && restaurant.address ? restaurant.address : result.address;

  console.log('address', address);

  const shareDescription = text
    ? `${text}와/과 관련되어 있는 음식은 ...`
    : `당신에게 어울리는 추천 결과입니다!`;

  return (
    <Container>
      <Main>
        <Heading>
          <h2>오늘의 추천 가게</h2>
        </Heading>
        <Card>
        
        {text && text !== '===' && (
          <h2 style={{ marginBottom: '0.5rem', fontWeight: 500 }}>
            {shareDescription}  
          </h2>
        )}
          <SelectedStore>{currentResult.store}</SelectedStore>
          <SelectedDescription>{currentResult.description}</SelectedDescription>
          <Address>{currentResult.address || result?.address}</Address>
            <ResultImage
              src="/image/rabbit_chef_body2.png"
              alt="토끼"
              width={200}
              height={200}
            />
          {currentResult.logo_url && (
          <StoreLogo
            src={currentResult?.logo_url || '/image/default_store_logo.png'}
            alt="추천 가게 로고"
            width={100}
            height={100}
          />
          )}
          <InfoText>
            <div><span style={{fontWeight: 'bold', color: '#6B4E71'}}>카테고리:</span> {currentResult.category}</div>
            <div><span style={{fontWeight: 'bold', color: '#6B4E71'}}>키워드:</span> {currentResult.keywords?.join(', ')}</div>
            <div><span style={{fontWeight: 'bold', color: '#6B4E71'}}>평균 평점:</span> {currentResult.review_avg ?? 0}</div>
            <div><span style={{fontWeight: 'bold', color: '#6B4E71'}}>테스트 결과:</span> {types}</div>
          </InfoText>
          <button
            style={{
              background: '#8CC0DE',
              color: 'white',
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

export default function TestResult() {
  return (
    <Suspense fallback={<Loading />}>
      <TestResultContent />
    </Suspense>
  );
}