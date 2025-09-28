/**
 * Hook for fetching specific crop recommendations
 * Implements Phase 4: Specific Crop Search Integration
 */

import { useQuery } from '@tanstack/react-query'
import { cropAPI } from '../services/api'

export interface UseSpecificCropRecommendationsParams {
  cropName: string
  lat: number
  lon: number
  season: 'current' | 'rainy' | 'dry' | 'all'
  enabled?: boolean
}

export const useSpecificCropRecommendations = ({
  cropName,
  lat,
  lon,
  season,
  enabled = true
}: UseSpecificCropRecommendationsParams) => {
  return useQuery({
    queryKey: ['specificCropRecommendations', cropName, lat, lon, season],
    queryFn: () => cropAPI.getSpecificCropRecommendations(cropName, lat, lon, season),
    enabled: enabled && !!cropName && !!lat && !!lon,
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
    retry: 2,
    retryDelay: 1000,
  })
}

export default useSpecificCropRecommendations
