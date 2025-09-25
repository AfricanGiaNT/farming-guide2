import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface WeatherData {
  temperature: number
  humidity: number
  pressure: number
  weather: string
  windSpeed: number
  rainfall: number
  location: string
  timestamp: string
}

interface RainfallData {
  current: number
  forecast7Day: number
  rainyDays: number
  seasonal: number
  status: 'deficit' | 'below_normal' | 'normal' | 'above_normal' | 'excess'
}

interface WeatherForecast {
  date: string
  temperature: {
    min: number
    max: number
  }
  rainfall: number
  weather: string
  humidity: number
}

interface WeatherState {
  current: WeatherData | null
  rainfall: RainfallData | null
  forecast: WeatherForecast[]
  historical: {
    monthlyAverages: Record<string, number>
    climateTrend: 'increasing' | 'decreasing' | 'stable'
    droughtYears: number[]
    floodYears: number[]
    variability: number
  } | null
  loading: boolean
  error: string | null
  lastUpdated: string | null
}

const initialState: WeatherState = {
  current: null,
  rainfall: null,
  forecast: [],
  historical: null,
  loading: false,
  error: null,
  lastUpdated: null,
}

const weatherSlice = createSlice({
  name: 'weather',
  initialState,
  reducers: {
    setWeatherLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload
      if (action.payload) {
        state.error = null
      }
    },
    setCurrentWeather: (state, action: PayloadAction<WeatherData>) => {
      state.current = action.payload
      state.lastUpdated = new Date().toISOString()
    },
    setRainfallData: (state, action: PayloadAction<RainfallData>) => {
      state.rainfall = action.payload
    },
    setWeatherForecast: (state, action: PayloadAction<WeatherForecast[]>) => {
      state.forecast = action.payload
    },
    setHistoricalData: (state, action: PayloadAction<WeatherState['historical']>) => {
      state.historical = action.payload
    },
    setWeatherError: (state, action: PayloadAction<string>) => {
      state.error = action.payload
      state.loading = false
    },
    clearWeatherError: (state) => {
      state.error = null
    },
  },
})

export const {
  setWeatherLoading,
  setCurrentWeather,
  setRainfallData,
  setWeatherForecast,
  setHistoricalData,
  setWeatherError,
  clearWeatherError,
} = weatherSlice.actions

export default weatherSlice.reducer