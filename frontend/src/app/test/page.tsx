'use client';

import { useEffect, useState, Suspense } from 'react';
import styled from '@emotion/styled';
import Image from 'next/image';
import { useRouter, useSearchParams } from 'next/navigation';
import Header from '@/components/Header';
import Loading from '@/components/Loading';
import { Question } from '@/types';

const questions: Question[] = [
  {
    q: '1. 혼밥을 하러 갔을 때, 어떤 분위기의 식당을 더 좋아하나요?',
    a: [
      { answer: 'a. 사람 많고 북적북적한 식당', type: 'active' },
      { answer: 'b. 조용하고 아늑한 식당', type: 'calm' }
    ]
  },
  {
    q: '2. 메뉴를 고를 때 나는...',
    a: [
      { answer: 'a. 항상 새로운 음식을 도전해본다', type: 'adventurous' },
      { answer: 'b. 내가 좋아하는 익숙한 메뉴를 고른다', type: 'familiar' }
    ]
  },
  {
    q: '3. 음식에 대해 나는...',
    a: [
      { answer: 'a. 매콤하거나 자극적인 맛을 좋아한다', type: 'spicy' },
      { answer: 'b. 담백하고 순한 맛을 선호한다', type: 'mild' }
    ]
  },
  {
    q: '4. 국물 있는 음식을 고를 때 나는...',
    a: [
      { answer: 'a. 진하고 기름진 국물이 좋다', type: 'rich' },
      { answer: 'b. 맑고 깔끔한 국물이 좋다', type: 'light' }
    ]
  },
  {
    q: '5. 음식을 먹고 나면...',
    a: [
      { answer: 'a. 입가심으로 음료를 마신다', type: 'drink' },
      { answer: 'b. 디저트로 케이크나 아이스크림을 먹는다', type: 'dessert' }
    ]
  },
  {
    q: '6. 친구가 나에게 추천을 부탁할 때 나는...',
    a: [
      { answer: 'a. 요즘 핫한 음식을 추천한다', type: 'trendy' },
      { answer: 'b. 무난하고 실패 없는 음식을 추천한다', type: 'safe' }
    ]
  }
];

const Container = styled.div`
  min-height: 100vh;
  background-color: #FAF0D7;
`;

const Main = styled.main`
  max-width: 50rem;
  margin: 0 auto;
  padding: 2rem;
  text-align: center;
  
  @media (max-width: 768px) {
    padding: 1.5rem;
  }
`;

const Title = styled.div`
  margin-bottom: 2rem;
`;

const RabbitImage = styled(Image)`
  width: 12.5rem;
  height: 17.8rem;
  
  @media (max-width: 768px) {
    width: 10rem;
    height: 14.2rem;
  }
`;

const QuestionBox = styled.div`
  background-color: white;
  border-radius: 0.75rem;
  padding: 2rem;
  box-shadow: 0 0.125rem 0.25rem rgba(0,0,0,0.1);
  
  @media (max-width: 768px) {
    padding: 1.5rem;
    border-radius: 0.5rem;
  }
`;

const QuestionText = styled.div`
  font-size: 1.5rem;
  color: #333;
  margin-bottom: 2rem;
  
  @media (max-width: 768px) {
    font-size: 1.2rem;
    margin-bottom: 1.5rem;
  }
`;

const AnswerButtons = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const AnswerButton = styled.button`
  background-color: #8CC0DE;
  color: white;
  padding: 1rem;
  border: none;
  border-radius: 0.5rem;
  font-size: 1.2rem;
  cursor: pointer;
  transition: background-color 0.3s;

  &:hover {
    background-color: #6BA8C6;
  }
  
  @media (max-width: 768px) {
    padding: 0.8rem;
    font-size: 1rem;
  }
`;

function TestPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedTypes, setSelectedTypes] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const text = searchParams.get('text') || '';
  const lat = searchParams.get('lat') || '';
  const lng = searchParams.get('lng') || '';

  useEffect(() => {
    setIsLoading(false);
  }, []);

  const handleAnswer = (type: string) => {
    const newTypes = [...selectedTypes, type];
    setSelectedTypes(newTypes);

    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    } else {
      // 모든 질문이 끝나면 결과 페이지로 이동
      router.push(`/test_result?text=${encodeURIComponent(text || '')}&lat=${lat}&lng=${lng}&types=${newTypes.join(',')}`);
    }
  };

  if (isLoading) {
    return <Loading />;
  }

  return (
    <Container>
      <Header />
      <Main>
        <Title>
          <RabbitImage
            src="/image/elice_chef_rabbit_1.png"
            alt="rabbit"
            width={200}
            height={285}
          />
        </Title>
        <QuestionBox>
          <QuestionText>{questions[currentQuestion].q}</QuestionText>
          <AnswerButtons>
            {questions[currentQuestion].a.map((answer, index) => (
              <AnswerButton
                key={index}
                onClick={() => handleAnswer(answer.type)}
              >
                {answer.answer}
              </AnswerButton>
            ))}
          </AnswerButtons>
        </QuestionBox>
      </Main>
    </Container>
  );
}

export default function Test() {
  return (
    <Suspense fallback={<Loading />}>
      <TestPage />
    </Suspense>
  );
} 