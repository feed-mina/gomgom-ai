'use client';

import React, { useState } from 'react';
import {
  Container,
  Typography,
  TextField,
  Button,
  Grid,
  Box,
  Alert,
  CircularProgress,
} from '@mui/material';
import { Search } from '@mui/icons-material';
import { recipeApi } from '../../api/recipeApi';
import { RecipeSearchResponse } from '../../types/recipe';
import { RecipeCard } from '../../components/RecipeCard';

export default function RecipeSearchPage() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchResult, setSearchResult] = useState<RecipeSearchResponse | null>(null);

  const handleSearch = async () => {
    if (!query.trim()) {
      setError('검색어를 입력해주세요.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await recipeApi.searchRecipes({
        query: query.trim(),
        number: 3,
        include_price: true,
      });

      setSearchResult(result);
    } catch (err) {
      console.error('레시피 검색 오류:', err);
      setError('레시피 검색 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h3" component="h1" gutterBottom sx={{ textAlign: 'center' }}>
        🍳 레시피 추천 서비스
      </Typography>
      
      <Box sx={{ mb: 4 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={8}>
            <TextField
              fullWidth
              label="음식명을 입력하세요 (예: 김치찌개)"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <Button
              fullWidth
              variant="contained"
              onClick={handleSearch}
              disabled={loading}
              startIcon={loading ? <CircularProgress size={20} /> : <Search />}
            >
              {loading ? '검색 중...' : '검색'}
            </Button>
          </Grid>
        </Grid>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {searchResult && (
        <Box>
          <Typography variant="h5" gutterBottom>
            &quot;{searchResult.query}&quot; 검색 결과 ({searchResult.total_results}개)
          </Typography>
          <Grid container spacing={3}>
            {searchResult.recipes.map((recipe, index) => (
              <Grid item xs={12} sm={6} md={4} key={index}>
                <RecipeCard recipe={recipe} />
              </Grid>
            ))}
          </Grid>
        </Box>
      )}
    </Container>
  );
} 