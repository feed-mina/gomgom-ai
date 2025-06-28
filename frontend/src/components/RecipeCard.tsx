import React from 'react';
import { Card, CardMedia, CardContent, Typography, Chip, Box } from '@mui/material';
import { RecipeRecommendation } from '../types/recipe';

interface RecipeCardProps {
  recipe: RecipeRecommendation;
  onClick?: () => void;
}

export const RecipeCard: React.FC<RecipeCardProps> = ({ recipe, onClick }) => {
  return (
    <Card
      sx={{
        maxWidth: 400,
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        cursor: onClick ? 'pointer' : 'default',
        transition: 'box-shadow 0.2s',
        '&:hover': { boxShadow: 6 }
      }}
      onClick={onClick}
    >
      {recipe.image && (
        <CardMedia
          component="img"
          height="200"
          image={recipe.image}
          alt={recipe.title}
          sx={{ objectFit: 'cover' }}
        />
      )}
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {recipe.title}
        </Typography>
        {recipe.summary && (
          <Typography variant="body2" color="text.secondary" gutterBottom>
            {recipe.summary.replace(/<[^>]+>/g, '').slice(0, 60)}...
          </Typography>
        )}
        <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          {recipe.cuisines && recipe.cuisines.map((cuisine, idx) => (
            <Chip key={idx} label={cuisine} size="small" color="primary" />
          ))}
          {recipe.dishTypes && recipe.dishTypes.map((dish, idx) => (
            <Chip key={idx} label={dish} size="small" color="secondary" />
          ))}
          {recipe.diets && recipe.diets.map((diet, idx) => (
            <Chip key={idx} label={diet} size="small" color="success" />
          ))}
        </Box>
        {recipe.difficulty && (
          <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
            난이도: {recipe.difficulty}
          </Typography>
        )}
        {recipe.readyInMinutes && (
          <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
            ⏱️ 조리 시간: {recipe.readyInMinutes}분
          </Typography>
        )}
        {recipe.ingredients && recipe.ingredients.length > 0 && (
          <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
            재료: {recipe.ingredients.map((i) => i.name).join(', ')}
          </Typography>
        )}
        {recipe.servings && (
          <Typography variant="caption" color="text.secondary" sx={{ ml: 1 }}>
            🍽️ {recipe.servings}인분
          </Typography>
        )}
      </CardContent>
    </Card>
  );
}; 