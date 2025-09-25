import { WeatherData, CropRecommendation, CropVariety, SearchResult } from '../types';

export const mockWeatherData: WeatherData = {
  location: "Lilongwe",
  current: {
    temperature: 28,
    humidity: 65,
    rainfall: 0,
    description: "Partly cloudy",
    windSpeed: 12,
    uvIndex: 7
  },
  forecast: [
    { date: "2025-01-26", tempHigh: 30, tempLow: 18, rainChance: 20, rainfall: 0, description: "Sunny", icon: "sun" },
    { date: "2025-01-27", tempHigh: 32, tempLow: 19, rainChance: 10, rainfall: 0, description: "Clear", icon: "sun" },
    { date: "2025-01-28", tempHigh: 29, tempLow: 20, rainChance: 60, rainfall: 8, description: "Light Rain", icon: "cloud-rain" },
    { date: "2025-01-29", tempHigh: 26, tempLow: 18, rainChance: 80, rainfall: 15, description: "Heavy Rain", icon: "cloud-rain" },
    { date: "2025-01-30", tempHigh: 28, tempLow: 17, rainChance: 40, rainfall: 3, description: "Scattered Clouds", icon: "cloud" },
    { date: "2025-01-31", tempHigh: 31, tempLow: 19, rainChance: 15, rainfall: 0, description: "Mostly Sunny", icon: "sun" },
    { date: "2025-02-01", tempHigh: 33, tempLow: 21, rainChance: 5, rainfall: 0, description: "Hot & Sunny", icon: "sun" }
  ]
};

export const mockCropRecommendations: CropRecommendation[] = [
  {
    crop: "Maize",
    score: 85,
    varieties: ["SC627", "DK8053", "PAN4M-19"],
    plantingTime: "November-December",
    yieldPotential: "4-6 tons/ha",
    requirements: {
      rainfall: "500-800mm",
      soil: "Well-drained loam",
      temperature: "18-25°C"
    },
    benefits: ["High yield potential", "Drought tolerance", "Market demand"]
  },
  {
    crop: "Groundnuts",
    score: 78,
    varieties: ["CG7", "Nsinjiro", "Baka"],
    plantingTime: "November-January",
    yieldPotential: "1.5-2.5 tons/ha",
    requirements: {
      rainfall: "400-600mm",
      soil: "Sandy loam",
      temperature: "20-30°C"
    },
    benefits: ["Nitrogen fixation", "Cash crop", "Food security"]
  },
  {
    crop: "Soybeans",
    score: 72,
    varieties: ["Makwacha", "Ocepara-4", "TGx1987-62F"],
    plantingTime: "November-December",
    yieldPotential: "1.2-2.0 tons/ha",
    requirements: {
      rainfall: "450-700mm",
      soil: "Well-drained",
      temperature: "20-28°C"
    },
    benefits: ["Protein rich", "Soil improvement", "Export potential"]
  }
];

export const mockCropVarieties: CropVariety[] = [
  {
    id: "sc627",
    name: "SC627",
    crop: "Maize",
    description: "High-yielding hybrid maize variety with excellent drought tolerance",
    maturityDays: 120,
    yieldPotential: "5-7 tons/ha",
    diseaseResistance: ["Gray Leaf Spot", "Common Rust"],
    characteristics: ["Drought tolerant", "High yield", "Good grain quality"],
    recommendations: ["Plant at 75cm x 25cm spacing", "Apply NPK 23:21:0+4S at planting"]
  },
  {
    id: "nsinjiro",
    name: "Nsinjiro",
    crop: "Groundnuts",
    description: "Popular groundnut variety with good market acceptance",
    maturityDays: 90,
    yieldPotential: "1.8-2.5 tons/ha",
    diseaseResistance: ["Leaf spot", "Rust"],
    characteristics: ["Medium maturity", "Good taste", "Market preferred"],
    recommendations: ["Plant 30cm x 10cm spacing", "Harvest when leaves turn yellow"]
  }
];

export const mockSearchResults: SearchResult[] = [
  {
    id: "pest-management-1",
    title: "Fall Armyworm Control in Maize",
    category: "pests",
    excerpt: "Effective strategies for managing fall armyworm infestations in maize crops...",
    content: "Fall armyworm is a major pest affecting maize production in Malawi...",
    tags: ["fall armyworm", "maize", "pest control", "IPM"],
    relevanceScore: 95
  },
  {
    id: "soil-fertility-1",
    title: "Improving Soil Fertility with Organic Matter",
    category: "soil",
    excerpt: "Learn how to enhance soil fertility using locally available organic materials...",
    content: "Soil fertility is crucial for sustainable crop production...",
    tags: ["soil fertility", "organic matter", "composting"],
    relevanceScore: 88
  }
];

export const malawianDistricts = [
  "Blantyre", "Lilongwe", "Mzuzu", "Zomba", "Kasungu", "Mangochi", "Salima", 
  "Machinga", "Balaka", "Chiradzulu", "Nsanje", "Chikwawa", "Thyolo", "Mulanje",
  "Phalombe", "Mwanza", "Neno", "Dedza", "Ntcheu", "Dowa", "Mchinji", "Nkhotakota",
  "Ntchisi", "Rumphi", "Nkhata Bay", "Likoma", "Karonga", "Chitipa"
];