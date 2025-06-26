import React from 'react';
import { Card, CardMedia } from '@mui/material';
import { RecipeRecommendation } from '../types/recipe';

interface RecipeCardProps {
  recipe: RecipeRecommendation;
  onClick?: () => void;
  query?: string;
}

export const RecipeCard: React.FC<RecipeCardProps> = ({ recipe, onClick }) => {
  return (
    <Card sx={{ maxWidth: 400, height: '100%', display: 'flex', flexDirection: 'column', cursor: onClick ? 'pointer' : 'default' }} onClick={onClick}>
      {recipe.image && (
        <CardMedia
          component="img"
          height="200"
          image={recipe.image}
          alt={recipe.title}
          sx={{ objectFit: 'cover' }}
        />
      )}
    </Card>
  );
}; 