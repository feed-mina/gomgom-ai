'use client';

import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import {
  Container,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  Chip,
  CircularProgress,
  Alert
} from '@mui/material';
import KakaoShare from '../../components/KakaoShare';

interface Restaurant {
  name: string;
  description: string;
  category: string;
  keywords: string[];
  logo_url?: string;
}

interface RecommendResult {
  result: Restaurant;
  address: string;
}

export default function RecommendResultPage() {
  const searchParams = useSearchParams();
  const [result, setResult] = useState<RecommendResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    const fetchResult = async () => {
      try {
        const text = searchParams.get('text');
        const lat = searchParams.get('lat');
        const lng = searchParams.get('lng');
        const types = searchParams.get('types');

        if (!text || !lat || !lng || !types) {
          setError('필수 파라미터가 누락되었습니다.');
          setLoading(false);
          return;
        }

        const response = await fetch(`/api/recommend_result?text=${text}&lat=${lat}&lng=${lng}&types=${types}`);
        if (!response.ok) {
          throw new Error('추천 결과를 가져오는데 실패했습니다.');
        }

        const data = await response.json();
        setResult(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.');
      } finally {
        setLoading(false);
      }
    };

    fetchResult();
  }, [searchParams]);

  if (loading) {
    return (
      <Container maxWidth="md">
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 8 }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="md">
        <Box sx={{ mt: 8 }}>
          <Alert severity="error">{error}</Alert>
        </Box>
      </Container>
    );
  }

  if (!result) {
    return (
      <Container maxWidth="md">
        <Box sx={{ mt: 8 }}>
          <Alert severity="warning">추천 결과가 없습니다.</Alert>
        </Box>
      </Container>
    );
  }

  const shareTitle = `🍽️ ${result.result.name} 추천!`;
  const shareDescription = `${result.result.description}\n\n📍 ${result.address}\n🏷️ ${result.result.category}`;

  return (
    <Container maxWidth="md">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          🎉 추천 결과
        </Typography>

        <Paper elevation={3} sx={{ p: 4, mt: 3 }}>
          <Card>
            <CardContent>
              <Typography variant="h5" component="h2" gutterBottom>
                {result.result.name}
              </Typography>
              
              <Typography variant="body1" color="text.secondary" paragraph>
                {result.result.description}
              </Typography>

              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle1" gutterBottom>
                  카테고리:
                </Typography>
                <Chip 
                  label={result.result.category} 
                  color="primary" 
                  variant="outlined"
                />
              </Box>

              {result.result.keywords && result.result.keywords.length > 0 && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    키워드:
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {result.result.keywords.map((keyword, index) => (
                      <Chip 
                        key={index} 
                        label={keyword} 
                        size="small" 
                        variant="outlined"
                      />
                    ))}
                  </Box>
                </Box>
              )}

              <Box sx={{ mt: 3 }}>
                <Typography variant="subtitle1" gutterBottom>
                  📍 위치:
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {result.address}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Paper>

        {/* 카카오 공유 버튼 */}
        <KakaoShare
          title={shareTitle}
          description={shareDescription}
          buttonText="🍽️ 카카오톡으로 추천 공유하기"
        />
      </Box>
    </Container>
  );
} 