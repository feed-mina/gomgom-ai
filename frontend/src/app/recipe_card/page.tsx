'use client';
import { useSearchParams, useRouter } from 'next/navigation';
import { useEffect, useState, Suspense } from 'react';
import { recipeApi } from '../../api/recipeApi';
import { Card, CircularProgress, Alert, Button, Switch, FormControlLabel, Box } from '@mui/material';
import { RecipeRecommendation } from '../../types/recipe';
import { RecipeDetailCard } from '../../components/RecipeDetailCard';
import LoadingFallback from '../../components/LoadingFallback';

// 레시피 상세 처리 컴포넌트
function RecipeDetailContent() {
  const params = useSearchParams();
  const router = useRouter();
  const id = params.get('id');
  const query = params.get('query');
  const source = params.get('source');
  const title = params.get('title');
  const [recipe, setRecipe] = useState<RecipeRecommendation | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [translate, setTranslate] = useState(false);
  const [isTranslating, setIsTranslating] = useState(false);

  const loadRecipe = async (shouldTranslate: boolean = false) => {
    if (!id) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const data = await recipeApi.getRecipeById(id, source || undefined, shouldTranslate);
      setRecipe(data);
      setLoading(false);
    } catch (err) {
      console.error('레시피 로딩 오류:', err);
      setError('레시피를 불러오는 중 오류가 발생했습니다.');
      setLoading(false);
    }
  };

  useEffect(() => {
    if (id) {
      loadRecipe(false); // 기본적으로 번역 없이 로드
    }
  }, [id, source]);

  const handleTranslateToggle = async () => {
    if (!id) return;
    
    const newTranslateState = !translate;
    setTranslate(newTranslateState);
    
    if (newTranslateState) {
      setIsTranslating(true);
      await loadRecipe(true);
      setIsTranslating(false);
    } else {
      // 번역 해제시 원본 데이터로 다시 로드
      await loadRecipe(false);
    }
  };

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        minHeight: '50vh',
        flexDirection: 'column',
        gap: '16px'
      }}>
        <CircularProgress />
        <div>레시피를 불러오는 중...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        minHeight: '50vh',
        flexDirection: 'column',
        gap: '16px'
      }}>
        <Alert severity="error" style={{ maxWidth: '400px' }}>
          {error}
        </Alert>
        <Button 
          variant="contained" 
          onClick={() => router.back()}
        >
          뒤로 가기
        </Button>
      </div>
    );
  }

  if (!recipe) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        minHeight: '50vh',
        flexDirection: 'column',
        gap: '16px'
      }}>
        <Alert severity="warning" style={{ maxWidth: '400px' }}>
          레시피를 찾을 수 없습니다.
        </Alert>
        <Button 
          variant="contained" 
          onClick={() => router.back()}
        >
          뒤로 가기
        </Button>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px' }}>
      {/* 번역 토글 버튼 */}
      <Box 
        display="flex" 
        justifyContent="center" 
        alignItems="center" 
        mb={2}
        gap={2}
      >
        <FormControlLabel
          control={
            <Switch
              checked={translate}
              onChange={handleTranslateToggle}
              disabled={isTranslating}
            />
          }
          label={isTranslating ? "번역 중..." : "한글로 번역"}
        />
        {isTranslating && <CircularProgress size={20} />}
      </Box>

      {/* 레시피 카드 */}
      <div style={{ display: 'flex', justifyContent: 'center' }}>
        <RecipeDetailCard recipe={{ ...recipe, title: title || recipe.title }} />
      </div>
    </div>
  );
}

// 메인 페이지 컴포넌트
export default function RecipeDetailPage() {
  return (
    <Suspense fallback={<LoadingFallback message="레시피를 불러오는 중..." variant="centered" />}>
      <RecipeDetailContent />
    </Suspense>
  );
}
