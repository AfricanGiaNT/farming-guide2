import { useState, useEffect } from 'react'

// API service function for variety information
const getVarietyInformation = async (cropName: string, lat?: number, lon?: number) => {
  const params = new URLSearchParams()
  if (lat && lon) {
    params.append('lat', lat.toString())
    params.append('lon', lon.toString())
  }
  const queryString = params.toString()
  // Use Replit domain if available, otherwise localhost for development
  const getApiBase = () => {
    if (typeof window !== 'undefined' && window.location.hostname.includes('replit.dev')) {
      return `https://${window.location.hostname}:8000/api`;
    }
    return 'http://localhost:8000/api';
  };
  const url = `${getApiBase()}/varieties/${cropName}${queryString ? `?${queryString}` : ''}`
  
  const response = await fetch(url)
  if (!response.ok) {
    throw new Error('Failed to fetch variety information')
  }
  return response.json()
}

export const useVarietyInformation = (cropName: string, lat?: number, lon?: number) => {
  const [data, setData] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    if (!cropName) {
      setData(null)
      setError(null)
      return
    }

    setIsLoading(true)
    setError(null)

    getVarietyInformation(cropName, lat, lon)
      .then(result => {
        setData(result)
      })
      .catch(err => {
        setError(err)
      })
      .finally(() => {
        setIsLoading(false)
      })
  }, [cropName, lat, lon])

  return { data, isLoading, error }
}
