import { Card, CardMedia } from '@mui/material';
import { RecipeRecommendation } from '../types/recipe';

interface RecipeCardItemProps {
  recipe: RecipeRecommendation;
}

export const RecipeCardItem = ({ recipe }: RecipeCardItemProps) => (
  <Card sx={{ maxWidth: 345, m: 1, display: 'flex', flexDirection: 'column' }}>
    {recipe.image && (
      <CardMedia
        component="img"
        height="180"
        image={recipe.image}
        alt={recipe.title}
        sx={{ objectFit: 'cover' }}
      />
    )}
  </Card>
);
