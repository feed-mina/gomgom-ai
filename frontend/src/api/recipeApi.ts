import axios from 'axios';
import { RecipeSearchRequest, RecipeSearchResponse } from '../types/recipe';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;
if (!API_BASE_URL) {
  throw new Error('NEXT_PUBLIC_API_URL is not defined');
}

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const recipeApi = {
  // 레시피 검색
  searchRecipes: async (params: {
    query: string;
    number?: number;
    include_price?: boolean;
    max_cooking_time?: number;
    cuisine_type?: string;
  }): Promise<RecipeSearchResponse> => {
    const response = await api.get('/api/v1/recommendations/search', { params });
    return response.data;
  },

  // POST로 레시피 검색
  searchRecipesPost: async (request: RecipeSearchRequest): Promise<RecipeSearchResponse> => {
    const response = await api.post('/api/v1/recommendations/search', request);
    return response.data;
  },

  // API 상태 확인
  healthCheck: async () => {
    const response = await api.get('/api/v1/recommendations/health');
    console.log('healthCheck', response.data);
    return response.data;
  },

  getRecipeById: async (id: number | string, source?: string, translate: boolean = false) => {
    // 한식인 경우 internal 엔드포인트 사용, 그 외에는 external 엔드포인트 사용
    const endpoint = source === 'KoreanRecipeCrawler' ? 'internal' : 'external';
    const params = translate ? { translate: 'true' } : {};
    const response = await api.get(`/api/v1/recipes/${endpoint}/${id}`, { params });
    return response.data;
  },
}; 