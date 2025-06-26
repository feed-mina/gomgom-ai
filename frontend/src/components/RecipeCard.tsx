import React from 'react';
import {
  Card,
  CardContent,
  CardMedia,
  Typography,
  Box,
  Chip,
  Grid,
  List,
  ListItem,
  ListItemText,
  Divider,
  IconButton,
  Collapse,
} from '@mui/material';
import {
  AccessTime,
  People,
  Restaurant,
  ExpandMore,
  ExpandLess,
  LocalDining,
  AttachMoney,
} from '@mui/icons-material';
import { RecipeRecommendation } from '../types/recipe';

interface RecipeCardProps {
  recipe: RecipeRecommendation;
}

export const RecipeCard: React.FC<RecipeCardProps> = ({ recipe }) => {
  const [expanded, setExpanded] = React.useState(false);

  const handleExpandClick = () => {
    setExpanded(!expanded);
  };

  const formatPrice = (price?: number) => {
    if (!price) return '가격 정보 없음';
    return `${price.toLocaleString()}원`;
  };

  const formatTime = (minutes?: number) => {
    if (!minutes) return '시간 정보 없음';
    if (minutes < 60) return `${minutes}분`;
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return mins > 0 ? `${hours}시간 ${mins}분` : `${hours}시간`;
  };

  return (
    <Card sx={{ maxWidth: 400, height: '100%', display: 'flex', flexDirection: 'column' }}>
      {recipe.image_url && (
        <CardMedia
          component="img"
          height="200"
          image={recipe.image_url}
          alt={recipe.title}
          sx={{ objectFit: 'cover' }}
        />
      )}
      
      <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
        <Typography variant="h6" component="h2" gutterBottom>
          {recipe.title}
        </Typography>
        
        {recipe.summary && (
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            {recipe.summary.length > 100 
              ? `${recipe.summary.substring(0, 100)}...` 
              : recipe.summary}
          </Typography>
        )}

        <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
          {recipe.cooking_time && (
            <Chip
              icon={<AccessTime />}
              label={`요리 시간: ${formatTime(recipe.cooking_time)}`}
              size="small"
              variant="outlined"
            />
          )}
          {recipe.difficulty && (
            <Chip
              icon={<Restaurant />}
              label={`난이도: ${recipe.difficulty}`}
              size="small"
              variant="outlined"
            />
          )}
          {recipe.servings && (
            <Chip
              icon={<People />}
              label={`${recipe.servings}인분`}
              size="small"
              variant="outlined"
            />
          )}
          {recipe.total_cost && (
            <Chip
              icon={<AttachMoney />}
              label={formatPrice(recipe.total_cost)}
              size="small"
              variant="outlined"
              color="primary"
            />
          )}
        </Box>

        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
          <Typography variant="body2" color="text.secondary">
            출처: {recipe.source}
          </Typography>
          <IconButton
            onClick={handleExpandClick}
            aria-expanded={expanded}
            aria-label="더 보기"
            size="small"
          >
            {expanded ? <ExpandLess /> : <ExpandMore />}
          </IconButton>
        </Box>

        <Collapse in={expanded} timeout="auto" unmountOnExit>
          <Divider sx={{ my: 1 }} />
          
          {/* 통곡물/크림 머스타드 소스만 별도 섹션 */}
          {recipe.ingredients.some(ing => ing.name.includes('통곡물/크림 머스타드 소스')) && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1, color: 'green' }}>
                🥄 특별 재료: 통곡물/크림 머스타드 소스
              </Typography>
              <Typography variant="body2" color="text.secondary">
                샐러드와 고기 요리에 잘 어울리는 고소하고 부드러운 머스타드 소스입니다.
              </Typography>
            </Box>
          )}

          {/* 재료 목록 (특별 재료는 제외) */}
          {recipe.ingredients.length > 0 && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <LocalDining fontSize="small" />
                요리재료 ({recipe.ingredients.length}개)
              </Typography>
              <List dense>
                {recipe.ingredients.filter(ing => ing.name !== '통곡물/크림 머스타드 소스').map((ingredient, index) => (
                  <ListItem key={index} sx={{ py: 0.5 }}>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <Typography variant="body2">
                            {ingredient.name}
                            {ingredient.amount && ingredient.unit && 
                              ` (${ingredient.amount}${ingredient.unit})`
                            }
                          </Typography>
                          {ingredient.price && (
                            <Typography variant="body2" color="primary" fontWeight="bold">
                              {formatPrice(ingredient.price)}
                            </Typography>
                          )}
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </Box>
          )}

          {/* 조리 단계 */}
          {recipe.instructions.length > 0 && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                조리 단계 ({recipe.instructions.length}단계)
              </Typography>
              <List dense>
                {recipe.instructions.map((instruction, index) => (
                  <ListItem key={index} sx={{ py: 0.5 }}>
                    <ListItemText
                      primary={
                        <Typography variant="body2">
                          <strong>{instruction.number || index + 1}.</strong> {instruction.step}
                        </Typography>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </Box>
          )}

          {/* 영양 정보 */}
          {recipe.nutrition && (
            <Box>
              <Typography variant="subtitle2" gutterBottom>
                영양 정보
              </Typography>
              <Grid container spacing={1}>
                {recipe.nutrition.calories && (
                  <Grid item xs={6}>
                    <Typography variant="body2">
                      칼로리: {recipe.nutrition.calories}kcal
                    </Typography>
                  </Grid>
                )}
                {recipe.nutrition.protein && (
                  <Grid item xs={6}>
                    <Typography variant="body2">
                      단백질: {recipe.nutrition.protein}g
                    </Typography>
                  </Grid>
                )}
                {recipe.nutrition.fat && (
                  <Grid item xs={6}>
                    <Typography variant="body2">
                      지방: {recipe.nutrition.fat}g
                    </Typography>
                  </Grid>
                )}
                {recipe.nutrition.carbohydrates && (
                  <Grid item xs={6}>
                    <Typography variant="body2">
                      탄수화물: {recipe.nutrition.carbohydrates}g
                    </Typography>
                  </Grid>
                )}
              </Grid>
            </Box>
          )}
        </Collapse>
      </CardContent>
    </Card>
  );
}; 