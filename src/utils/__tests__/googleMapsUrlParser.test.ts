import { GoogleMapsUrlParser, parseGoogleMapsUrl, parseGoogleMapsUrlAsync } from '../utils/googleMapsUrlParser'

describe('GoogleMapsUrlParser', () => {
  describe('parseUrlSync', () => {
    describe('Valid Google Maps URLs', () => {
      test('parses standard Google Maps URL with @ coordinates', () => {
        const url = 'https://maps.google.com/maps/@-13.9833,33.7833,15z'
        const result = GoogleMapsUrlParser.parseUrlSync(url)
        
        expect(result.success).toBe(true)
        expect(result.coordinates).toEqual({
          lat: -13.9833,
          lon: 33.7833
        })
      })

      test('parses Google Maps URL with q parameter', () => {
        const url = 'https://maps.google.com/maps?q=-13.9833,33.7833'
        const result = GoogleMapsUrlParser.parseUrlSync(url)
        
        expect(result.success).toBe(true)
        expect(result.coordinates).toEqual({
          lat: -13.9833,
          lon: 33.7833
        })
      })

      test('parses Google Maps URL with ll parameter', () => {
        const url = 'https://maps.google.com/maps?ll=-13.9833,33.7833'
        const result = GoogleMapsUrlParser.parseUrlSync(url)
        
        expect(result.success).toBe(true)
        expect(result.coordinates).toEqual({
          lat: -13.9833,
          lon: 33.7833
        })
      })

      test('parses Google Maps URL with center parameter', () => {
        const url = 'https://maps.google.com/maps?center=-13.9833,33.7833'
        const result = GoogleMapsUrlParser.parseUrlSync(url)
        
        expect(result.success).toBe(true)
        expect(result.coordinates).toEqual({
          lat: -13.9833,
          lon: 33.7833
        })
      })

      test('parses Google Maps URL with sll parameter', () => {
        const url = 'https://maps.google.com/maps?sll=-13.9833,33.7833'
        const result = GoogleMapsUrlParser.parseUrlSync(url)
        
        expect(result.success).toBe(true)
        expect(result.coordinates).toEqual({
          lat: -13.9833,
          lon: 33.7833
        })
      })

      test('parses www.google.com/maps URL', () => {
        const url = 'https://www.google.com/maps/@-13.9833,33.7833,15z'
        const result = GoogleMapsUrlParser.parseUrlSync(url)
        
        expect(result.success).toBe(true)
        expect(result.coordinates).toEqual({
          lat: -13.9833,
          lon: 33.7833
        })
      })

      test('parses new Google Maps format', () => {
        const url = 'https://www.google.com/maps/@-13.9833,33.7833,15z/data=!3m1!1e3'
        const result = GoogleMapsUrlParser.parseUrlSync(url)
        
        expect(result.success).toBe(true)
        expect(result.coordinates).toEqual({
          lat: -13.9833,
          lon: 33.7833
        })
      })

      test('handles URLs with additional parameters', () => {
        const url = 'https://maps.google.com/maps?q=-13.9833,33.7833&hl=en&z=15'
        const result = GoogleMapsUrlParser.parseUrlSync(url)
        
        expect(result.success).toBe(true)
        expect(result.coordinates).toEqual({
          lat: -13.9833,
          lon: 33.7833
        })
      })

      test('preserves coordinate precision', () => {
        const url = 'https://maps.google.com/maps/@-13.983333333,33.783333333,15z'
        const result = GoogleMapsUrlParser.parseUrlSync(url)
        
        expect(result.success).toBe(true)
        expect(result.coordinates).toEqual({
          lat: -13.983333333,
          lon: 33.783333333
        })
      })
    })

    describe('Edge Cases', () => {
      test('handles coordinates at poles', () => {
        const url = 'https://maps.google.com/maps/@90,0,15z'
        const result = GoogleMapsUrlParser.parseUrlSync(url)
        
        expect(result.success).toBe(true)
        expect(result.coordinates).toEqual({
          lat: 90,
          lon: 0
        })
      })

      test('handles coordinates at date line', () => {
        const url = 'https://maps.google.com/maps/@0,180,15z'
        const result = GoogleMapsUrlParser.parseUrlSync(url)
        
        expect(result.success).toBe(true)
        expect(result.coordinates).toEqual({
          lat: 0,
          lon: 180
        })
      })

      test('handles negative coordinates', () => {
        const url = 'https://maps.google.com/maps/@-90,-180,15z'
        const result = GoogleMapsUrlParser.parseUrlSync(url)
        
        expect(result.success).toBe(true)
        expect(result.coordinates).toEqual({
          lat: -90,
          lon: -180
        })
      })

      test('handles zero coordinates', () => {
        const url = 'https://maps.google.com/maps/@0,0,15z'
        const result = GoogleMapsUrlParser.parseUrlSync(url)
        
        expect(result.success).toBe(true)
        expect(result.coordinates).toEqual({
          lat: 0,
          lon: 0
        })
      })
    })

    describe('Invalid URLs', () => {
      test('rejects non-Google Maps URLs', () => {
        const url = 'https://www.example.com/maps?q=-13.9833,33.7833'
        const result = GoogleMapsUrlParser.parseUrlSync(url)
        
        expect(result.success).toBe(false)
        expect(result.error).toContain('Not a Google Maps URL')
      })

      test('rejects URLs without coordinates', () => {
        const url = 'https://maps.google.com/maps?hl=en'
        const result = GoogleMapsUrlParser.parseUrlSync(url)
        
        expect(result.success).toBe(false)
        expect(result.error).toContain('No coordinates found')
      })

      test('rejects invalid coordinate ranges', () => {
        const url = 'https://maps.google.com/maps/@91,181,15z'
        const result = GoogleMapsUrlParser.parseUrlSync(url)
        
        expect(result.success).toBe(false)
        expect(result.error).toContain('No coordinates found')
      })

      test('rejects empty string', () => {
        const result = GoogleMapsUrlParser.parseUrlSync('')
        
        expect(result.success).toBe(false)
        expect(result.error).toContain('Invalid URL')
      })

      test('rejects null input', () => {
        const result = GoogleMapsUrlParser.parseUrlSync(null as any)
        
        expect(result.success).toBe(false)
        expect(result.error).toContain('Invalid URL')
      })

      test('rejects non-string input', () => {
        const result = GoogleMapsUrlParser.parseUrlSync(123 as any)
        
        expect(result.success).toBe(false)
        expect(result.error).toContain('Invalid URL')
      })

      test('rejects URLs without protocol', () => {
        const url = 'maps.google.com/maps/@-13.9833,33.7833,15z'
        const result = GoogleMapsUrlParser.parseUrlSync(url)
        
        expect(result.success).toBe(false)
        expect(result.error).toContain('Invalid URL')
      })
    })

    describe('Shortened URLs', () => {
      test('handles goo.gl URLs (basic detection)', () => {
        const url = 'https://goo.gl/maps/abc123'
        const result = GoogleMapsUrlParser.parseUrlSync(url)
        
        // This will fail because we can't resolve the actual URL in sync mode
        expect(result.success).toBe(false)
        expect(result.error).toContain('No coordinates found')
      })

      test('handles maps.app.goo.gl URLs (basic detection)', () => {
        const url = 'https://maps.app.goo.gl/abc123'
        const result = GoogleMapsUrlParser.parseUrlSync(url)
        
        // This will fail because we can't resolve the actual URL in sync mode
        expect(result.success).toBe(false)
        expect(result.error).toContain('No coordinates found')
      })
    })
  })

  describe('parseUrl (async)', () => {
    test('handles async parsing', async () => {
      const url = 'https://maps.google.com/maps/@-13.9833,33.7833,15z'
      const result = await GoogleMapsUrlParser.parseUrl(url)
      
      expect(result.success).toBe(true)
      expect(result.coordinates).toEqual({
        lat: -13.9833,
        lon: 33.7833
      })
    })

    test('handles errors in async parsing', async () => {
      const url = 'https://www.example.com/maps?q=-13.9833,33.7833'
      const result = await GoogleMapsUrlParser.parseUrl(url)
      
      expect(result.success).toBe(false)
      expect(result.error).toContain('Not a Google Maps URL')
    })
  })

  describe('Convenience functions', () => {
    test('parseGoogleMapsUrl works correctly', () => {
      const url = 'https://maps.google.com/maps/@-13.9833,33.7833,15z'
      const result = parseGoogleMapsUrl(url)
      
      expect(result.success).toBe(true)
      expect(result.coordinates).toEqual({
        lat: -13.9833,
        lon: 33.7833
      })
    })

    test('parseGoogleMapsUrlAsync works correctly', async () => {
      const url = 'https://maps.google.com/maps/@-13.9833,33.7833,15z'
      const result = await parseGoogleMapsUrlAsync(url)
      
      expect(result.success).toBe(true)
      expect(result.coordinates).toEqual({
        lat: -13.9833,
        lon: 33.7833
      })
    })
  })

  describe('getSupportedFormats', () => {
    test('returns array of supported URL formats', () => {
      const formats = GoogleMapsUrlParser.getSupportedFormats()
      
      expect(Array.isArray(formats)).toBe(true)
      expect(formats.length).toBeGreaterThan(0)
      expect(formats.every(format => typeof format === 'string')).toBe(true)
    })
  })

  describe('Performance', () => {
    test('parses URL quickly', () => {
      const url = 'https://maps.google.com/maps/@-13.9833,33.7833,15z'
      const start = performance.now()
      const result = GoogleMapsUrlParser.parseUrlSync(url)
      const end = performance.now()
      
      expect(result.success).toBe(true)
      expect(end - start).toBeLessThan(100) // Should parse in less than 100ms
    })
  })
})
