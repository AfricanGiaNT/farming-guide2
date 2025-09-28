/**
 * Tests for Content Validation Service
 * Tests data quality validation and content validation functionality
 */

import { ContentValidationService, contentValidationService } from '../contentValidationService'

describe('ContentValidationService', () => {
  let service: ContentValidationService

  beforeEach(() => {
    service = new ContentValidationService()
  })

  describe('Crop Recommendations Validation', () => {
    it('should validate valid crop recommendations data', () => {
      const validData = {
        recommendations: [
          {
            crop_name: 'maize',
            score: 85,
            suitability_level: 'excellent',
            rainfall_match: 'excellent',
            temperature_match: 'good',
            season_suitability: 'excellent',
            guide_recommendations: [
              'Plant in November-December for best results',
              'Use certified seeds for higher yields'
            ]
          }
        ],
        risk_assessment: {
          overall_risk_level: 'moderate',
          weather_risks: ['Heavy rainfall expected', 'Potential drought conditions'],
          pest_risks: ['Stem borer attack']
        },
        management_tips: [
          'Monitor soil moisture regularly',
          'Apply fertilizer at recommended rates'
        ],
        environmental_summary: {
          current_temperature: 25,
          total_7day_rainfall: 50,
          humidity: 60
        }
      }

      const result = service.validateCropRecommendations(validData)

      expect(result.isValid).toBe(true)
      expect(result.errors).toHaveLength(0)
      expect(result.qualityScore).toBeGreaterThan(0.8)
    })

    it('should detect missing required fields', () => {
      const invalidData = {
        recommendations: [
          {
            // Missing crop_name
            score: 85,
            suitability_level: 'excellent'
          }
        ]
      }

      const result = service.validateCropRecommendations(invalidData)

      expect(result.isValid).toBe(false)
      expect(result.errors).toContain("Recommendation 1: Missing required field 'crop_name'")
    })

    it('should detect invalid score values', () => {
      const invalidData = {
        recommendations: [
          {
            crop_name: 'maize',
            score: 150, // Invalid score > 100
            suitability_level: 'excellent'
          }
        ]
      }

      const result = service.validateCropRecommendations(invalidData)

      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('Recommendation 1: Invalid score (must be 0-100)')
    })

    it('should detect invalid suitability levels', () => {
      const invalidData = {
        recommendations: [
          {
            crop_name: 'maize',
            score: 85,
            suitability_level: 'invalid_level'
          }
        ]
      }

      const result = service.validateCropRecommendations(invalidData)

      expect(result.isValid).toBe(false)
      expect(result.errors).toContain("Recommendation 1: Invalid suitability level 'invalid_level'")
    })

    it('should handle empty data', () => {
      const result = service.validateCropRecommendations(null)

      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('No data received from API')
    })

    it('should handle missing recommendations array', () => {
      const invalidData = {
        risk_assessment: {},
        management_tips: []
      }

      const result = service.validateCropRecommendations(invalidData)

      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('Invalid recommendations data structure')
    })
  })

  describe('Risk Assessment Validation', () => {
    it('should validate valid risk assessment', () => {
      const validRiskAssessment = {
        overall_risk_level: 'moderate',
        weather_risks: [
          'Heavy rainfall expected in the next 7 days',
          'Potential drought conditions due to low precipitation'
        ],
        pest_risks: [
          'Stem borer attack detected in nearby fields'
        ]
      }

      const result = service.validateRiskAssessment(validRiskAssessment)

      expect(result.isValid).toBe(true)
      expect(result.errors).toHaveLength(0)
    })

    it('should detect invalid overall risk level', () => {
      const invalidRiskAssessment = {
        overall_risk_level: 'invalid_level',
        weather_risks: ['Heavy rainfall expected']
      }

      const result = service.validateRiskAssessment(invalidRiskAssessment)

      expect(result.isValid).toBe(false)
      expect(result.errors).toContain("Invalid overall risk level: 'invalid_level'")
    })

    it('should warn about too many weather risks', () => {
      const riskAssessment = {
        overall_risk_level: 'moderate',
        weather_risks: Array(20).fill('Risk item') // Too many risks
      }

      const result = service.validateRiskAssessment(riskAssessment)

      expect(result.warnings).toContain('Too many weather risks (20), consider filtering')
    })

    it('should validate individual risk text', () => {
      const riskAssessment = {
        overall_risk_level: 'moderate',
        weather_risks: [
          'Valid risk description',
          'TABLE_SCHEMA: invalid_database_fragment', // Should be flagged
          'A' // Too short
        ]
      }

      const result = service.validateRiskAssessment(riskAssessment)

      expect(result.errors).toContain('Weather Risk 2: Contains forbidden pattern (likely database fragment)')
      expect(result.errors).toContain('Weather Risk 3: Text too short (minimum 10 characters)')
    })
  })

  describe('Management Tips Validation', () => {
    it('should validate valid management tips', () => {
      const validTips = [
        'Monitor soil moisture regularly throughout the growing season',
        'Apply fertilizer at recommended rates for optimal growth',
        'Control weeds early to prevent competition with crops'
      ]

      const result = service.validateManagementTips(validTips)

      expect(result.isValid).toBe(true)
      expect(result.errors).toHaveLength(0)
    })

    it('should detect non-array management tips', () => {
      const result = service.validateManagementTips('not an array')

      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('Management tips must be an array')
    })

    it('should warn about too many management tips', () => {
      const manyTips = Array(25).fill('Management tip')

      const result = service.validateManagementTips(manyTips)

      expect(result.warnings).toContain('Too many management tips (25), consider categorization')
    })

    it('should validate individual tip content', () => {
      const tips = [
        'Valid management tip with sufficient content',
        'COLUMN_NAME: database_fragment', // Should be flagged
        'Short' // Too short
      ]

      const result = service.validateManagementTips(tips)

      expect(result.errors).toContain('Management Tip 2: Contains forbidden pattern (likely database fragment)')
      expect(result.errors).toContain('Management Tip 3: Text too short (minimum 15 characters)')
    })
  })

  describe('Environmental Summary Validation', () => {
    it('should validate valid environmental summary', () => {
      const validSummary = {
        current_temperature: 25,
        total_7day_rainfall: 50,
        humidity: 60
      }

      const result = service.validateEnvironmentalSummary(validSummary)

      expect(result.isValid).toBe(true)
      expect(result.errors).toHaveLength(0)
    })

    it('should detect invalid temperature values', () => {
      const invalidSummary = {
        current_temperature: 100, // Too high
        total_7day_rainfall: 50,
        humidity: 60
      }

      const result = service.validateEnvironmentalSummary(invalidSummary)

      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('Invalid temperature value')
    })

    it('should detect invalid rainfall values', () => {
      const invalidSummary = {
        current_temperature: 25,
        total_7day_rainfall: -10, // Negative
        humidity: 60
      }

      const result = service.validateEnvironmentalSummary(invalidSummary)

      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('Invalid rainfall value')
    })

    it('should detect invalid humidity values', () => {
      const invalidSummary = {
        current_temperature: 25,
        total_7day_rainfall: 50,
        humidity: 150 // Too high
      }

      const result = service.validateEnvironmentalSummary(invalidSummary)

      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('Invalid humidity value')
    })
  })

  describe('Text Content Validation', () => {
    it('should validate valid agricultural text', () => {
      const validText = 'Monitor soil moisture regularly for optimal crop growth'

      const result = service.validateTextContent(validText, 'Test Context')

      expect(result.isValid).toBe(true)
      expect(result.errors).toHaveLength(0)
    })

    it('should detect forbidden patterns', () => {
      const forbiddenTexts = [
        '123. Database entry',
        'TABLE_SCHEMA: invalid',
        'COLUMN_NAME: field',
        '{}',
        'snake_case_pattern',
        'CONSTANT_CASE',
        '123456',
        '!@#$%^&*()'
      ]

      forbiddenTexts.forEach((text, index) => {
        const result = service.validateTextContent(text, `Test ${index}`)
        expect(result.isValid).toBe(false)
        expect(result.errors).toContain(`Test ${index}: Contains forbidden pattern (likely database fragment)`)
      })
    })

    it('should detect non-agricultural content', () => {
      const nonAgriculturalText = 'This is about computer programming and software development'

      const result = service.validateTextContent(nonAgriculturalText, 'Test Context')

      expect(result.warnings).toContain('Test Context: May not contain agricultural content')
    })

    it('should suggest actionable content', () => {
      const nonActionableText = 'This is just descriptive information'

      const result = service.validateTextContent(nonActionableText, 'Test Context')

      expect(result.suggestions).toContain('Test Context: Consider making content more actionable')
    })
  })

  describe('Content Quality Metrics', () => {
    it('should calculate quality metrics for complete data', () => {
      const completeData = {
        recommendations: [{ crop_name: 'maize', score: 85, suitability_level: 'excellent' }],
        risk_assessment: { overall_risk_level: 'moderate', weather_risks: ['Heavy rainfall'] },
        management_tips: ['Monitor soil moisture'],
        environmental_summary: { current_temperature: 25, total_7day_rainfall: 50 }
      }

      const metrics = service.getContentQualityMetrics(completeData)

      expect(metrics.completeness).toBe(1.0) // All components present
      expect(metrics.accuracy).toBeGreaterThan(0.8) // No errors
      expect(metrics.relevance).toBeGreaterThan(0.5) // Agricultural content
      expect(metrics.clarity).toBeGreaterThan(0.5) // Clear text
      expect(metrics.overall).toBeGreaterThan(0.7)
    })

    it('should calculate lower quality metrics for incomplete data', () => {
      const incompleteData = {
        recommendations: [{ crop_name: 'maize', score: 85, suitability_level: 'excellent' }]
        // Missing other components
      }

      const metrics = service.getContentQualityMetrics(incompleteData)

      expect(metrics.completeness).toBeLessThan(1.0)
      expect(metrics.overall).toBeLessThan(0.7)
    })

    it('should calculate accuracy based on validation errors', () => {
      const errorData = {
        recommendations: [
          { crop_name: 'maize', score: 150, suitability_level: 'invalid' }, // Errors
          { crop_name: 'rice', score: -10, suitability_level: 'excellent' } // More errors
        ]
      }

      const metrics = service.getContentQualityMetrics(errorData)

      expect(metrics.accuracy).toBeLessThan(0.6) // Multiple errors
    })
  })

  describe('Helper Methods', () => {
    it('should identify agricultural keywords', () => {
      const agriculturalText = 'Plant maize seeds in well-prepared soil'
      const nonAgriculturalText = 'Computer programming and software development'

      const containsAgricultural = (service as any).containsAgriculturalKeywords.bind(service)
      
      expect(containsAgricultural(agriculturalText)).toBe(true)
      expect(containsAgricultural(nonAgriculturalText)).toBe(false)
    })

    it('should identify actionable content', () => {
      const actionableText = 'Apply fertilizer at recommended rates'
      const nonActionableText = 'This is descriptive information'

      const isActionable = (service as any).isActionableContent.bind(service)
      
      expect(isActionable(actionableText)).toBe(true)
      expect(isActionable(nonActionableText)).toBe(false)
    })
  })
})

describe('Singleton Instance', () => {
  it('should export singleton instance', () => {
    expect(contentValidationService).toBeInstanceOf(ContentValidationService)
  })

  it('should have default validation rules', () => {
    expect(contentValidationService).toBeDefined()
  })
})
