import React from 'react';
import { Container, Box, CircularProgress, Typography, Paper } from '@mui/material';

interface LoadingFallbackProps {
  message?: string;
  variant?: 'simple' | 'card' | 'centered';
  size?: 'small' | 'medium' | 'large';
  containerMaxWidth?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  showMessage?: boolean;
}

const LoadingFallback: React.FC<LoadingFallbackProps> = ({
  message = '로딩 중...',
  variant = 'simple',
  size = 'medium',
  containerMaxWidth = 'md',
  showMessage = true
}) => {
  const getSize = () => {
    switch (size) {
      case 'small': return 20;
      case 'large': return 60;
      default: return 40;
    }
  };

  const renderContent = () => {
    const progress = <CircularProgress size={getSize()} />;
    
    switch (variant) {
      case 'card':
        return (
          <Paper elevation={3} sx={{ p: 4, textAlign: 'center' }}>
            <CircularProgress sx={{ mb: 2 }} size={getSize()} />
            {showMessage && (
              <Typography variant="h6">
                {message}
              </Typography>
            )}
          </Paper>
        );
      
      case 'centered':
        return (
          <Box sx={{ 
            display: 'flex', 
            justifyContent: 'center', 
            alignItems: 'center', 
            minHeight: '50vh',
            flexDirection: 'column',
            gap: '16px'
          }}>
            {progress}
            {showMessage && (
              <Typography variant="body1">
                {message}
              </Typography>
            )}
          </Box>
        );
      
      default: // simple
        return (
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 8 }}>
            {progress}
          </Box>
        );
    }
  };

  if (variant === 'card') {
    return (
      <Container maxWidth={containerMaxWidth}>
        <Box sx={{ mt: 8, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          {renderContent()}
        </Box>
      </Container>
    );
  }

  if (variant === 'centered') {
    return renderContent();
  }

  return (
    <Container maxWidth={containerMaxWidth}>
      {renderContent()}
    </Container>
  );
};

export default LoadingFallback; 