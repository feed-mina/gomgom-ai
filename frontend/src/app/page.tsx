'use client';

import { useState, useEffect, useCallback, useMemo } from 'react';
import styled from '@emotion/styled';
import { useRouter } from 'next/navigation';
import dynamic from 'next/dynamic';

// 지연 로딩으로 모달 컴포넌트 분리
const ConfirmModal = dynamic(() => import('../components/ConfirmModal'), {
  loading: () => <div>로딩 중...</div>,
  ssr: false
});

const EmptyInputModal = dynamic(() => import('../components/EmptyInputModal'), {
  loading: () => <div>로딩 중...</div>,
  ssr: false
});

export default function Home() {
  const [latestLat, setLatestLat] = useState<number | null>(null);
  const [latestLng, setLatestLng] = useState<number | null>(null);
  const [geoReady, setGeoReady] = useState(false);
  const [userInput, setUserInput] = useState('');
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [showEmptyInputModal, setShowEmptyInputModal] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  // 지오로케이션 설정을 메모이제이션
  const getLocation = useCallback(async () => {
    if (typeof window === 'undefined') return;
    
    if (!navigator.geolocation) {
      router.push('/restaurant_list?lat=37.484934&lng=126.981321');
      return;
    }

    try {
      const position = await new Promise<GeolocationPosition>((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject, {
          timeout: 10000,
          enableHighAccuracy: false,
          maximumAge: 300000 // 5분 캐시
        });
      });
      
      setLatestLat(position.coords.latitude);
      setLatestLng(position.coords.longitude);
      setGeoReady(true);
    } catch (error) {
      console.error('Geolocation error:', error);
      router.push('/restaurant_list?lat=37.484934&lng=126.981321');
    } finally {
      setIsLoading(false);
    }
  }, [router]);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      setIsLoggedIn(true);
    }

    getLocation();
  }, [getLocation]);

  // 이벤트 핸들러들을 메모이제이션
  const handleRecommend = useCallback(() => {
    if (!geoReady) return;
    setShowConfirmModal(true);
  }, [geoReady]);

  const handleTestClick = useCallback(() => {
    if (!geoReady) return;
    if (!userInput.trim()) {
      setShowEmptyInputModal(true);
    } else {
      router.push(`/start?text=${encodeURIComponent(userInput)}&lat=${latestLat}&lng=${latestLng}`);
    }
  }, [geoReady, userInput, latestLat, latestLng, router]);

  const handleCheckYogiyo = useCallback(() => {
    if (!geoReady) return;
    router.push(`/restaurant_list?lat=${latestLat}&lng=${latestLng}`);
  }, [geoReady, latestLat, latestLng, router]);

  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setUserInput(e.target.value);
  }, []);

  // 모달 닫기 핸들러들
  const closeConfirmModal = useCallback(() => {
    setShowConfirmModal(false);
  }, []);

  const closeEmptyInputModal = useCallback(() => {
    setShowEmptyInputModal(false);
  }, []);

  // 로딩 중일 때 스켈레톤 UI 표시
  if (isLoading) {
    return (
      <Container>
        <Header>
          <HeaderLink href="/">
            <LogoImg src="/image/logo.png" alt="토끼" />
            <HeaderText>CLICK YOUR TASTE!</HeaderText>
          </HeaderLink>
        </Header>
        <MainContainer>
          <LoadingSkeleton />
        </MainContainer>
      </Container>
    );
  }

  return (
    <Container>
      <Header>
        <HeaderLink href="/">
          <LogoImg src="/image/logo.png" alt="토끼" />
          <HeaderText>CLICK YOUR TASTE!</HeaderText>
        </HeaderLink>
      </Header>
      
      <MainContainer>
        <CheckYogiyoDiv>
          <CheckYogiyoButton onClick={handleCheckYogiyo}>
            내 주변 가게
          </CheckYogiyoButton>
        </CheckYogiyoDiv>

        <Main>
          <All>
            <Article>
              <TextBackground>
                <TextBox>
                  <Text></Text>
                  <Blink>▼</Blink>
                </TextBox>
              </TextBackground>

              <Image>
                {!(showConfirmModal || showEmptyInputModal) && (
                  <>
                    <Circle />
                    <RabbitImg src="/image/elice_rabbit_stand.png" alt="토끼" />
                  </>
                )}
              </Image>

              <ButtonGroup>
                <InputBox>
                  <Input
                    type="text"
                    value={userInput}
                    onChange={handleInputChange}
                    placeholder="예: 매운 음식 추천해줘"
                  />
                  <Button onClick={handleRecommend}>입력 추천</Button>
                </InputBox>
                <Button onClick={handleTestClick}>입맛 테스트</Button>
                {isLoggedIn && (
                  <Button onClick={() => router.push('/recipe_search')}>
                    레시피 검색하기
                  </Button>
                )}
              </ButtonGroup>
            </Article>
          </All>
        </Main>
      </MainContainer>

      {showConfirmModal && (
        <ConfirmModal
          onClose={closeConfirmModal}
          onConfirm={() => {
            closeConfirmModal();
            if (!userInput.trim()) {
              alert("추천을 받기 위해서는 입력값이 필요해요!");
              return;
            }
            router.push(
              `/recommend_result?text=${encodeURIComponent(userInput)}&lat=${latestLat}&lng=${latestLng}&types=${encodeURIComponent('restaurant,food')}`
            );
          }}
          onTest={() => {
            closeConfirmModal();
            router.push(`/start?text=${encodeURIComponent(userInput)}&lat=${latestLat}&lng=${latestLng}`);
          }}
        />
      )}

      {showEmptyInputModal && (
        <EmptyInputModal
          onClose={closeEmptyInputModal}
          onConfirm={() => {
            closeEmptyInputModal();
            router.push(`/start?text=&lat=${latestLat}&lng=${latestLng}`);
          }}
        />
      )}
    </Container>
  );
}

