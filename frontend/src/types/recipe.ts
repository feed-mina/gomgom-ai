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

export interface AnalyzedInstructionStep {
  number: number;
  step: string;
  ingredients?: Array<{
    id: number;
    name: string;
    localizedName?: string;
    image?: string;
  }>;
  equipment?: Array<{
    id: number;
    name: string;
    localizedName?: string;
    image?: string;
  }>;
  length?: {
    number: number;
    unit: string;
  };
}

export interface AnalyzedInstructionGroup {
  name?: string;
  steps: AnalyzedInstructionStep[];
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
  image?: string;
  readyInMinutes?: number;
  cuisines?: string[];
  dishTypes?: string[];
  diets?: string[];
  extendedIngredients?: ExtendedIngredient[];
  sourceName?: string;
  sourceUrl?: string;
  ingredients?: RecipeIngredient[];
  instructions?: RecipeInstruction[] | string;
  analyzedInstructions?: AnalyzedInstructionGroup[];
  nutrition?: RecipeNutrition;
  cooking_time?: number;
  servings?: number;
  difficulty?: string;
  source: string;
  total_cost?: number;
  currency: string;
  pricePerServing?: number;
  aggregateLikes?: number;
  vegetarian?: boolean;
  vegan?: boolean;
  glutenFree?: boolean;
  dairyFree?: boolean;
  veryHealthy?: boolean;
  cheap?: boolean;
  [key: string]: any;
}

export interface ExtendedIngredient {
  id: number;
  aisle?: string;
  image?: string;
  consistency?: string;
  name: string;
  nameClean?: string;
  original: string;
  originalName?: string;
  amount: number;
  unit: string;
  meta?: string[];
  measures?: {
    us?: {
      amount: number;
      unitShort: string;
      unitLong: string;
    };
    metric?: {
      amount: number;
      unitShort: string;
      unitLong: string;
    };
  };
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

const tagMap: Record<string, string> = {
  // cuisines
  Chinese: '중식',
  Asian: '아시아',
  // dishTypes
  'main course': '메인 코스',
  'side dish': '사이드',
  lunch: '점심',
  dinner: '저녁',
  // diets
  'gluten free': '글루텐 프리',
  'dairy free': '유제품 프리',
  vegetarian: '채식',
  vegan: '비건',
  // ...필요한 만큼 추가
};

function translateTag(tag: string) {
  return tagMap[tag] || tag;
} 