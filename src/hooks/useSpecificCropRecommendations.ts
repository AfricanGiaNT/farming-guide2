import { useQuery } from 'react-query'
import { cropAPI } from '../services/api'

export const useSpecificCropRecommendations = (
  cropName: string,
  lat: number,
  lon: number,
  season: 'current' | 'rainy' | 'dry' | 'all' = 'rainy',
  enabled: boolean = true
) => {
  return useQuery(
    ['specific-crop-recommendations', cropName, lat, lon, season],
    () => cropAPI.getSpecificCropRecommendations(cropName, lat, lon, season),
    {
      enabled: enabled && !!(cropName && lat && lon),
      staleTime: 30 * 60 * 1000, // 30 minutes
      cacheTime: 60 * 60 * 1000, // 1 hour
      retry: 2,
      onError: (error) => {
        console.error('Specific crop recommendations fetch error:', error)
      },
    }
  )
}