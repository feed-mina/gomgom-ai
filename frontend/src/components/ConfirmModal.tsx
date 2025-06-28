import React from 'react';
import styled from '@emotion/styled';

interface ConfirmModalProps {
  onClose: () => void;
  onConfirm: () => void;
  onTest: () => void;
}

const ConfirmModal: React.FC<ConfirmModalProps> = ({ onClose, onConfirm, onTest }) => {
  return (
    <Modal>
      <ModalContent>
        <p>GomGom-AI 심리테스트도 해보시겠어요?</p>
        <ButtonGroup>
          <Button onClick={onTest}>네</Button>
          <Button onClick={onConfirm}>아니요</Button>
        </ButtonGroup>
      </ModalContent>
    </Modal>
  );
};

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
  
  @media (max-width: 768px) {
    padding: 1.5rem;
    
    p {
      font-size: 1rem;
    }
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 0.5rem;
  justify-content: center;
`;

const Button = styled.button`
  background: lightseagreen;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 0.25rem;
  cursor: pointer;
  font-size: 1rem;
  
  &:hover {
    background: #0056b3;
  }
  
  @media (max-width: 768px) {
    font-size: 0.9rem;
    padding: 0.4rem 0.8rem;
  }
`;

export default ConfirmModal; 