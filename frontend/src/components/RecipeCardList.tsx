import { Grid } from '@mui/material';
import { RecipeCardItem } from './RecipeCardItem';
import { RecipeRecommendation } from '../types/recipe';

export const RecipeCardList = ({ recipes }: { recipes: RecipeRecommendation[] }) => (
  <Grid container spacing={2} justifyContent="flex-start">
    {recipes.map((recipe) => (
      <Grid item key={recipe.id}>
        <RecipeCardItem recipe={recipe} />
      </Grid>
    ))}
  </Grid>
);
