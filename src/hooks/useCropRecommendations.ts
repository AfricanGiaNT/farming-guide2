import { useQuery } from 'react-query'
import { cropAPI } from '../services/api'

export const useCropRecommendations = (
  lat: number, 
  lon: number, 
  season: 'current' | 'rainy' | 'dry' | 'all' = 'current'
) => {
  return useQuery(
    ['crop-recommendations', lat, lon, season],
    () => cropAPI.getCropRecommendations(lat, lon, season),
    {
      enabled: !!(lat && lon),
      staleTime: 30 * 60 * 1000, // 30 minutes
      cacheTime: 60 * 60 * 1000, // 1 hour
      retry: 2,
      onError: (error) => {
        console.error('Crop recommendations fetch error:', error)
      },
    }
  )
}

export const useVarietyInformation = (cropName: string, lat?: number, lon?: number) => {
  return useQuery(
    ['variety-info', cropName, lat, lon],
    () => cropAPI.getVarietyInformation(cropName, lat, lon),
    {
      enabled: !!cropName,
      staleTime: 60 * 60 * 1000, // 1 hour
      cacheTime: 24 * 60 * 60 * 1000, // 24 hours
      retry: 2,
    }
  )
}

export const usePlantingCalendar = (cropName: string, lat: number, lon: number) => {
  return useQuery(
    ['planting-calendar', cropName, lat, lon],
    () => cropAPI.getPlantingCalendar(cropName, lat, lon),
    {
      enabled: !!(cropName && lat && lon),
      staleTime: 24 * 60 * 60 * 1000, // 24 hours
      cacheTime: 7 * 24 * 60 * 60 * 1000, // 7 days
      retry: 1,
    }
  )
}

export const useYieldPrediction = (cropName: string, lat: number, lon: number) => {
  return useQuery(
    ['yield-prediction', cropName, lat, lon],
    () => cropAPI.getYieldPrediction(cropName, lat, lon),
    {
      enabled: !!(cropName && lat && lon),
      staleTime: 60 * 60 * 1000, // 1 hour
      cacheTime: 24 * 60 * 60 * 1000, // 24 hours
      retry: 1,
    }
  )
}