import { createTransform } from 'redux-persist'
import storage from 'redux-persist/lib/storage'

/**
 * Custom storage engine for redux-persist with 12-hour expiration
 * Wraps localStorage with timestamp checking
 */
const CACHE_DURATION = 12 * 60 * 60 * 1000 // 12 hours in milliseconds
const TIMESTAMP_SUFFIX = '_timestamp'

// Wrapper around redux-persist's localStorage storage
const expiringStorage = {
  getItem: async (key: string): Promise<string | null> => {
    try {
      // Get the stored item using redux-persist's storage
      const item = await storage.getItem(key)
      if (!item) {
        return null
      }

      // Check timestamp from localStorage
      const timestampStr = localStorage.getItem(`${key}${TIMESTAMP_SUFFIX}`)
      if (!timestampStr) {
        // No timestamp means old format, treat as expired
        await storage.removeItem(key)
        return null
      }

      const timestamp = parseInt(timestampStr, 10)
      const now = Date.now()
      const age = now - timestamp

      // Check if cache is expired
      if (age > CACHE_DURATION) {
        console.log(`Cache expired for ${key}, age: ${Math.round(age / 1000 / 60)} minutes`)
        await storage.removeItem(key)
        localStorage.removeItem(`${key}${TIMESTAMP_SUFFIX}`)
        return null
      }

      console.log(`Cache hit for ${key}, age: ${Math.round(age / 1000 / 60)} minutes`)
      return item
    } catch (error) {
      console.error('Error getting cache:', error)
      return null
    }
  },

  setItem: async (key: string, value: string): Promise<void> => {
    try {
      await storage.setItem(key, value)
      // Store timestamp separately in localStorage
      localStorage.setItem(`${key}${TIMESTAMP_SUFFIX}`, Date.now().toString())
    } catch (error) {
      console.error('Error setting cache:', error)
      throw error
    }
  },

  removeItem: async (key: string): Promise<void> => {
    try {
      await storage.removeItem(key)
      localStorage.removeItem(`${key}${TIMESTAMP_SUFFIX}`)
    } catch (error) {
      console.error('Error removing cache:', error)
      throw error
    }
  },
}

export const createExpiringStorage = () => expiringStorage

/**
 * Transform to handle nested state persistence
 * Filters out loading states and errors to prevent stale UI states
 * Applied to all persisted slices
 */
export const persistTransform = createTransform(
  // Transform state on its way to being serialized and persisted
  (inboundState: any) => {
    // Remove loading and error states as they shouldn't be persisted
    if (!inboundState) return inboundState
    const { loading, error, ...rest } = inboundState
    return rest
  },
  // Transform state being rehydrated
  (outboundState: any) => {
    // Restore default loading/error states
    if (!outboundState) return outboundState
    return {
      ...outboundState,
      loading: false,
      error: null,
    }
  }
)

/**
 * Manually clear expired cache entries
 */
export const clearExpiredCache = (): void => {
  try {
    const keys = Object.keys(localStorage)
    const now = Date.now()
    let cleared = 0

    keys.forEach((key) => {
      // Only check persist keys, skip timestamp keys
      if (key.startsWith('persist:') && !key.endsWith(TIMESTAMP_SUFFIX)) {
        try {
          const timestampStr = localStorage.getItem(`${key}${TIMESTAMP_SUFFIX}`)
          if (!timestampStr) {
            // Old format or corrupted, remove it
            localStorage.removeItem(key)
            cleared++
            return
          }

          const timestamp = parseInt(timestampStr, 10)
          const age = now - timestamp

          if (age > CACHE_DURATION) {
            localStorage.removeItem(key)
            localStorage.removeItem(`${key}${TIMESTAMP_SUFFIX}`)
            cleared++
          }
        } catch (error) {
          // If parsing fails, remove the corrupted entry
          localStorage.removeItem(key)
          localStorage.removeItem(`${key}${TIMESTAMP_SUFFIX}`)
          cleared++
        }
      }
    })

    if (cleared > 0) {
      console.log(`Cleared ${cleared} expired cache entries`)
    }
  } catch (error) {
    console.error('Error clearing expired cache:', error)
  }
}

/**
 * Clear all persisted cache
 */
export const clearAllCache = (): void => {
  try {
    const keys = Object.keys(localStorage)
    keys.forEach((key) => {
      if (key.startsWith('persist:') || key.endsWith(TIMESTAMP_SUFFIX)) {
        localStorage.removeItem(key)
      }
    })
    console.log('All cache cleared')
  } catch (error) {
    console.error('Error clearing all cache:', error)
  }
}
