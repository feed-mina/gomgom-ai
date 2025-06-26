export interface RecipeIngredient {
  name: string;
  amount?: string;
  unit?: string;
  price?: number;
}

export interface RecipeInstruction {
  step: string;
  number?: number;
}

export interface RecipeNutrition {
  calories?: number;
  protein?: number;
  fat?: number;
  carbohydrates?: number;
  fiber?: number;
}

export interface RecipeRecommendation {
  id?: number;
  title: string;
  summary?: string;
  image_url?: string;
  ingredients: RecipeIngredient[];
  instructions: RecipeInstruction[];
  nutrition?: RecipeNutrition;
  cooking_time?: number;
  servings?: number;
  difficulty?: string;
  source: string;
  total_cost?: number;
  currency: string;
}

export interface RecipeSearchRequest {
  query: string;
  number: number;
  include_price: boolean;
  max_cooking_time?: number;
  cuisine_type?: string;
}

export interface RecipeSearchResponse {
  query: string;
  total_results: number;
  recipes: RecipeRecommendation[];
  estimated_total_cost?: number;
  currency: string;
} 