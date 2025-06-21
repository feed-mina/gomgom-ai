'use client';

import { useEffect, useState, Suspense, useCallback } from 'react';
import styled from '@emotion/styled';
import Image from 'next/image';
import { useRouter, useSearchParams } from 'next/navigation';
import Header from '@/components/Header';
import Loading from '@/components/Loading';
import { TestResult } from '@/types';

const Container = styled.div`
  min-height: 100vh;
  background-color: #FAF0D7;
  padding: 2rem;
  
  @media (max-width: 768px) {
    padding: 1rem;
  }
`;

const Card = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  max-width: 25rem;
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
  margin: 1rem 0;
  
  @media (max-width: 768px) {
    font-size: 0.9rem;
  }
`;

const StoreLogo = styled(Image)`
  margin: 1rem 0;
  border-radius: 0.5rem;
`;

const RetryButton = styled.button`
  display: inline-block;
  margin-top: 1.25rem;
  background-color: #8CC0DE;
  color: white;
  padding: 0.625rem 1.25rem;
  border: none;
  border-radius: 0.625rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    background-color: #FFDBDA;
    color: #FF908B;
  }
  
  @media (max-width: 768px) {
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
  }
`;

function RecommendResultPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [result, setResult] = useState<TestResult | null>(null);
  const [currentAddress, setCurrentAddress] = useState<string>('로딩 중...');
  const [isLoading, setIsLoading] = useState(true);
  const text = searchParams.get('text') || '';
  const lat = searchParams.get('lat') || '';
  const lng = searchParams.get('lng') || '';
  const [imgSrc, setImgSrc] = useState('/images/default_store_logo.png');

  const loadResult = useCallback(async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/recommend_result/?text=${text}&lat=${lat}&lng=${lng}&mode=recommend`
      );
      console.log('[loadResult]response', response);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      console.log('[loadResult]data', data);
      console.log('[loadResult]data.restaurants', data.restaurants);
      if (data.detail) {
        throw new Error(data.detail);
      }
      
      setResult(data.result);
      
      const address =
        Array.isArray(data.restaurants) && data.restaurants.length > 0 && data.restaurants[0] && data.restaurants[0].address
          ? data.restaurants[0].address
          : data.address || data.result?.address || '===';
      setCurrentAddress(address);
      
      console.log('[loadResult]data.result.address', data.result?.address);
      console.log('[loadResult]data.result.store', data.result?.store);
      console.log('[loadResult]data.result.description', data.result?.description);
      console.log('[loadResult]data.result.category', data.result?.category);
      console.log('[loadResult]data.result.keywords', data.result?.keywords);
      console.log('[loadResult]data.result.logo_url', data.result?.logo_url);
      console.log('[loadResult]data.result.review_avg', data.result?.review_avg);
      console.log('[loadResult]restaurants address', data.restaurants?.[0]?.address);
    } catch (error) {
      console.error('결과 로딩 실패', error);
      // 에러 상태 처리
      setResult(null);
      setCurrentAddress('데이터를 불러오는데 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  }, [lat, lng, text]);

  useEffect(() => {
    if (lat && lng) {
      loadResult();
    }
  }, [lat, lng, loadResult]);

  useEffect(() => {
    if (result && result.logo_url) {
      setImgSrc(result.logo_url);
    }
  }, [result]);

  const handleRetry = () => {
    router.push('/');
  };

  if (isLoading) {
    return <Loading />;
  }

  if (!result) {
    return <div>결과를 불러오는데 실패했습니다.</div>;
  }

  return (
    <Container>
      <Header />
      <Card>
        <h3>오늘의 추천 가게</h3>
        <h3>{result.store}</h3>
        <p><strong>{result.description}</strong></p>
        <Address>{currentAddress}</Address>
        <p><strong>내가 검색한 단어:</strong> {text}</p>
        <p>📌 <strong>카테고리: {result.category}</strong></p>
        <p>🔍 <strong>관련 키워드:{Array.isArray(result.keywords) ? result.keywords.join(', ') : '키워드 없음'}
        </strong></p>
        <StoreLogo
          src={imgSrc}
          alt="추천 가게 로고"
          width={120}
          height={120}
          onError={() => setImgSrc('/image/default_store_logo.png')}
        />
        <RetryButton onClick={handleRetry}>다시 추천받기</RetryButton>
      </Card>
    </Container>
  );
}

export default function RecommendResult() {
  return (
    <Suspense fallback={<Loading />}>
      <RecommendResultPage />
    </Suspense>
  );
} 