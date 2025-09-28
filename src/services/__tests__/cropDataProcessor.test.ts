import { cropDataProcessor, ProcessedRisk, CategorizedTips } from '../cropDataProcessor'

describe('CropDataProcessor', () => {
  describe('processRiskAssessment', () => {
    it('should limit weather risks to maximum 5 items', () => {
      const rawRisks = [
        'Heavy rainfall expected in the next 2 weeks',
        'Drought conditions may affect crop growth',
        'High temperature stress during flowering period',
        'Pest infestation risk due to wet conditions',
        'Disease outbreak potential in humid weather',
        'Soil erosion from excessive rainfall',
        'Flooding risk in low-lying areas',
        'Wind damage to young plants',
        'Frost damage during cold spells',
        'Hail damage to crops',
        'Lightning strikes affecting irrigation',
        'Heat wave conditions',
        'Low humidity affecting pollination',
        'Excessive cloud cover reducing photosynthesis'
      ]

      const processed = cropDataProcessor.processRiskAssessment(rawRisks)
      
      expect(processed).toHaveLength(5)
      expect(processed.every(risk => risk.text.length > 10)).toBe(true)
    })

    it('should filter out database fragments from risk text', () => {
      const rawRisks = [
        'Heavy rainfall expected in the next 2 weeks',
        'table_weather_risks: column_risk_level',
        '123. database_fragment',
        'Drought conditions may affect crop growth',
        'ID: 456, TYPE: weather_risk',
        'High temperature stress during flowering period',
        'row_1: {risk_type: "weather", level: "high"}',
        'Pest infestation risk due to wet conditions'
      ]

      const processed = cropDataProcessor.processRiskAssessment(rawRisks)
      
      // Should only include valid agricultural risks
      expect(processed).toHaveLength(4)
      expect(processed.every(risk => 
        risk.text.includes('rainfall') || 
        risk.text.includes('Drought') || 
        risk.text.includes('temperature') || 
        risk.text.includes('Pest')
      )).toBe(true)
    })

    it('should categorize risks correctly', () => {
      const rawRisks = [
        'Heavy rainfall expected in the next 2 weeks',
        'Pest infestation risk due to wet conditions',
        'Fungal disease outbreak potential',
        'General agricultural concern'
      ]

      const processed = cropDataProcessor.processRiskAssessment(rawRisks)
      
      expect(processed[0].category).toBe('weather')
      expect(processed[1].category).toBe('pest')
      expect(processed[2].category).toBe('disease')
      expect(processed[3].category).toBe('other')
    })

    it('should handle empty or invalid input gracefully', () => {
      expect(cropDataProcessor.processRiskAssessment([])).toEqual([])
      expect(cropDataProcessor.processRiskAssessment(null as any)).toEqual([])
      expect(cropDataProcessor.processRiskAssessment(undefined as any)).toEqual([])
      expect(cropDataProcessor.processRiskAssessment([''])).toEqual([])
      expect(cropDataProcessor.processRiskAssessment(['   '])).toEqual([])
    })

    it('should prioritize risks correctly', () => {
      const rawRisks = [
        'Minor weather concern',
        'Severe drought conditions expected',
        'Critical pest outbreak',
        'Moderate disease risk'
      ]

      const processed = cropDataProcessor.processRiskAssessment(rawRisks)
      
      // Severe and critical risks should have higher priority
      const severeRisk = processed.find(r => r.text.includes('Severe'))
      const criticalRisk = processed.find(r => r.text.includes('Critical'))
      const minorRisk = processed.find(r => r.text.includes('Minor'))
      
      expect(severeRisk?.priority).toBeGreaterThan(minorRisk?.priority || 0)
      expect(criticalRisk?.priority).toBeGreaterThan(minorRisk?.priority || 0)
    })
  })

  describe('summarizeManagementTips', () => {
    it('should categorize management tips by farming phase', () => {
      const tips = [
        'Plant seeds at proper depth',
        'Apply fertilizer every 6 weeks',
        'Harvest when crops are mature',
        'Monitor soil moisture regularly',
        'Sow seeds in rows',
        'Control weeds early',
        'Collect produce in morning',
        'General farming advice'
      ]

      const categorized = cropDataProcessor.summarizeManagementTips(tips)
      
      expect(categorized.planting).toContain('Plant seeds at proper depth')
      expect(categorized.planting).toContain('Sow seeds in rows')
      expect(categorized.maintenance).toContain('Apply fertilizer every 6 weeks')
      expect(categorized.maintenance).toContain('Control weeds early')
      expect(categorized.harvest).toContain('Harvest when crops are mature')
      expect(categorized.harvest).toContain('Collect produce in morning')
      expect(categorized.general).toContain('General farming advice')
    })

    it('should limit tips per category to prevent information overload', () => {
      const tips = Array.from({ length: 20 }, (_, i) => `Planting tip ${i + 1}`)
      
      const categorized = cropDataProcessor.summarizeManagementTips(tips)
      
      expect(categorized.planting).toHaveLength(3) // Limited to 3
      expect(categorized.maintenance).toHaveLength(0)
      expect(categorized.harvest).toHaveLength(0)
      expect(categorized.general).toHaveLength(0)
    })

    it('should filter out invalid tips', () => {
      const tips = [
        'Valid planting tip',
        '', // Empty
        '   ', // Whitespace only
        'Too short', // Too short
        'This is a very long tip that exceeds the maximum length limit and should be filtered out because it is too verbose and contains excessive information that would overwhelm the user with too much detail about agricultural practices and recommendations',
        'Valid maintenance tip'
      ]

      const categorized = cropDataProcessor.summarizeManagementTips(tips)
      
      expect(categorized.planting).toHaveLength(1)
      expect(categorized.maintenance).toHaveLength(1)
    })
  })

  describe('prioritizeRecommendations', () => {
    it('should prioritize recommendations by score and suitability', () => {
      const recommendations = [
        {
          crop_name: 'maize',
          score: 75,
          suitability_level: 'good',
          rainfall_match: 'good',
          temperature_match: 'excellent',
          season_suitability: 'good',
          guide_recommendations: ['Plant in November', 'Use certified seeds']
        },
        {
          crop_name: 'groundnut',
          score: 85,
          suitability_level: 'excellent',
          rainfall_match: 'excellent',
          temperature_match: 'excellent',
          season_suitability: 'excellent',
          guide_recommendations: ['Plant in December', 'Ensure good drainage']
        }
      ]

      const prioritized = cropDataProcessor.prioritizeRecommendations(recommendations)
      
      expect(prioritized[0].crop_name).toBe('groundnut') // Higher score and excellent suitability
      expect(prioritized[0].priority).toBeGreaterThan(prioritized[1].priority)
    })

    it('should filter recommendation text', () => {
      const recommendations = [
        {
          crop_name: 'maize',
          score: 75,
          suitability_level: 'good',
          guide_recommendations: [
            'Plant seeds at proper depth for optimal growth',
            '123. database_fragment',
            'Apply fertilizer according to soil test results',
            'table_recommendations: invalid_data'
          ]
        }
      ]

      const prioritized = cropDataProcessor.prioritizeRecommendations(recommendations)
      
      expect(prioritized[0].filtered_recommendations).toHaveLength(2)
      expect(prioritized[0].filtered_recommendations).toContain('Plant seeds at proper depth for optimal growth')
      expect(prioritized[0].filtered_recommendations).toContain('Apply fertilizer according to soil test results')
    })
  })

  describe('validateApiResponse', () => {
    it('should validate correct API response structure', () => {
      const validResponse = {
        recommendations: [
          { crop_name: 'maize', score: 75 }
        ],
        risk_assessment: {
          weather_risks: ['Heavy rainfall expected']
        },
        management_tips: ['Plant seeds properly']
      }

      const validation = cropDataProcessor.validateApiResponse(validResponse)
      
      expect(validation.isValid).toBe(true)
      expect(validation.errors).toHaveLength(0)
    })

    it('should detect invalid API response structure', () => {
      const invalidResponse = {
        recommendations: 'not an array',
        risk_assessment: {
          // Missing weather_risks
        },
        management_tips: 'not an array'
      }

      const validation = cropDataProcessor.validateApiResponse(invalidResponse)
      
      expect(validation.isValid).toBe(false)
      expect(validation.errors.length).toBeGreaterThan(0)
      expect(validation.errors).toContain('Invalid recommendations data structure')
      expect(validation.errors).toContain('Missing weather risks in risk assessment')
      expect(validation.errors).toContain('Invalid management tips data structure')
    })

    it('should handle null or undefined responses', () => {
      const validation1 = cropDataProcessor.validateApiResponse(null)
      const validation2 = cropDataProcessor.validateApiResponse(undefined)
      
      expect(validation1.isValid).toBe(false)
      expect(validation1.errors).toContain('No data received from API')
      expect(validation2.isValid).toBe(false)
      expect(validation2.errors).toContain('No data received from API')
    })
  })

  // Phase 2 Tests: AI Enhancement and Comprehensive Processing
  describe('Phase 2: AI Enhancement', () => {
    describe('processRiskAssessment with AI', () => {
      it('should process risks with AI enhancement when context is provided', async () => {
        const rawRisks = [
          'Heavy rainfall expected in the next 7 days',
          'Potential drought conditions due to low precipitation'
        ]

        const result = await cropDataProcessor.processRiskAssessment(
          rawRisks,
          'Lilongwe',
          'current',
          { temperature: 25, rainfall: 50 }
        )

        expect(result).toHaveLength(2)
        expect(result[0]).toHaveProperty('id')
        expect(result[0]).toHaveProperty('text')
        expect(result[0]).toHaveProperty('category')
        expect(result[0]).toHaveProperty('severity')
        expect(result[0]).toHaveProperty('priority')
      })

      it('should fallback to non-AI processing when context is missing', async () => {
        const rawRisks = ['Heavy rainfall expected']

        const result = await cropDataProcessor.processRiskAssessment(rawRisks)

        expect(result).toHaveLength(1)
        expect(result[0].text).toContain('Heavy rainfall')
      })
    })

    describe('summarizeManagementTips with AI', () => {
      it('should process management tips with AI enhancement', async () => {
        const tips = [
          'Plant seeds in well-prepared soil',
          'Monitor soil moisture regularly',
          'Apply fertilizer at recommended rates'
        ]

        const result = await cropDataProcessor.summarizeManagementTips(
          tips,
          'Lilongwe',
          'current'
        )

        expect(result).toHaveProperty('planting')
        expect(result).toHaveProperty('maintenance')
        expect(result).toHaveProperty('harvest')
        expect(result).toHaveProperty('general')
        expect(result.planting.length).toBeGreaterThan(0)
        expect(result.maintenance.length).toBeGreaterThan(0)
      })

      it('should fallback to non-AI processing when context is missing', async () => {
        const tips = ['Plant seeds in well-prepared soil']

        const result = await cropDataProcessor.summarizeManagementTips(tips)

        expect(result.planting).toHaveLength(1)
        expect(result.planting[0]).toContain('Plant seeds')
      })
    })

    describe('prioritizeRecommendations with AI', () => {
      it('should enhance recommendations with AI insights', async () => {
        const recommendations = [
          {
            crop_name: 'maize',
            score: 85,
            suitability_level: 'excellent',
            rainfall_match: 'excellent',
            temperature_match: 'good',
            season_suitability: 'excellent'
          }
        ]

        const result = await cropDataProcessor.prioritizeRecommendations(
          recommendations,
          'Lilongwe',
          'current',
          { temperature: 25, rainfall: 50 }
        )

        expect(result).toHaveLength(1)
        expect(result[0]).toHaveProperty('crop_name', 'maize')
        expect(result[0]).toHaveProperty('score', 85)
        // AI enhancement fields should be present (even if fallback)
        expect(result[0]).toHaveProperty('ai_summary')
        expect(result[0]).toHaveProperty('key_benefits')
        expect(result[0]).toHaveProperty('potential_challenges')
        expect(result[0]).toHaveProperty('actionable_steps')
        expect(result[0]).toHaveProperty('seasonal_advice')
        expect(result[0]).toHaveProperty('confidence_score')
      })

      it('should preserve original data when AI enhancement fails', async () => {
        const recommendations = [
          {
            crop_name: 'maize',
            score: 85,
            suitability_level: 'excellent'
          }
        ]

        const result = await cropDataProcessor.prioritizeRecommendations(recommendations)

        expect(result).toHaveLength(1)
        expect(result[0].crop_name).toBe('maize')
        expect(result[0].score).toBe(85)
      })
    })
  })

  describe('Phase 2: Comprehensive Data Processing', () => {
    it('should process comprehensive data with all enhancements', async () => {
      const rawData = {
        recommendations: [
          {
            crop_name: 'maize',
            score: 85,
            suitability_level: 'excellent',
            rainfall_match: 'excellent',
            temperature_match: 'good',
            season_suitability: 'excellent',
            guide_recommendations: ['Plant in November-December']
          }
        ],
        risk_assessment: {
          overall_risk_level: 'moderate',
          weather_risks: ['Heavy rainfall expected', 'Potential drought']
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

      const result = await cropDataProcessor.processComprehensiveData(
        rawData,
        'Lilongwe',
        'current',
        { temperature: 25, rainfall: 50, humidity: 60 }
      )

      // Should have all original data plus enhancements
      expect(result).toHaveProperty('recommendations')
      expect(result).toHaveProperty('risk_assessment')
      expect(result).toHaveProperty('management_tips')
      expect(result).toHaveProperty('environmental_summary')
      expect(result).toHaveProperty('processing_metadata')

      // Processing metadata should be present
      expect(result.processing_metadata).toHaveProperty('location', 'Lilongwe')
      expect(result.processing_metadata).toHaveProperty('season', 'current')
      expect(result.processing_metadata).toHaveProperty('timestamp')
      expect(result.processing_metadata).toHaveProperty('processing_version', '2.0')
      expect(result.processing_metadata).toHaveProperty('validation')

      // Validation metadata should be present
      expect(result.processing_metadata.validation).toHaveProperty('isValid')
      expect(result.processing_metadata.validation).toHaveProperty('qualityScore')
      expect(result.processing_metadata.validation).toHaveProperty('errorCount')
      expect(result.processing_metadata.validation).toHaveProperty('warningCount')
      expect(result.processing_metadata.validation).toHaveProperty('qualityMetrics')
    })

    it('should handle processing errors gracefully', async () => {
      const invalidData = {
        recommendations: [
          {
            crop_name: 'maize',
            score: 150, // Invalid score
            suitability_level: 'invalid' // Invalid level
          }
        ]
      }

      const result = await cropDataProcessor.processComprehensiveData(
        invalidData,
        'Lilongwe',
        'current',
        {}
      )

      // Should still return processed data with error information
      expect(result).toHaveProperty('processing_metadata')
      expect(result.processing_metadata.validation.isValid).toBe(false)
      expect(result.processing_metadata.validation.errorCount).toBeGreaterThan(0)
    })

    it('should include AI enhancement status in metadata', async () => {
      const rawData = {
        recommendations: [{ crop_name: 'maize', score: 85, suitability_level: 'excellent' }],
        risk_assessment: { weather_risks: ['Heavy rainfall'] },
        management_tips: ['Monitor soil moisture'],
        environmental_summary: { current_temperature: 25 }
      }

      const result = await cropDataProcessor.processComprehensiveData(
        rawData,
        'Lilongwe',
        'current',
        { temperature: 25 }
      )

      // AI enhancement status should be tracked
      expect(result.processing_metadata).toHaveProperty('ai_enhanced')
      expect(typeof result.processing_metadata.ai_enhanced).toBe('boolean')
    })

    it('should handle null/undefined data gracefully', async () => {
      const result = await cropDataProcessor.processComprehensiveData(
        null,
        'Lilongwe',
        'current',
        {}
      )

      // Should return fallback data structure
      expect(result).toHaveProperty('processing_metadata')
      expect(result.processing_metadata.processing_version).toContain('fallback')
    })
  })
})
