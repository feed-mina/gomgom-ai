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
  Card,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import { Search } from '@mui/icons-material';
import { recipeApi } from '../../api/recipeApi';
import { RecipeSearchResponse } from '../../types/recipe';
import { RecipeCard } from '../../components/RecipeCard';
import { useRouter } from 'next/navigation';

export default function RecipeSearchPage() {
  const [query, setQuery] = useState('');
  const [cuisineType, setCuisineType] = useState<string>('all'); // 요리 타입 선택
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchResult, setSearchResult] = useState<RecipeSearchResponse | null>(null);
  const router = useRouter();

  const handleSearch = async () => {
    if (!query.trim()) {
      setError('검색어를 입력해주세요.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // 요리 타입에 따라 cuisine_type 설정
      const cuisineTypeParam = cuisineType === 'all' ? undefined : cuisineType;
      
      const result = await recipeApi.searchRecipes({
        query: query.trim(),
        number: 10,
        include_price: true,
        cuisine_type: cuisineTypeParam
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
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="음식명을 입력하세요 (예: 김치찌개, pasta, curry)"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>요리 타입</InputLabel>
              <Select
                value={cuisineType}
                label="요리 타입"
                onChange={(e) => setCuisineType(e.target.value)}
              >
                <MenuItem value="all">모든 요리</MenuItem>
                <MenuItem value="korean">한식</MenuItem>
                <MenuItem value="chinese">중식</MenuItem>
                <MenuItem value="japanese">일식</MenuItem>
                <MenuItem value="italian">이탈리안</MenuItem>
                <MenuItem value="mexican">멕시칸</MenuItem>
                <MenuItem value="indian">인도</MenuItem>
                <MenuItem value="thai">태국</MenuItem>
                <MenuItem value="french">프랑스</MenuItem>
                <MenuItem value="american">미국</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={3}>
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
            {cuisineType !== 'all' && (
              <Typography component="span" variant="body2" color="text.secondary" sx={{ ml: 1 }}>
                ({cuisineType === 'korean' ? '한식' : 
                  cuisineType === 'chinese' ? '중식' :
                  cuisineType === 'japanese' ? '일식' :
                  cuisineType === 'italian' ? '이탈리안' :
                  cuisineType === 'mexican' ? '멕시칸' :
                  cuisineType === 'indian' ? '인도' :
                  cuisineType === 'thai' ? '태국' :
                  cuisineType === 'french' ? '프랑스' :
                  cuisineType === 'american' ? '미국' : cuisineType} 필터 적용)
              </Typography>
            )}
          </Typography>
          <Grid container spacing={3}>
            {searchResult.recipes.map((recipe, index) => (
              <Grid item xs={12} sm={6} md={4} key={index}>
                <RecipeCard
                  recipe={recipe}
                  onClick={() => router.push(`/recipe_card?id=${recipe.id}&query=${encodeURIComponent(query)}`)}
                />
              </Grid>
            ))}
          </Grid>
        </Box>
      )}
    </Container>
  );
} 