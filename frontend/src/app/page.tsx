'use client';

import { useState, useEffect } from 'react';
import styled from '@emotion/styled';
import { useRouter } from 'next/navigation';

export default function Home() {
  const [latestLat, setLatestLat] = useState<number | null>(null);
  const [latestLng, setLatestLng] = useState<number | null>(null);
  const [geoReady, setGeoReady] = useState(false);
  const [userInput, setUserInput] = useState('');
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [showEmptyInputModal, setShowEmptyInputModal] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const getLocation = async () => {
      if (typeof window === 'undefined') return;
      
      if (!navigator.geolocation) {
        router.push('/restaurant_list?lat=37.484934&lng=126.981321');
        return;
      }

      try {
        const position = await new Promise<GeolocationPosition>((resolve, reject) => {
          navigator.geolocation.getCurrentPosition(resolve, reject);
        });
        
        setLatestLat(position.coords.latitude);
        setLatestLng(position.coords.longitude);
        setGeoReady(true);
      } catch (error) {
        console.error('Geolocation error:', error);
        router.push('/restaurant_list?lat=37.484934&lng=126.981321');
      }
    };

    getLocation();
  }, [router]);

  const handleRecommend = () => {
    if (!geoReady) return;
    setShowConfirmModal(true);
  };

  const handleTestClick = () => {
    if (!geoReady) return;
    if (!userInput.trim()) {
      setShowEmptyInputModal(true);
    } else {
      router.push(`/start?text=${encodeURIComponent(userInput)}&lat=${latestLat}&lng=${latestLng}`);
    }
  };

  const handleCheckYogiyo = () => {
    if (!geoReady) return;
    router.push(`/restaurant_list?lat=${latestLat}&lng=${latestLng}`);
  };

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
                    onChange={(e) => setUserInput(e.target.value)}
                    placeholder="예: 매운 음식 추천해줘"
                  />
                  <Button onClick={handleRecommend}>입력 추천</Button>
                </InputBox>
                <Button onClick={handleTestClick}>입맛 테스트</Button>
              </ButtonGroup>
            </Article>
          </All>
        </Main>
      </MainContainer>

      {showConfirmModal && (
        <Modal>
          <ModalContent>
            <p>입맛 테스트도 해보시겠어요?</p>
            <Button onClick={() => {
              setShowConfirmModal(false);
              router.push(`/start?text=${encodeURIComponent(userInput)}&lat=${latestLat}&lng=${latestLng}`);
            }}>네</Button>
            <Button onClick={() => {
              setShowConfirmModal(false);
              if (!userInput.trim()) {
                alert("추천을 받기 위해서는 입력값이 필요해요!");
                return;
              }
              router.push(`/recommend_result?text=${encodeURIComponent(userInput)}&lat=${latestLat}&lng=${latestLng}`);
            }}>아니요</Button>
          </ModalContent>
        </Modal>
      )}

      {showEmptyInputModal && (
        <Modal>
          <ModalContent>
            <p>바로 입맛 테스트를 진행할까요?</p>
            <Button onClick={() => {
              setShowEmptyInputModal(false);
              router.push(`/start?text=&lat=${latestLat}&lng=${latestLng}`);
            }}>네</Button>
            <Button onClick={() => setShowEmptyInputModal(false)}>아니요</Button>
          </ModalContent>
        </Modal>
      )}
    </Container>
  );
}

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
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const Text = styled.span``;

const Blink = styled.span`
  animation: blink 1s infinite;
  
  @keyframes blink {
    50% { opacity: 0; }
  }
`;

const Image = styled.div`
  position: relative;
  display: flex;
  justify-content: center;
  margin: 2rem 0;
  z-index: 1;
  
  @media (max-width: 768px) {
    margin: 1.5rem 0;
  }
`;

const Circle = styled.div`
  position: absolute;
  width: 12.5rem;
  height: 12.5rem;
  border-radius: 50%;
  background: #f8f9fa;
  z-index: 1;
  
  @media (max-width: 768px) {
    width: 10rem;
    height: 10rem;
  }
`;

const RabbitImg = styled.img`
  position: relative;
  z-index: 2;
  height: 12.5rem;
  
  @media (max-width: 768px) {
    height: 10rem;
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const InputBox = styled.div`
  display: flex;
  gap: 0.5rem;
  
  @media (max-width: 768px) {
    flex-direction: column;
  }
`;

const Input = styled.input`
  flex: 1;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 0.25rem;
  font-size: 1rem;
  outline: none;
  
  &:focus {
    border-color: #007bff;
  }
  
  @media (max-width: 768px) {
    font-size: 0.9rem;
    padding: 0.4rem;
  }
`;

const Button = styled.button`
  padding: 0.5rem 1rem;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  font-size: 1rem;
  
  &:hover {
    background-color: #218838;
  }
  
  @media (max-width: 768px) {
    padding: 0.4rem 0.8rem;
    font-size: 0.9rem;
  }
`;

const Modal = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
`;

const ModalContent = styled.div`
  background: white;
  padding: 2rem;
  border-radius: 0.5rem;
  text-align: center;
  z-index: 1001;
  max-width: 90vw;
  margin: 1rem;
  
  p {
    margin-bottom: 1rem;
    font-size: 1.1rem;
  }
  
  button {
    margin: 0 0.5rem;
  }
  
  @media (max-width: 768px) {
    padding: 1.5rem;
    
    p {
      font-size: 1rem;
    }
  }
`; 