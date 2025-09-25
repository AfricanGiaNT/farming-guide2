import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface CropVariety {
  name: string
  type: string
  maturityDays: number
  yieldPotential: 'high' | 'moderate' | 'low'
  droughtTolerance: 'excellent' | 'good' | 'moderate' | 'poor'
  diseaseResistance: string[]
}

interface CropRecommendation {
  cropId: string
  cropName: string
  totalScore: number
  suitabilityLevel: 'excellent' | 'very_good' | 'good' | 'fair' | 'poor'
  scoreComponents: {
    rainfallScore: number
    temperatureScore: number
    seasonalScore: number
    humidityScore: number
    timingScore: number
    droughtToleranceScore: number
    soilSuitabilityScore: number
    marketDemandScore: number
    inputAvailabilityScore: number
    climateTrendScore: number
  }
  reasons: string[]
  varieties: CropVariety[]
  confidenceScore: number
  confidenceLevel: 'high' | 'medium' | 'low'
}

interface PlantingCalendar {
  cropName: string
  bestPlantingMonth: string
  alternativeMonths: string[]
  avoidMonths: string[]
  monthlyRecommendations: Record<string, {
    recommendationType: 'optimal' | 'alternative' | 'avoid'
    activities: string[]
    advice: string
  }>
  riskAssessment: {
    droughtRisk: {
      level: 'low' | 'medium' | 'high'
      probability: number
    }
    floodRisk: {
      level: 'low' | 'medium' | 'high'
      probability: number
    }
    overallRiskLevel: 'low' | 'medium' | 'high'
    mitigationStrategies: string[]
  }
}

interface CropState {
  recommendations: CropRecommendation[]
  selectedSeason: 'current' | 'rainy' | 'dry' | 'all'
  plantingCalendar: PlantingCalendar | null
  varietyDetails: {
    [cropName: string]: {
      varieties: CropVariety[]
      weatherSuitability: Record<string, number>
      plantingAdvice: string[]
    }
  }
  loading: boolean
  error: string | null
  lastLocation: { lat: number; lon: number } | null
}

const initialState: CropState = {
  recommendations: [],
  selectedSeason: 'current',
  plantingCalendar: null,
  varietyDetails: {},
  loading: false,
  error: null,
  lastLocation: null,
}

const cropSlice = createSlice({
  name: 'crop',
  initialState,
  reducers: {
    setCropLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload
      if (action.payload) {
        state.error = null
      }
    },
    setCropRecommendations: (state, action: PayloadAction<CropRecommendation[]>) => {
      state.recommendations = action.payload
    },
    setSelectedSeason: (state, action: PayloadAction<CropState['selectedSeason']>) => {
      state.selectedSeason = action.payload
    },
    setPlantingCalendar: (state, action: PayloadAction<PlantingCalendar>) => {
      state.plantingCalendar = action.payload
    },
    setVarietyDetails: (state, action: PayloadAction<{
      cropName: string
      details: CropState['varietyDetails'][string]
    }>) => {
      state.varietyDetails[action.payload.cropName] = action.payload.details
    },
    setCropError: (state, action: PayloadAction<string>) => {
      state.error = action.payload
      state.loading = false
    },
    clearCropError: (state) => {
      state.error = null
    },
    setLastLocation: (state, action: PayloadAction<{ lat: number; lon: number }>) => {
      state.lastLocation = action.payload
    },
  },
})

export const {
  setCropLoading,
  setCropRecommendations,
  setSelectedSeason,
  setPlantingCalendar,
  setVarietyDetails,
  setCropError,
  clearCropError,
  setLastLocation,
} = cropSlice.actions

export default cropSlice.reducer