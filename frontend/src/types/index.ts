// Core application types
export interface Location {
  name: string;
  latitude: number;
  longitude: number;
  district: string;
}

export interface WeatherData {
  location: string;
  current: {
    temperature: number;
    humidity: number;
    rainfall: number;
    description: string;
    windSpeed: number;
    uvIndex: number;
  };
  forecast: DailyForecast[];
}

export interface DailyForecast {
  date: string;
  tempHigh: number;
  tempLow: number;
  rainChance: number;
  rainfall: number;
  description: string;
  icon: string;
}

export interface CropRecommendation {
  crop: string;
  score: number;
  varieties: string[];
  plantingTime: string;
  yieldPotential: string;
  requirements: {
    rainfall: string;
    soil: string;
    temperature: string;
  };
  benefits: string[];
}

export interface CropVariety {
  id: string;
  name: string;
  crop: string;
  description: string;
  maturityDays: number;
  yieldPotential: string;
  diseaseResistance: string[];
  characteristics: string[];
  recommendations: string[];
}

export interface SearchResult {
  id: string;
  title: string;
  category: string;
  excerpt: string;
  content: string;
  tags: string[];
  relevanceScore: number;
}

export type Season = 'rainy' | 'dry' | 'cold';
export type SearchCategory = 'all' | 'crops' | 'pests' | 'soil' | 'weather' | 'markets';