import styled from '@emotion/styled';
import { useRouter } from 'next/navigation';

const ErrorContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  text-align: center;
  padding: 2rem;
`;

const ErrorCard = styled.div`
  background: white;
  border-radius: 1.25rem;
  box-shadow: 0 0.25rem 0.625rem rgba(0,0,0,0.1);
  padding: 2.5rem;
  max-width: 30rem;
  margin: 0 auto;
  
  @media (max-width: 768px) {
    padding: 2rem;
    border-radius: 1rem;
  }
`;

const ErrorIcon = styled.div`
  width: 6rem;
  height: 6rem;
  background: linear-gradient(135deg, #FFE8EE 0%, #FFD6E0 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1.5rem;
  font-size: 2.5rem;
  
  @media (max-width: 768px) {
    width: 5rem;
    height: 5rem;
    font-size: 2rem;
  }
`;

const ErrorTitle = styled.h2`
  color: #6B4E71;
  font-size: 1.5rem;
  margin-bottom: 1rem;
  
  @media (max-width: 768px) {
    font-size: 1.3rem;
  }
`;

const ErrorMessage = styled.p`
  color: #666;
  font-size: 1.1rem;
  line-height: 1.6;
  margin-bottom: 2rem;
  
  @media (max-width: 768px) {
    font-size: 1rem;
  }
`;

const ErrorButton = styled.button`
  background-color: #BEA397;
  color: white;
  padding: 1rem 2rem;
  border: none;
  border-radius: 0.5rem;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  margin: 0 0.5rem;

  &:hover {
    background-color: #A89287;
    transform: translateY(-2px);
  }
  
  @media (max-width: 768px) {
    padding: 0.8rem 1.5rem;
    font-size: 1rem;
    margin: 0.5rem;
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
  
  @media (max-width: 768px) {
    flex-direction: column;
    align-items: center;
  }
`;

interface ErrorDisplayProps {
  title?: string;
  message?: string;
  icon?: string;
  onRetry?: () => void;
  onGoHome?: () => void;
  showRetryButton?: boolean;
  showHomeButton?: boolean;
  retryButtonText?: string;
  homeButtonText?: string;
}

export default function ErrorDisplay({
  title = "결과를 불러오는데 실패했습니다",
  message = "네트워크 연결을 확인하거나 잠시 후 다시 시도해주세요.\n문제가 지속되면 다른 방법으로 시도해보세요.",
  icon = "😔",
  onRetry,
  onGoHome,
  showRetryButton = true,
  showHomeButton = true,
  retryButtonText = "다시 시도하기",
  homeButtonText = "홈으로 돌아가기"
}: ErrorDisplayProps) {
  const router = useRouter();

  const handleRetry = () => {
    if (onRetry) {
      onRetry();
    } else {
      window.location.reload();
    }
  };

  const handleGoHome = () => {
    if (onGoHome) {
      onGoHome();
    } else {
      router.push('/');
    }
  };

  return (
    <ErrorContainer>
      <ErrorCard>
        <ErrorIcon>{icon}</ErrorIcon>
        <ErrorTitle>{title}</ErrorTitle>
        <ErrorMessage>
          {message.split('\n').map((line, index) => (
            <span key={index}>
              {line}
              {index < message.split('\n').length - 1 && <br />}
            </span>
          ))}
        </ErrorMessage>
        <ButtonGroup>
          {showRetryButton && (
            <ErrorButton onClick={handleRetry}>
              {retryButtonText}
            </ErrorButton>
          )}
          {showHomeButton && (
            <ErrorButton onClick={handleGoHome}>
              {homeButtonText}
            </ErrorButton>
          )}
        </ButtonGroup>
      </ErrorCard>
    </ErrorContainer>
  );
} 