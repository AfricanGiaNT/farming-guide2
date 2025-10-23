import { useQuery } from 'react-query'
import { cropAPI } from '../services/api'
import { displayToDatabaseName } from '../utils/cropNameMapping'

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
  // Convert display crop name to database name
  const databaseCropName = displayToDatabaseName(cropName)
  
  return useQuery(
    ['variety-info', cropName, databaseCropName, lat, lon],
    () => cropAPI.getVarietyInformation(databaseCropName, lat, lon),
    {
      enabled: !!cropName,
      staleTime: 60 * 60 * 1000, // 1 hour
      cacheTime: 24 * 60 * 60 * 1000, // 24 hours
      retry: 2,
    }
  )
}

export const usePlantingCalendar = (cropName: string, lat: number, lon: number) => {
  // Convert display crop name to database name
  const databaseCropName = displayToDatabaseName(cropName)
  
  return useQuery(
    ['planting-calendar', cropName, databaseCropName, lat, lon],
    () => cropAPI.getPlantingCalendar(databaseCropName, lat, lon),
    {
      enabled: !!(cropName && lat && lon),
      staleTime: 24 * 60 * 60 * 1000, // 24 hours
      cacheTime: 7 * 24 * 60 * 60 * 1000, // 7 days
      retry: 1,
    }
  )
}

export const useYieldPrediction = (cropName: string, lat: number, lon: number) => {
  // Convert display crop name to database name
  const databaseCropName = displayToDatabaseName(cropName)
  
  return useQuery(
    ['yield-prediction', cropName, databaseCropName, lat, lon],
    () => cropAPI.getYieldPrediction(databaseCropName, lat, lon),
    {
      enabled: !!(cropName && lat && lon),
      staleTime: 60 * 60 * 1000, // 1 hour
      cacheTime: 24 * 60 * 60 * 1000, // 24 hours
      retry: 1,
    }
  )
}