# Crop Name Mapping Implementation

## Problem
The frontend was using "phaseolus beans" as the display name for beans, but in the Supabase database, the crop is stored as simply "beans". This naming mismatch was causing the API to return no results when users searched for "phaseolus beans" varieties.

## Solution

### 1. Created a Crop Name Mapping Utility
Created a utility file (`src/utils/cropNameMapping.ts`) that:
- Maps display names to database names
- Provides functions to convert between display and database names
- Handles edge cases like "phaseolus beans" → "beans" and "soyabean" → "soybean"

### 2. Updated the Variety Information Hook
Modified `useVarietyInformation` in `src/hooks/useCropRecommendations.ts` to:
- Convert display crop names to database names before making API calls
- Keep the original crop name in the query cache key for proper caching
- Apply the same pattern to other crop-related hooks for consistency

### 3. Improved Error Handling
Enhanced error handling in the API service to:
- Provide better error messages for debugging
- Log detailed information about failed requests
- Properly propagate errors to the UI

## Implementation Details

### Crop Name Mapping Utility
```typescript
// src/utils/cropNameMapping.ts
export const cropNameMap: Record<string, string> = {
  'phaseolus beans': 'beans',
  'soyabean': 'soybean',
  'sweet potato': 'sweet_potato',
  'leafy vegetables': 'leafy_vegetables',
}

export const displayToDatabaseName = (displayName: string): string => {
  const lowerCaseName = displayName.toLowerCase()
  return cropNameMap[lowerCaseName] || lowerCaseName
}

export const databaseToDisplayName = (databaseName: string): string => {
  const entries = Object.entries(cropNameMap)
  const matchingEntry = entries.find(([_, dbName]) => dbName === databaseName.toLowerCase())
  return matchingEntry ? matchingEntry[0] : databaseName
}
```

### Updated Variety Information Hook
```typescript
// src/hooks/useCropRecommendations.ts
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
```

## Benefits

1. **Improved User Experience**: Users can now search for varieties using either the common or scientific names
2. **Consistent Data**: The frontend displays consistent crop names while the database maintains its naming convention
3. **Better Debugging**: Enhanced error handling makes it easier to diagnose API issues
4. **Extensibility**: Easy to add new crop name mappings as needed
5. **Maintainability**: Centralized mapping logic makes it easy to update or extend

## Future Improvements

1. **Fuzzy Matching**: Implement fuzzy matching for crop names to handle typos and variations
2. **Automated Mapping**: Generate mappings automatically based on database content
3. **Localization Support**: Add support for crop names in multiple languages
4. **Alias System**: Expand to support multiple aliases for each crop
5. **Admin Interface**: Create an admin interface to manage crop name mappings


