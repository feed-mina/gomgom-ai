'use client';

import React, { useState, useMemo } from 'react';
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

const KOREAN_KEYWORDS = [
  '김밥', '비빔밥', '불고기', '된장찌개', '김치찌개', '잡채', '떡볶이', '갈비', '삼겹살', '순두부', '부대찌개', '파전', '감자탕', '냉면', '칼국수', '수제비', '팥빙수', '전', '국밥', '콩나물국밥', '순대', '오징어볶음', '제육볶음', '닭갈비', '닭볶음탕', '찜닭', '불닭', '쭈꾸미', '해물파전', '김치전', '계란찜', '계란말이', '미역국', '갈비탕', '설렁탕', '육개장', '곰탕', '동태찌개', '감자조림', '멸치볶음', '시금치나물', '콩나물무침', '무생채', '도라지무침', '고등어조림', '코다리조림', '장조림', '오이무침', '깻잎장아찌', '고추장아찌', '깍두기', '총각김치', '백김치', '열무김치', '동치미', '오징어채볶음', '고추장불고기', '닭강정', '닭발', '곱창', '막창', '순대국', '감자전', '호박전', '동그랑땡', '유부초밥', '주먹밥', '비빔국수', '잔치국수', '쫄면', '라면', '부추전', '고추전', '고등어구이', '삼치구이', '꽁치조림', '북엇국', '콩비지찌개', '청국장', '홍합탕', '매운탕', '아구찜', '해물찜', '낙지볶음', '낙지탕탕이', '오징어순대', '명태조림', '명란젓', '오징어젓', '창란젓', '게장', '간장게장', '양념게장', '새우장', '멍게비빔밥', '돌솥비빔밥', '산채비빔밥', '콩국수', '냉콩국수', '우엉조림', '연근조림', '고사리나물', '취나물', '도토리묵', '묵사발', '묵무침', '오이소박이', '깻잎김치', '파김치', '고추김치', '나박김치', '물김치', '보쌈', '족발', '편육', '수육', '홍어삼합', '굴비', '조기구이', '병어조림', '갈치조림', '갈치구이', '고등어무조림', '꽁치구이', '장어구이', '장어덮밥', '추어탕', '민물매운탕', '복지리', '복매운탕', '아욱국', '시래기국', '우거지국', '우거지해장국', '선지해장국', '콩나물해장국', '북어해장국', '황태해장국', '뼈해장국', '감자해장국', '매운해장국', '닭한마리', '닭도리탕', '닭곰탕', '닭죽', '삼계탕', '오리백숙', '오리주물럭', '오리불고기', '오리훈제', '오리탕', '오리로스', '오리찜', '오리구이', '오리백숙', '오리탕', '오리주물럭', '오리불고기', '오리훈제', '오리로스', '오리찜', '오리구이'
  // 필요시 더 추가
];

function isKoreanFood(query: string): boolean {
  return KOREAN_KEYWORDS.some(keyword => query.includes(keyword));
}

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
      const cuisineTypeParam =
        cuisineType === 'all'
          ? (isKoreanFood(query) ? 'korean' : undefined)
          : cuisineType;
      
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
      const translatedRecipes = translated.map((translatedText, index) => {
        const recipe = result.recipes[index];
        return {
          ...recipe,
          title: translatedText,
          summary: translatedText,
          difficulty: translatedText,
          ingredients: recipe.ingredients?.map((i, iidx) => ({ ...i, name: translatedText })) || [],
          cuisines: recipe.cuisines?.map(() => translatedText) || [],
          dishTypes: recipe.dishTypes?.map(() => translatedText) || [],
          diets: recipe.diets?.map(() => translatedText) || [],
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