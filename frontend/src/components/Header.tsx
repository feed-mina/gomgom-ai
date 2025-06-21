import styled from '@emotion/styled';
import Link from 'next/link';
import Image from 'next/image';

const Header = () => {
  return (
    <HeaderContainer>
      <HeaderLink href="/">
        <LogoImage src="/image/logo.png" alt="logo" width={50} height={50} />
        <HeaderText>CLICK YOUR TASTE!</HeaderText>
      </HeaderLink>
    </HeaderContainer>
  );
};

const HeaderContainer = styled.header`
  margin-bottom: 30px;
`;

const HeaderLink = styled(Link)`
  text-decoration: none;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const LogoImage = styled(Image)`
  width: 8vw;
  height: 7vh;
  max-width: 50px;
  max-height: 80px;
`;

const HeaderText = styled.span`
  font-weight: bold;
  font-size: 1.2em;
  color: #6B4E71;
  margin-left: 0.5rem;
`;

export default Header; 