// 스켈레톤 로딩 컴포넌트
const LoadingSkeleton = () => (
  <div style={{ 
    display: 'flex', 
    justifyContent: 'center', 
    alignItems: 'center', 
    height: '50vh',
    fontSize: '1.2rem',
    color: '#666'
  }}>
    위치 정보를 가져오는 중...
  </div>
);

const Container = styled.div`
  font-family: 'Noto Sans KR', sans-serif;
`;

const Header = styled.header`
  padding: 1rem;
`;

const HeaderLink = styled.a`
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const LogoImg = styled.img`
  height: 2.5rem;
  
  @media (max-width: 768px) {
    height: 2rem;
  }
`;

const HeaderText = styled.span`
  color: #333;
  font-weight: bold;
  font-size: 1.1rem;
  
  @media (max-width: 768px) {
    font-size: 1rem;
  }
`;

const MainContainer = styled.div`
  max-width: 75rem;
  margin: 0 auto;
  padding: 2rem;
  
  @media (max-width: 768px) {
    padding: 1rem;
  }
`;

const CheckYogiyoDiv = styled.div`
  margin-bottom: 2rem;
`;

const CheckYogiyoButton = styled.button`
  padding: 0.5rem 1rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  font-size: 1rem;
  
  &:hover {
    background-color: #0056b3;
  }
  
  @media (max-width: 768px) {
    padding: 0.4rem 0.8rem;
    font-size: 0.9rem;
  }
`;

const Main = styled.main`
  display: flex;
  justify-content: center;
`;

const All = styled.div`
  width: 100%;
  max-width: 50rem;
`;

const Article = styled.article`
  background: white;
  border-radius: 0.5rem;
  padding: 2rem;
  box-shadow: 0 0.125rem 0.25rem rgba(0,0,0,0.1);
  
  @media (max-width: 768px) {
    padding: 1.5rem;
    border-radius: 0.375rem;
  }
`;

const TextBackground = styled.div`
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 0.5rem;
  margin-bottom: 2rem;
  
  @media (max-width: 768px) {
    padding: 0.75rem;
    margin-bottom: 1.5rem;
  }
`;

const TextBox = styled.div`
  padding: 16px;
  background: #fff;
`;

const Image = styled.div`
  margin-bottom: 2rem;
  display: flex;
  justify-content: center;
  align-items: center;
`;

const Circle = styled.div`
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background-color: #007bff;
  margin-right: 20px;
`;

const RabbitImg = styled.img`
  height: 100px;
`;

const ButtonGroup = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const InputBox = styled.div`
  display: flex;
  align-items: center;
`;

const Input = styled.input`
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 0.25rem;
  margin-right: 0.5rem;
`;

const Button = styled.button`
  padding: 0.5rem 1rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  font-size: 1rem;
  
  &:hover {
    background-color: #0056b3;
  }
  
  @media (max-width: 768px) {
    padding: 0.4rem 0.8rem;
    font-size: 0.9rem;
  }
`;

const Text = styled.span`
  color: #333;
  font-size: 1rem;
`;

const Blink = styled.span`
  animation: blink 1s step-end infinite;
  @keyframes blink {
    0% { opacity: 0; }
    50% { opacity: 1; }
    100% { opacity: 0; }
  }
`;