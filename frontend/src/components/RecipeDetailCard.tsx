import React from 'react';
import { 
  Card, 
  CardMedia, 
  CardContent, 
  Typography, 
  Chip, 
  Box, 
  List, 
  ListItem, 
  ListItemText,
  Grid
} from '@mui/material';
import { RecipeRecommendation, AnalyzedInstructionGroup, AnalyzedInstructionStep } from '../types/recipe';

interface RecipeDetailCardProps {
  recipe: RecipeRecommendation;
}

// summary에서 불필요한 문구 제거하는 함수
function cleanSummary(summary: string): string {
  if (!summary) return '';
  
  let cleaned = summary;

  // 출처 문구 제거
  cleaned = cleaned.replace(/(Foodista|Afrolems|푸디스타|Afrolems)에서 제공합니다\./g, '');
  
  // 사이트 유도 문구 제거
  cleaned = cleaned.replace(/오늘 만들 재료들을 구매하세요\./g, '');
  cleaned = cleaned.replace(/fullbellysisters\.blogspot\.com에서 제공합니다\./g, '');
  
  // 추천 문구 제거
  cleaned = cleaned.replace(/비슷한 요리법(을|이) 보려면.*?시도해 보세요\./g, '');
  cleaned = cleaned.replace(/If you like this recipe, you might also like recipes such as.*?\./g, '');
  cleaned = cleaned.replace(/더 많은 레시피.*?\./g, '');
  cleaned = cleaned.replace(/레시피 모음.*?\./g, '');
  cleaned = cleaned.replace(/레시피 컬렉션.*?\./g, '');
  
  // a태그 링크 제거
  cleaned = cleaned.replace(/<a [^>]+>.*?<\/a>/g, '');
  
  // 연속된 쉼표, 공백 정리
  cleaned = cleaned.replace(/, ,/g, '');
  cleaned = cleaned.replace(/ +/g, ' ');
  
  return cleaned.trim();
}

