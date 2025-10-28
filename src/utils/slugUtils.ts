/**
 * Utility for creating URL-safe slugs from names
 */

/**
 * Convert a name to a URL-safe slug
 * @param name The name to convert
 * @returns A URL-safe slug
 */
export const createSlug = (name: string): string => {
  return name.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '')
}

/**
 * Convert a slug back to a display name (approximate)
 * @param slug The slug to convert
 * @returns A display-friendly name
 */
export const slugToDisplayName = (slug: string): string => {
  return slug.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}


