# Caching System Documentation

## Overview

The application implements a comprehensive 12-hour caching system using Redux Persist with a custom expiration mechanism. This ensures that users can navigate between pages without losing their data or information.

## Architecture

### Components

1. **Custom Storage Engine** (`src/utils/persistentStorage.ts`)
   - Wraps localStorage with 12-hour expiration
   - Automatically removes expired cache entries
   - Provides utilities for cache management

2. **Redux Persist Configuration** (`src/store/store.ts`)
   - Persists user, weather, crop, and knowledge slices
   - Uses custom expiring storage
   - Filters out loading/error states during persistence

3. **PersistGate** (`src/main.tsx`)
   - Handles rehydration of persisted state
   - Shows loading screen during cache restoration
   - Clears expired cache on app startup

4. **Cache Management Hook** (`src/hooks/useCache.ts`)
   - Provides utilities for cache operations
   - Allows manual cache clearing
   - Tracks rehydration status

## Cached Data

The following Redux slices are persisted for 12 hours:

- **User State**: Location, profile, preferences, authentication status
- **Weather State**: Current weather, forecast, rainfall data, historical data
- **Crop State**: Recommendations, selected season, planting calendar, variety details
- **Knowledge State**: Search results, search history, bookmarks, filters

## Cache Expiration

- **Duration**: 12 hours (43,200,000 milliseconds)
- **Automatic Cleanup**: Expired entries are cleared on app startup
- **Manual Cleanup**: Use `clearExpiredCache()` or `clearAllCache()` utilities

## Usage

### Accessing Cache Status

```typescript
import { useCache } from '../hooks/useCache'

function MyComponent() {
  const { isRehydrated, getCacheAge, clearCache } = useCache()
  
  // Check if cache is loaded
  if (!isRehydrated) {
    return <div>Loading cached data...</div>
  }
  
  // Get cache age in milliseconds
  const cacheAge = getCacheAge()
  
  // Clear cache manually (will reload the page)
  const handleClearCache = () => {
    clearCache()
  }
}
```

### Manual Cache Clearing

```typescript
import { clearAllCache, clearExpiredCache } from '../utils/persistentStorage'

// Clear only expired entries
clearExpiredCache()

// Clear all cache
clearAllCache()
```

## How It Works

1. **On Data Save**: When Redux state updates, Redux Persist:
   - Transforms state (removes loading/error states)
   - Serializes to JSON string
   - Wraps in timestamped object
   - Saves to localStorage with `persist:root` key

2. **On App Load**: 
   - PersistGate waits for cache rehydration
   - Custom storage checks expiration
   - If expired, returns null (fresh state)
   - If valid, returns cached data
   - Redux state is restored from cache

3. **On Navigation**: 
   - All persisted slices remain in Redux store
   - Components read from Redux (already cached)
   - No API calls needed for cached data
   - React Query also uses 12-hour cache for API responses

## Configuration

### Changing Cache Duration

Edit `CACHE_DURATION` in `src/utils/persistentStorage.ts`:

```typescript
const CACHE_DURATION = 12 * 60 * 60 * 1000 // Change this value
```

### Excluding Slices from Persistence

Edit the `whitelist` in `src/store/store.ts`:

```typescript
const persistConfig = {
  key: 'root',
  storage: expiringStorage,
  whitelist: ['user', 'weather', 'crop', 'knowledge'], // Remove slices here
  transforms: [persistTransform],
}
```

### React Query Cache

React Query cache duration is synchronized with Redux Persist (12 hours) in `src/main.tsx`:

```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 12 * 60 * 60 * 1000, // 12 hours
      cacheTime: 12 * 60 * 60 * 1000, // 12 hours
    },
  },
})
```

## Benefits

1. **Offline Navigation**: Users can browse cached data without internet
2. **Performance**: Instant page loads from cache
3. **Data Persistence**: User selections and preferences survive page reloads
4. **Bandwidth Savings**: Reduces API calls for frequently accessed data
5. **Automatic Expiration**: Ensures data freshness with 12-hour TTL

## Debugging

To inspect cached data in browser console:

```javascript
// View all cached data
localStorage.getItem('persist:root')

// Check cache age
const cached = JSON.parse(localStorage.getItem('persist:root'))
const age = Date.now() - cached.timestamp
console.log(`Cache age: ${Math.round(age / 1000 / 60)} minutes`)

// Clear cache
localStorage.removeItem('persist:root')
```

## Known Limitations

1. Cache is limited by localStorage size (~5-10MB typically)
2. Expired cache is only cleared on app startup
3. Manual cache clearing requires page reload
4. Loading/error states are not persisted (intentional)