const RecipeDetailCardComponent: React.FC<RecipeDetailCardProps> = ({ recipe }) => {
  return (
    <Card sx={{ maxWidth: 800, width: '100%', mx: 'auto' }}>
      {recipe.image && (
        <CardMedia
          component="img"
          height="400"
          image={recipe.image}
          alt={recipe.title}
          loading="lazy"
          sx={{ objectFit: 'cover' }}
        />
      )}
      
      <CardContent sx={{ p: 4 }}>
        {/* 제목 */}
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
          {recipe.title}
        </Typography>

        {/* 요약 정보 */}
        {recipe.summary && (
          <Typography
            variant="body1"
            color="text.secondary"
            sx={{ mb: 3, lineHeight: 1.6 }}
            component="div"
            dangerouslySetInnerHTML={{ __html: cleanSummary(recipe.summary) }}
          />
        )}

        {/* 태그들 */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
            태그
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {recipe.cuisines?.map((cuisine, idx) => (
              <Chip key={`cuisine-${idx}`} label={cuisine} size="small" color="primary" />
            ))}
            {recipe.dishTypes?.map((dish, idx) => (
              <Chip key={`dish-${idx}`} label={dish} size="small" color="secondary" />
            ))}
            {recipe.diets?.map((diet, idx) => (
              <Chip key={`diet-${idx}`} label={diet} size="small" color="success" />
            ))}
          </Box>
        </Box>

        {/* 기본 정보 */}
        <Box sx={{ mb: 3, p: 2, backgroundColor: '#f8f9fa', borderRadius: 2 }}>
          <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
          기본 정보
          </Typography>
          <Grid container spacing={2}>
            {recipe.readyInMinutes && (
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h6" color="primary">
                    ⏱️ {recipe.readyInMinutes}분
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    조리 시간
                  </Typography>
                </Box>
              </Grid>
            )}
            {recipe.servings && (
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h6" color="primary">
                    🍽️ {recipe.servings}인분
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    인분 수
                  </Typography>
                </Box>
              </Grid>
            )}
            {recipe.pricePerServing && (
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h6" color="primary">
                    💰 ${(recipe.pricePerServing / 100).toFixed(2)}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    1인분당 가격
                  </Typography>
                </Box>
              </Grid>
            )}
            {recipe.aggregateLikes && (
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h6" color="primary">
                    ❤️ {recipe.aggregateLikes}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    좋아요
                  </Typography>
                </Box>
              </Grid>
            )}
          </Grid>
          
          <Typography>
         재료 :   {recipe.ingredients?.map(i => i.name).join(', ')}
          </Typography>
          {/* 추가 정보 */}
          <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid #e0e0e0' }}>
            <Grid container spacing={1}>
              {recipe.vegetarian && (
                <Grid item>
                  <Chip label="채식" size="small" color="success" />
                </Grid>
              )}
              {recipe.vegan && (
                <Grid item>
                  <Chip label="비건" size="small" color="success" />
                </Grid>
              )}
              {recipe.glutenFree && (
                <Grid item>
                  <Chip label="글루텐 프리" size="small" color="warning" />
                </Grid>
              )}
              {recipe.dairyFree && (
                <Grid item>
                  <Chip label="유제품 프리" size="small" color="warning" />
                </Grid>
              )}
              {recipe.veryHealthy && (
                <Grid item>
                  <Chip label="건강식" size="small" color="info" />
                </Grid>
              )}
              {recipe.cheap && (
                <Grid item>
                  <Chip label="저렴한" size="small" color="secondary" />
                </Grid>
              )}
            </Grid>
          </Box>
        </Box>

        {/* 재료 */}
        {recipe.extendedIngredients && recipe.extendedIngredients.length > 0 && (
          <Box sx={{ mb: 3 }}>
            <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
              재료 ({recipe.extendedIngredients.length}개)
            </Typography>
            <Grid container spacing={2}>
              {recipe.extendedIngredients.map((ingredient, index) => (
                <Grid item xs={12} sm={6} key={index}>
                  <Box sx={{ 
                    p: 2, 
                    border: '1px solid #e0e0e0', 
                    borderRadius: 1,
                    backgroundColor: '#fafafa'
                  }}>
                    <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                      {ingredient.name}
                    </Typography>
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                      {ingredient.original}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {ingredient.measures?.metric?.amount}{ingredient.measures?.metric?.unitShort} 
                      {ingredient.measures?.us?.amount !== ingredient.measures?.metric?.amount && 
                        ` (${ingredient.measures?.us?.amount}${ingredient.measures?.us?.unitShort})`}
                    </Typography>
                    {ingredient.meta && ingredient.meta.length > 0 && (
                      <Box sx={{ mt: 1 }}>
                        {ingredient.meta.map((meta, metaIndex) => (
                          <Chip 
                            key={metaIndex} 
                            label={meta} 
                            size="small" 
                            variant="outlined" 
                            sx={{ mr: 0.5, mb: 0.5 }} 
                          />
                        ))}
                      </Box>
                    )}
                  </Box>
                </Grid>
              ))}
            </Grid>
          </Box>
        )}

        {/* 조리법 */}
        {recipe.analyzedInstructions && recipe.analyzedInstructions.length > 0 ? (
          <Box>
            <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
              조리법
            </Typography>
            {recipe.analyzedInstructions.map((instructionGroup: AnalyzedInstructionGroup, groupIndex: number) => (
              <Box key={groupIndex}>
                {instructionGroup.name && (
                  <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 'bold' }}>
                    {instructionGroup.name}
                  </Typography>
                )}
                <List>
                  {instructionGroup.steps.map((step: AnalyzedInstructionStep, stepIndex: number) => (
                    <ListItem key={stepIndex} sx={{ py: 1, alignItems: 'flex-start' }}>
                      <ListItemText
                        primary={
                          <Box>
                            <Typography variant="body2" sx={{ lineHeight: 1.6, mb: 1 }}>
                              <strong>{step.number}.</strong> {step.step}
                            </Typography>
                            {step.ingredients && step.ingredients.length > 0 && (
                              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                                재료: {step.ingredients.map((ing: { localizedName?: string; name: string }) => ing.localizedName || ing.name).join(', ')}
                              </Typography>
                            )}
                            {step.equipment && step.equipment.length > 0 && (
                              <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                                도구: {step.equipment.map((eq: { localizedName?: string; name: string }) => eq.localizedName || eq.name).join(', ')}
                              </Typography>
                            )}
                            {step.length && (
                              <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                                ⏱️ {step.length.number} {step.length.unit}
                              </Typography>
                            )}
                          </Box>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              </Box>
            ))}
          </Box>
        ) : recipe.instructions ? (
          <Box>
            <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
              조리법
            </Typography>
            {Array.isArray(recipe.instructions) ? (
              <List>
                {recipe.instructions.map((instruction, index) => (
                  <ListItem key={index} sx={{ py: 1 }}>
                    <ListItemText
                      primary={
                        <Typography variant="body2" sx={{ lineHeight: 1.6 }}>
                          <strong>{instruction.number || index + 1}.</strong> {instruction.step}
                        </Typography>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            ) : (
              <Typography variant="body2" sx={{ lineHeight: 1.6, whiteSpace: 'pre-line' }}>
                {recipe.instructions}
              </Typography>
            )}
          </Box>
        ) : null}

        {/* 영양 정보 */}
        {recipe.nutrition && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
              영양 정보
            </Typography>
            <Grid container spacing={2}>
              {recipe.nutrition.calories && (
                <Grid item xs={6} sm={3}>
                  <Typography variant="body2" color="text.secondary">
                    칼로리: {recipe.nutrition.calories}kcal
                  </Typography>
                </Grid>
              )}
              {recipe.nutrition.protein && (
                <Grid item xs={6} sm={3}>
                  <Typography variant="body2" color="text.secondary">
                    단백질: {recipe.nutrition.protein}g
                  </Typography>
                </Grid>
              )}
              {recipe.nutrition.fat && (
                <Grid item xs={6} sm={3}>
                  <Typography variant="body2" color="text.secondary">
                    지방: {recipe.nutrition.fat}g
                  </Typography>
                </Grid>
              )}
              {recipe.nutrition.carbohydrates && (
                <Grid item xs={6} sm={3}>
                  <Typography variant="body2" color="text.secondary">
                    탄수화물: {recipe.nutrition.carbohydrates}g
                  </Typography>
                </Grid>
              )}
            </Grid>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export const RecipeDetailCard = React.memo(RecipeDetailCardComponent); 