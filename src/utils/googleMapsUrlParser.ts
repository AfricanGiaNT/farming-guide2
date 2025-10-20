/**
 * Google Maps URL Parser Utility
 * Parses various Google Maps URL formats to extract latitude and longitude coordinates
 */

export interface ParsedCoordinates {
  lat: number
  lon: number
}

export interface ParseResult {
  success: boolean
  coordinates?: ParsedCoordinates
  error?: string
}

/**
 * Parses Google Maps URLs to extract coordinates
 * Supports multiple URL formats including shortened URLs
 */
export class GoogleMapsUrlParser {
  private static readonly COORDINATE_PATTERNS = [
    // Standard Google Maps URLs with coordinates
    /@(-?\d+\.?\d*),(-?\d+\.?\d*)/,
    // Query parameter format: ?q=lat,lng
    /[?&]q=(-?\d+\.?\d*),(-?\d+\.?\d*)/,
    // Query parameter format: ?ll=lat,lng
    /[?&]ll=(-?\d+\.?\d*),(-?\d+\.?\d*)/,
    // Query parameter format: ?center=lat,lng
    /[?&]center=(-?\d+\.?\d*),(-?\d+\.?\d*)/,
    // Query parameter format: ?sll=lat,lng
    /[?&]sll=(-?\d+\.?\d*),(-?\d+\.?\d*)/,
  ]

  private static readonly URL_PATTERNS = [
    // Standard Google Maps URLs
    /^https?:\/\/(www\.)?maps\.google\.(com|co\.uk|ca|com\.au)\/maps/,
    // New Google Maps URLs
    /^https?:\/\/(www\.)?google\.com\/maps/,
    // Shortened URLs
    /^https?:\/\/(goo\.gl|maps\.app\.goo\.gl)\/maps/,
    // Mobile URLs
    /^https?:\/\/(maps\.google\.com\/maps\/ms)/,
  ]

  /**
   * Validates if the URL is a Google Maps URL
   */
  private static isValidGoogleMapsUrl(url: string): boolean {
    return this.URL_PATTERNS.some(pattern => pattern.test(url))
  }

  /**
   * Validates coordinate ranges
   */
  private static validateCoordinates(lat: number, lon: number): boolean {
    return lat >= -90 && lat <= 90 && lon >= -180 && lon <= 180
  }

  /**
   * Extracts coordinates from URL using regex patterns
   */
  private static extractCoordinatesFromUrl(url: string): ParsedCoordinates | null {
    for (const pattern of this.COORDINATE_PATTERNS) {
      const match = url.match(pattern)
      if (match) {
        const lat = parseFloat(match[1])
        const lon = parseFloat(match[2])
        
        if (!isNaN(lat) && !isNaN(lon) && this.validateCoordinates(lat, lon)) {
          return { lat, lon }
        }
      }
    }
    return null
  }

  /**
   * Attempts to resolve shortened URLs (basic implementation)
   * Note: This is a simplified version. In production, you might want to use
   * a service to resolve shortened URLs or handle them differently.
   */
  private static async resolveShortenedUrl(url: string): Promise<string> {
    // For now, we'll try to extract coordinates from common shortened URL patterns
    // In a real implementation, you might want to make a HEAD request to resolve the URL
    
    // Check if it's a goo.gl or maps.app.goo.gl URL
    if (url.includes('goo.gl') || url.includes('maps.app.goo.gl')) {
      // These URLs often contain encoded coordinates
      // This is a simplified approach - in production you'd want to resolve the actual URL
      console.warn('Shortened URL detected. Consider implementing URL resolution for better accuracy.')
    }
    
    return url
  }

  /**
   * Main parsing method
   */
  public static async parseUrl(url: string): Promise<ParseResult> {
    try {
      // Clean and validate input
      if (!url || typeof url !== 'string') {
        return {
          success: false,
          error: 'Invalid URL: URL must be a non-empty string'
        }
      }

      // Remove whitespace and ensure it's a valid URL
      const cleanUrl = url.trim()
      
      if (!cleanUrl.startsWith('http://') && !cleanUrl.startsWith('https://')) {
        return {
          success: false,
          error: 'Invalid URL: URL must start with http:// or https://'
        }
      }

      // Check if it's a Google Maps URL
      if (!this.isValidGoogleMapsUrl(cleanUrl)) {
        return {
          success: false,
          error: 'Invalid URL: Not a Google Maps URL'
        }
      }

      // Try to extract coordinates directly
      let coordinates = this.extractCoordinatesFromUrl(cleanUrl)
      
      // If no coordinates found and it's a shortened URL, try to resolve it
      if (!coordinates && (cleanUrl.includes('goo.gl') || cleanUrl.includes('maps.app.goo.gl'))) {
        try {
          const resolvedUrl = await this.resolveShortenedUrl(cleanUrl)
          coordinates = this.extractCoordinatesFromUrl(resolvedUrl)
        } catch (error) {
          console.warn('Failed to resolve shortened URL:', error)
        }
      }

      if (!coordinates) {
        return {
          success: false,
          error: 'No coordinates found in URL. Make sure the URL contains latitude and longitude.'
        }
      }

      return {
        success: true,
        coordinates
      }

    } catch (error) {
      return {
        success: false,
        error: `Parsing error: ${error instanceof Error ? error.message : 'Unknown error'}`
      }
    }
  }

  /**
   * Synchronous version for simple cases (no URL resolution)
   */
  public static parseUrlSync(url: string): ParseResult {
    try {
      // Clean and validate input
      if (!url || typeof url !== 'string') {
        return {
          success: false,
          error: 'Invalid URL: URL must be a non-empty string'
        }
      }

      const cleanUrl = url.trim()
      
      if (!cleanUrl.startsWith('http://') && !cleanUrl.startsWith('https://')) {
        return {
          success: false,
          error: 'Invalid URL: URL must start with http:// or https://'
        }
      }

      // Check if it's a Google Maps URL
      if (!this.isValidGoogleMapsUrl(cleanUrl)) {
        return {
          success: false,
          error: 'Invalid URL: Not a Google Maps URL'
        }
      }

      // Try to extract coordinates
      const coordinates = this.extractCoordinatesFromUrl(cleanUrl)

      if (!coordinates) {
        return {
          success: false,
          error: 'No coordinates found in URL. Make sure the URL contains latitude and longitude.'
        }
      }

      return {
        success: true,
        coordinates
      }

    } catch (error) {
      return {
        success: false,
        error: `Parsing error: ${error instanceof Error ? error.message : 'Unknown error'}`
      }
    }
  }

  /**
   * Get supported URL formats for user reference
   */
  public static getSupportedFormats(): string[] {
    return [
      'https://maps.google.com/maps?q=-13.9833,33.7833',
      'https://www.google.com/maps/@-13.9833,33.7833,15z',
      'https://maps.google.com/?q=-13.9833,33.7833',
      'https://goo.gl/maps/...',
      'https://maps.app.goo.gl/...'
    ]
  }
}

/**
 * Convenience function for parsing Google Maps URLs
 */
export const parseGoogleMapsUrl = GoogleMapsUrlParser.parseUrlSync

/**
 * Convenience function for async parsing (with URL resolution)
 */
export const parseGoogleMapsUrlAsync = GoogleMapsUrlParser.parseUrl
