import { useCallback, useEffect, useState } from 'react'
import { persistor } from '../store/store'
import { clearExpiredCache, clearAllCache } from '../utils/persistentStorage'

/**
 * Hook for cache management
 * Provides utilities to check cache status and clear cache
 */
export const useCache = () => {
  const [isRehydrated, setIsRehydrated] = useState(false)

  useEffect(() => {
    // Check if rehydration is complete
    const unsubscribe = persistor.subscribe(() => {
      if (persistor.getState().bootstrapped) {
        setIsRehydrated(true)
      }
    })

    return unsubscribe
  }, [])

  /**
   * Clear all persisted cache
   */
  const clearCache = useCallback(async () => {
    try {
      await persistor.purge()
      clearAllCache()
      // Reload to reset state
      window.location.reload()
    } catch (error) {
      console.error('Error clearing cache:', error)
    }
  }, [])

  /**
   * Clear expired cache entries
   */
  const clearExpired = useCallback(() => {
    clearExpiredCache()
  }, [])

  /**
   * Get cache age for debugging
   */
  const getCacheAge = useCallback((): number | null => {
    try {
      const timestampStr = localStorage.getItem('persist:root_timestamp')
      if (!timestampStr) return null

      const timestamp = parseInt(timestampStr, 10)
      return Date.now() - timestamp
    } catch (error) {
      console.error('Error getting cache age:', error)
      return null
    }
  }, [])

  return {
    isRehydrated,
    clearCache,
    clearExpired,
    getCacheAge,
  }
}

