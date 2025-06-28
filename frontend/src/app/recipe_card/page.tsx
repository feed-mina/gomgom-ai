'use client';
import { useSearchParams, useRouter } from 'next/navigation';
import { useEffect, useState, Suspense } from 'react';
import { recipeApi } from '../../api/recipeApi';
import { Card, CircularProgress, Alert, Button } from '@mui/material';
import { RecipeRecommendation } from '../../types/recipe';
import { RecipeDetailCard } from '../../components/RecipeDetailCard';
import LoadingFallback from '../../components/LoadingFallback';

// 레시피 상세 처리 컴포넌트
function RecipeDetailContent() {
  const params = useSearchParams();
  const router = useRouter();
  const id = params.get('id');
  const query = params.get('query');
  const [recipe, setRecipe] = useState<RecipeRecommendation | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      setLoading(true);
      setError(null);
      
      recipeApi.getRecipeById(id)
        .then((data) => {
          setRecipe(data);
          setLoading(false);
        })
        .catch((err) => {
          console.error('레시피 로딩 오류:', err);
          setError('레시피를 불러오는 중 오류가 발생했습니다.');
          setLoading(false);
        });
    }
  }, [id]);

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
    <div style={{ display: 'flex', justifyContent: 'center', marginTop: 32 }}>
      <RecipeDetailCard recipe={recipe} />
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
