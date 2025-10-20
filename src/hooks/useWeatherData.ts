import { useQuery } from 'react-query'
import { weatherAPI } from '../services/api'

export const useWeatherData = (lat: number, lon: number) => {
  return useQuery(
    ['weather', lat, lon],
    () => weatherAPI.getCurrentWeather(lat, lon),
    {
      enabled: !!(lat && lon),
      staleTime: 10 * 60 * 1000, // 10 minutes
      cacheTime: 30 * 60 * 1000, // 30 minutes
      retry: 2,
      onError: (error) => {
        console.error('Weather data fetch error:', error)
      },
    }
  )
}

export const useWeatherForecast = (lat: number, lon: number) => {
  return useQuery(
    ['weather-forecast', lat, lon],
    () => weatherAPI.getWeatherForecast(lat, lon),
    {
      enabled: !!(lat && lon),
      staleTime: 60 * 60 * 1000, // 1 hour
      cacheTime: 2 * 60 * 60 * 1000, // 2 hours
      retry: 2,
    }
  )
}

export const useRainfallData = (lat: number, lon: number) => {
  return useQuery(
    ['rainfall', lat, lon],
    () => weatherAPI.getRainfallData(lat, lon),
    {
      enabled: !!(lat && lon),
      staleTime: 30 * 60 * 1000, // 30 minutes
      cacheTime: 60 * 60 * 1000, // 1 hour
      retry: 2,
    }
  )
}

export const useHistoricalWeather = (lat: number, lon: number, yearsOrList: number | number[] = 5, shouldFetch: boolean = true) => {
  return useQuery(
    ['historical-weather', lat, lon, yearsOrList],
    () => weatherAPI.getHistoricalWeather(lat, lon, yearsOrList),
    {
      enabled: !!(lat && lon && shouldFetch),
      staleTime: 24 * 60 * 60 * 1000, // 24 hours
      cacheTime: 7 * 24 * 60 * 60 * 1000, // 7 days
      retry: 1,
    }
  )
}