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
  LinearProgress,
} from '@mui/material';
import { Search } from '@mui/icons-material';
import { recipeApi } from '../../api/recipeApi';
import { RecipeSearchResponse } from '../../types/recipe';
import { RecipeCard } from '../../components/RecipeCard';
import { useRouter } from 'next/navigation';
import { batchTranslate } from '../../types/translate';

export default function RecipeSearchPage() {
  const [query, setQuery] = useState('');
  const [cuisineType, setCuisineType] = useState<string>('all'); // 요리 타입 선택
  const [loading, setLoading] = useState(false);
  const [translating, setTranslating] = useState(false);
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
        number: 3,
        include_price: true,
        cuisine_type: cuisineTypeParam
      });

      // 먼저 기본 결과를 표시
      setSearchResult(result);
      setLoading(false);

      // 번역은 백그라운드에서 진행
      setTranslating(true);
      
      // 번역할 텍스트 모으기
      const textsToTranslate: string[] = [];
      result.recipes.forEach((r) => {
        textsToTranslate.push(
          r.title ?? "",
          r.summary ?? "",
          r.difficulty ?? ""
        );
        r.ingredients?.forEach((i) => textsToTranslate.push(i.name ?? ""));
        r.cuisines?.forEach((c) => textsToTranslate.push(c ?? ""));
        r.dishTypes?.forEach((d) => textsToTranslate.push(d ?? ""));
        r.diets?.forEach((d) => textsToTranslate.push(d ?? ""));
      });

      console.log(`번역 시작: ${textsToTranslate.length}개 텍스트`);
      const translated = await batchTranslate(textsToTranslate);
      
      // 번역 결과 매핑
      let idx = 0;
      const translatedRecipes = result.recipes.map((r) => {
        const title_ko = translated[idx++];
        const summary_ko = translated[idx++];
        const difficulty_ko = translated[idx++];
        const ingredients_ko = r.ingredients?.map(() => translated[idx++]) || [];
        const cuisines_ko = r.cuisines?.map(() => translated[idx++]) || [];
        const dishTypes_ko = r.dishTypes?.map(() => translated[idx++]) || [];
        const diets_ko = r.diets?.map(() => translated[idx++]) || [];
        return {
          ...r,
          title: title_ko,
          summary: summary_ko,
          difficulty: difficulty_ko,
          ingredients: r.ingredients?.map((i, iidx) => ({ ...i, name: ingredients_ko[iidx] })) || [],
          cuisines: cuisines_ko,
          dishTypes: dishTypes_ko,
          diets: diets_ko,
        };
      });
      
      // 번역된 결과로 업데이트
      setSearchResult({ ...result, recipes: translatedRecipes });
      setTranslating(false);
      
    } catch (err) {
      console.error('레시피 검색 오류:', err);
      setError('레시피 검색 중 오류가 발생했습니다.');
      setLoading(false);
      setTranslating(false);
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

      {translating && (
        <Alert severity="info" sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <CircularProgress size={20} />
            <Typography>
              한국어 번역 중... 잠시만 기다려주세요.
            </Typography>
          </Box>
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
                  onClick={() => router.push(`/recipe_card?id=${recipe.id}&query=${encodeURIComponent(String(query))}`)}
                />
              </Grid>
            ))}
          </Grid>
        </Box>
      )}
    </Container>
  );
} 