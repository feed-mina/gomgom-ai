'use client';
import { useSearchParams, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { recipeApi } from '../../api/recipeApi';
import { Card } from '@mui/material';
import { RecipeRecommendation } from '../../types/recipe';
import { RecipeCard } from '../../components/RecipeCard';

export default function RecipeDetailPage() {
  const params = useSearchParams();
  const id = params.get('id');
  const query = params.get('query');
  const [recipe, setRecipe] = useState<RecipeRecommendation | null>(null);

  useEffect(() => {
    if (id) {
      recipeApi.getRecipeById(id).then(setRecipe);
    }
  }, [id]);

  if (!recipe) return <div>로딩중...</div>;
  return (
    <div style={{ display: 'flex', justifyContent: 'center', marginTop: 32 }}>
      <RecipeCard recipe={recipe} />
    </div>
  );
}
