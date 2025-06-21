export interface Restaurant {
  id: string;
  name: string;
  logo_url: string;
  categories: string[];
  review_avg: number;
  review_count: number;
  delivery_fee_to_display: {
    basic: string;
  };
  address: string;
  keywords?: string[];
}

export interface TestResult {
  store: string;
  description: string;
  category: string;
  keywords: string[];
  logo_url: string;
}

export interface Location {
  lat: number;
  lng: number;
}

export interface Question {
  q: string;
  a: {
    answer: string;
    type: string;
  }[];
} 