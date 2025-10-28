/**
 * Utility for mapping display crop names to database crop names
 * This handles cases where the frontend displays a crop name differently than how it's stored in the database
 */

// Map of display names to database names
export const cropNameMap: Record<string, string> = {
  'phaseolus beans': 'beans',
  'phaseolus-beans': 'beans', // Add URL slug version
  'soyabean': 'soybean',
  'sweet potato': 'sweet_potato',
  'sweet-potato': 'sweet_potato', // Add URL slug version
  'leafy vegetables': 'leafy_vegetables',
  'leafy-vegetables': 'leafy_vegetables', // Add URL slug version
  // Add more mappings as needed
}

/**
 * Convert a display crop name to its database name
 * @param displayName The crop name as shown in the UI
 * @returns The corresponding database name
 */
export const displayToDatabaseName = (displayName: string): string => {
  const lowerCaseName = displayName.toLowerCase()
  return cropNameMap[lowerCaseName] || lowerCaseName
}

/**
 * Convert a database crop name to its display name
 * @param databaseName The crop name as stored in the database
 * @returns The corresponding display name
 */
export const databaseToDisplayName = (databaseName: string): string => {
  const entries = Object.entries(cropNameMap)
  const matchingEntry = entries.find(([_, dbName]) => dbName === databaseName.toLowerCase())
  return matchingEntry ? matchingEntry[0] : databaseName
}