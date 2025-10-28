/**
 * Debug utilities for cache inspection
 */

export const inspectCache = () => {
  console.log('=== Cache Inspection ===')
  
  // Check all persist keys
  const persistKeys = Object.keys(localStorage).filter(key => key.startsWith('persist:'))
  console.log(`Found ${persistKeys.length} persist keys:`, persistKeys)
  
  // Check root cache
  const rootCache = localStorage.getItem('persist:root')
  const rootTimestamp = localStorage.getItem('persist:root_timestamp')
  
  if (rootCache) {
    console.log('Root cache exists:', rootCache.substring(0, 100) + '...')
    if (rootTimestamp) {
      const age = Date.now() - parseInt(rootTimestamp, 10)
      console.log(`Cache age: ${Math.round(age / 1000 / 60)} minutes`)
    } else {
      console.log('⚠️ No timestamp found - cache may be old format')
    }
  } else {
    console.log('❌ No root cache found')
  }
  
  // Check individual slice caches
  const slices = ['user', 'weather', 'crop', 'knowledge']
  slices.forEach(slice => {
    const sliceCache = localStorage.getItem(`persist:${slice}`)
    if (sliceCache) {
      console.log(`✓ ${slice} cache exists (${sliceCache.length} chars)`)
    } else {
      console.log(`✗ ${slice} cache NOT found`)
    }
  })
  
  console.log('=== End Cache Inspection ===')
}

export const clearAllCacheDebug = () => {
  console.log('Clearing all cache...')
  const keys = Object.keys(localStorage)
  let cleared = 0
  keys.forEach(key => {
    if (key.startsWith('persist:') || key.endsWith('_timestamp')) {
      localStorage.removeItem(key)
      cleared++
    }
  })
  console.log(`Cleared ${cleared} cache entries`)
}

