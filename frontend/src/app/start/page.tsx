'use client';

import { useEffect, useState, Suspense } from 'react';
import styled from '@emotion/styled';
import Image from 'next/image';
import { useRouter, useSearchParams } from 'next/navigation';

import Loading from '@/components/Loading';

const Container = styled.div`
  min-height: 100vh;
  background-color: ivory;
`;

const Main = styled.main`
    margin-top: 8rem;
  max-width: 50rem;
  margin: 0 auto;
  padding: 2rem;
  text-align: center;
  
  @media (max-width: 768px) {
    padding: 1.5rem;
  }
`;

const Title = styled.div`
    margin-top: 5rem;
  margin-bottom: 2rem;
`;

const TitleText = styled.h2`
  font-size: 2rem;
  color: #6B4E71;
  
  @media (max-width: 768px) {
    font-size: 1.5rem;
  }
`;

const Box = styled.div`
  margin: 2rem 0;
    display: flex;
    justify-content: center;
  @media (max-width: 768px) {
    margin: 1.5rem 0;
  }
`;

const RabbitImage = styled(Image)`
  width: 12.5rem;
  height: 17.8rem;
  
  @media (max-width: 768px) {
    width: 10rem;
    height: 14.2rem;
  }
`;

const WelcomeText = styled.h1`
  font-size: 1.5rem;
  color: #333;
  margin: 2rem 0;
  
  @media (max-width: 768px) {
    font-size: 1.2rem;
    margin: 1.5rem 0;
  }
`;

const SavedText = styled.p`
  font-size: 1.2rem;
  color: #666;
  margin: 1rem 0;
  
  @media (max-width: 768px) {
    font-size: 1rem;
  }
`;

const NextButton = styled.button`
margin-top: 2rem;
  background-color: #8CC0DE;
  color: white;
  padding: 1rem 2rem;
  border: none;
  border-radius: 0.5rem;
  font-size: 1.2rem;
  cursor: pointer;
  transition: background-color 0.3s;

  &:hover {
    background-color: #6BA8C6;
  }
  
  @media (max-width: 768px) {
    padding: 0.8rem 1.5rem;
    font-size: 1rem;
  }
`;

function StartContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [isLoading, setIsLoading] = useState(true);
  const text = searchParams.get('text') || '';
  const lat = searchParams.get('lat') || '';
  const lng = searchParams.get('lng') || '';

  useEffect(() => {
    setIsLoading(false);
  }, []);

  const handleNext = () => {
    router.push(`/test?text=${encodeURIComponent(text || '')}&lat=${lat}&lng=${lng}`);
  };

  if (isLoading) {
    return <Loading />;
  }

  return (
    <Container>
      <Main>
        <Title>
          <TitleText>GomGom-AI 심리테스트</TitleText>
        </Title>
        <Box>
          <RabbitImage
            src="/image/elice_chef_rabbit_1.png"
            alt="rabbit"
            width={200}
            height={285}
          />
        </Box>
        <WelcomeText>🐰 GomGom-AI 심리테스트에 오신 걸 환영합니다!</WelcomeText>
        {text && <SavedText><strong>입력된 텍스트: {text}</strong></SavedText>}
        <NextButton onClick={handleNext}>다음으로</NextButton>
      </Main>
    </Container>
  );
}

export default function Start() {
  return (
    <Suspense fallback={<Loading />}>
      <StartContent />
    </Suspense>
  );
} 