/**
 * Crop Data Processor Service
 * Handles data filtering, cleaning, and transformation for crop recommendations
 * Enhanced with AI-powered summarization capabilities
 */

import { aiSummarizationService, SummarizedRisk, SummarizedManagementTips, EnhancedRecommendation } from './aiSummarizationService'
import { contentValidationService, ValidationResult, ContentQualityMetrics } from './contentValidationService'

export interface ProcessedRisk {
  id: string;
  text: string;
  category: 'weather' | 'pest' | 'disease' | 'other';
  severity: 'low' | 'medium' | 'high';
  priority: number;
}

export interface CategorizedTips {
  planting: string[];
  maintenance: string[];
  harvest: string[];
  general: string[];
}

export interface PrioritizedRecommendation {
  crop_name: string;
  score: number;
  suitability_level: string;
  priority: number;
  filtered_recommendations: string[];
}

export class CropDataProcessor {
  /**
   * Process and filter weather risks to top 5 most relevant
   * Enhanced with AI summarization capabilities
   */
  async processRiskAssessment(
    rawRisks: string[], 
    location?: string, 
    season?: string, 
    weatherData?: any
  ): Promise<ProcessedRisk[]> {
    if (!rawRisks || !Array.isArray(rawRisks)) {
      return [];
    }

    // Filter out database fragments and technical specs
    const filteredRisks = rawRisks
      .filter(risk => this.isValidRiskText(risk))
      .map((risk, index) => this.processRiskText(risk, index))
      .filter(risk => risk !== null)
      .sort((a, b) => b.priority - a.priority) // Sort by priority (high to low)
      .slice(0, 5); // Limit to top 5

    // Try AI enhancement if context is available
    if (location && season && weatherData) {
      try {
        const aiSummarizedRisks = await aiSummarizationService.summarizeWeatherRisks(
          filteredRisks.map(r => r.text),
          location,
          season,
          weatherData
        );
        
        // Convert AI results back to ProcessedRisk format
        return aiSummarizedRisks.map(aiRisk => ({
          id: aiRisk.id,
          text: aiRisk.summary || aiRisk.originalText,
          category: aiRisk.category,
          severity: aiRisk.severity,
          priority: aiRisk.priority,
        }));
      } catch (error) {
        console.warn('AI risk summarization failed, using fallback:', error);
      }
    }

    return filteredRisks as ProcessedRisk[];
  }

  /**
   * Check if risk text is valid (not a database fragment)
   */
  private isValidRiskText(text: string): boolean {
    if (!text || typeof text !== 'string') {
      return false;
    }

    const cleanText = text.trim();
    
    // Filter out very short or very long text (likely fragments)
    if (cleanText.length < 10 || cleanText.length > 500) {
      return false;
    }

    // Filter out database-like content
    const databasePatterns = [
      /^[0-9]+\./, // Starts with numbers
      /^[A-Z_]+:/, // Database field names
      /^table|column|row|id:/i, // Database terms
      /^[{}[\]()]+/, // JSON-like structures
      /^[a-z]+_[a-z]+/, // Snake_case patterns
      /^[A-Z]+_[A-Z]+/, // CONSTANT_CASE patterns
    ];

    for (const pattern of databasePatterns) {
      if (pattern.test(cleanText)) {
        return false;
      }
    }

    // Must contain some agricultural keywords
    const agriculturalKeywords = [
      'rain', 'drought', 'flood', 'temperature', 'weather', 'climate',
      'pest', 'disease', 'insect', 'fungus', 'bacteria', 'virus',
      'crop', 'plant', 'seed', 'soil', 'fertilizer', 'irrigation',
      'harvest', 'yield', 'growth', 'maturity', 'planting'
    ];

    const hasAgriculturalContent = agriculturalKeywords.some(keyword => 
      cleanText.toLowerCase().includes(keyword)
    );

    return hasAgriculturalContent;
  }

  /**
   * Process individual risk text and categorize it
   */
  private processRiskText(text: string, index: number): ProcessedRisk | null {
    const cleanText = text.trim();
    
    // Determine category based on content
    let category: 'weather' | 'pest' | 'disease' | 'other' = 'other';
    let severity: 'low' | 'medium' | 'high' = 'medium';
    let priority = 50; // Default priority

    const lowerText = cleanText.toLowerCase();

    // Weather-related risks
    if (lowerText.includes('rain') || lowerText.includes('drought') || 
        lowerText.includes('flood') || lowerText.includes('temperature') ||
        lowerText.includes('weather') || lowerText.includes('climate')) {
      category = 'weather';
      priority = 80; // High priority for weather risks
    }

    // Pest-related risks
    if (lowerText.includes('pest') || lowerText.includes('insect') || 
        lowerText.includes('worm') || lowerText.includes('beetle')) {
      category = 'pest';
      priority = 70;
    }

    // Disease-related risks
    if (lowerText.includes('disease') || lowerText.includes('fungus') || 
        lowerText.includes('bacteria') || lowerText.includes('virus') ||
        lowerText.includes('blight') || lowerText.includes('rot')) {
      category = 'disease';
      priority = 75;
    }

    // Determine severity based on keywords
    if (lowerText.includes('severe') || lowerText.includes('critical') || 
        lowerText.includes('extreme') || lowerText.includes('high risk')) {
      severity = 'high';
      priority += 20;
    } else if (lowerText.includes('moderate') || lowerText.includes('medium') || 
               lowerText.includes('possible') || lowerText.includes('potential')) {
      severity = 'medium';
    } else if (lowerText.includes('low') || lowerText.includes('minor') || 
               lowerText.includes('slight')) {
      severity = 'low';
      priority -= 10;
    }

    return {
      id: `risk_${index}`,
      text: cleanText,
      category,
      severity,
      priority
    };
  }

  /**
   * Categorize management tips by farming phase
   * Enhanced with AI summarization capabilities
   */
  async summarizeManagementTips(
    tips: string[], 
    location?: string, 
    season?: string
  ): Promise<CategorizedTips> {
    if (!tips || !Array.isArray(tips)) {
      return { planting: [], maintenance: [], harvest: [], general: [] };
    }

    const categorized: CategorizedTips = {
      planting: [],
      maintenance: [],
      harvest: [],
      general: []
    };

    tips.forEach(tip => {
      if (!tip || typeof tip !== 'string') return;

      const cleanTip = tip.trim();
      if (cleanTip.length < 10) return; // Skip very short tips

      const lowerTip = cleanTip.toLowerCase();

      // Categorize based on keywords
      if (lowerTip.includes('plant') || lowerTip.includes('seed') || 
          lowerTip.includes('sow') || lowerTip.includes('transplant')) {
        categorized.planting.push(cleanTip);
      } else if (lowerTip.includes('fertiliz') || lowerTip.includes('weed') || 
                 lowerTip.includes('irrigat') || lowerTip.includes('spray') ||
                 lowerTip.includes('maintain') || lowerTip.includes('care')) {
        categorized.maintenance.push(cleanTip);
      } else if (lowerTip.includes('harvest') || lowerTip.includes('pick') || 
                 lowerTip.includes('collect') || lowerTip.includes('gather')) {
        categorized.harvest.push(cleanTip);
      } else {
        categorized.general.push(cleanTip);
      }
    });

    // Limit each category to prevent information overload
    categorized.planting = categorized.planting.slice(0, 3);
    categorized.maintenance = categorized.maintenance.slice(0, 4);
    categorized.harvest = categorized.harvest.slice(0, 2);
    categorized.general = categorized.general.slice(0, 3);

    // Try AI enhancement if context is available
    if (location && season) {
      try {
        const aiSummarizedTips = await aiSummarizationService.summarizeManagementTips(
          tips,
          location,
          season
        );
        
        // Convert AI results back to CategorizedTips format
        return {
          planting: aiSummarizedTips.planting.map(tip => tip.summary),
          maintenance: aiSummarizedTips.maintenance.map(tip => tip.summary),
          harvest: aiSummarizedTips.harvest.map(tip => tip.summary),
          general: aiSummarizedTips.general.map(tip => tip.summary),
        };
      } catch (error) {
        console.warn('AI management tips summarization failed, using fallback:', error);
      }
    }

    return categorized;
  }

  /**
   * Prioritize and filter crop recommendations
   * Enhanced with AI summarization capabilities
   */
  async prioritizeRecommendations(
    recs: any[], 
    location?: string, 
    season?: string, 
    weatherData?: any
  ): Promise<PrioritizedRecommendation[]> {
    if (!recs || !Array.isArray(recs)) {
      return [];
    }

    const prioritizedRecs = recs
      .filter(rec => rec && rec.crop_name && typeof rec.score === 'number')
      .map(rec => ({
        ...rec,
        priority: this.calculateRecommendationPriority(rec),
        filtered_recommendations: this.filterRecommendationText(rec.guide_recommendations || [])
      }))
      .sort((a, b) => b.priority - a.priority);

    // Try AI enhancement if context is available
    if (location && season && weatherData) {
      try {
        const aiEnhancedRecs = await aiSummarizationService.enhanceCropRecommendations(
          prioritizedRecs.slice(0, 5), // Only enhance top 5 for efficiency
          location,
          season,
          weatherData
        );
        
        // Merge AI enhancements with existing recommendations
        return prioritizedRecs.map(rec => {
          const aiEnhanced = aiEnhancedRecs.find(aiRec => aiRec.crop_name === rec.crop_name);
          if (aiEnhanced) {
            return {
              ...rec,
              ai_summary: aiEnhanced.ai_summary,
              key_benefits: aiEnhanced.key_benefits,
              potential_challenges: aiEnhanced.potential_challenges,
              actionable_steps: aiEnhanced.actionable_steps,
              seasonal_advice: aiEnhanced.seasonal_advice,
              confidence_score: aiEnhanced.confidence_score,
            };
          }
          return rec;
        });
      } catch (error) {
        console.warn('AI recommendation enhancement failed, using fallback:', error);
      }
    }

    return prioritizedRecs;
  }

  /**
   * Calculate priority score for recommendations
   */
  private calculateRecommendationPriority(rec: any): number {
    let priority = rec.score || 0;

    // Boost priority for excellent suitability
    if (rec.suitability_level === 'excellent') {
      priority += 20;
    } else if (rec.suitability_level === 'very_good') {
      priority += 10;
    }

    // Boost priority for excellent matches
    if (rec.rainfall_match === 'excellent') priority += 5;
    if (rec.temperature_match === 'excellent') priority += 5;
    if (rec.season_suitability === 'excellent') priority += 5;

    return Math.min(priority, 100); // Cap at 100
  }

  /**
   * Filter recommendation text to remove database fragments
   */
  private filterRecommendationText(recommendations: string[]): string[] {
    if (!recommendations || !Array.isArray(recommendations)) {
      return [];
    }

    return recommendations
      .filter(rec => this.isValidRecommendationText(rec))
      .slice(0, 3); // Limit to top 3 recommendations
  }

  /**
   * Check if recommendation text is valid
   */
  private isValidRecommendationText(text: string): boolean {
    if (!text || typeof text !== 'string') {
      return false;
    }

    const cleanText = text.trim();
    
    // Must be reasonable length
    if (cleanText.length < 15 || cleanText.length > 200) {
      return false;
    }

    // Must not be database-like
    const databasePatterns = [
      /^[0-9]+\./, // Starts with numbers
      /^[A-Z_]+:/, // Database field names
      /^table|column|row|id:/i, // Database terms
    ];

    for (const pattern of databasePatterns) {
      if (pattern.test(cleanText)) {
        return false;
      }
    }

    return true;
  }

  /**
   * Comprehensive data processing pipeline
   * Aligns with bot's AI processing logic
   */
  async processComprehensiveData(
    rawData: any,
    location: string,
    season: string,
    weatherData: any
  ): Promise<any> {
    try {
      // Comprehensive content validation
      const validation = contentValidationService.validateCropRecommendations(rawData);
      const qualityMetrics = contentValidationService.getContentQualityMetrics(rawData);
      
      if (!validation.isValid) {
        console.warn('Content validation failed:', validation.errors);
        // Log quality metrics for monitoring
        console.warn('Data quality metrics:', qualityMetrics);
      }

      // Log validation results for monitoring
      console.log('Content validation results:', {
        isValid: validation.isValid,
        errorCount: validation.errors.length,
        warningCount: validation.warnings.length,
        qualityScore: validation.qualityScore,
        qualityMetrics
      });

      // Process all components with AI enhancement
      const [processedRisks, processedTips, processedRecommendations] = await Promise.all([
        this.processRiskAssessment(
          rawData.risk_assessment?.weather_risks || [],
          location,
          season,
          weatherData
        ),
        this.summarizeManagementTips(
          rawData.management_tips || [],
          location,
          season
        ),
        this.prioritizeRecommendations(
          rawData.recommendations || [],
          location,
          season,
          weatherData
        )
      ]);

      // Return enhanced data structure
      return {
        ...rawData,
        risk_assessment: rawData.risk_assessment ? {
          ...rawData.risk_assessment,
          weather_risks: processedRisks,
          ai_enhanced: true,
        } : null,
        management_tips: processedTips,
        recommendations: processedRecommendations,
        processing_metadata: {
          location,
          season,
          timestamp: new Date().toISOString(),
          ai_enhanced: true,
          processing_version: '2.0',
          validation: {
            isValid: validation.isValid,
            qualityScore: validation.qualityScore,
            errorCount: validation.errors.length,
            warningCount: validation.warnings.length,
            qualityMetrics
          }
        }
      };
    } catch (error) {
      console.error('Comprehensive data processing failed:', error);
      // Return original data with fallback processing
      return {
        ...rawData,
        risk_assessment: rawData.risk_assessment ? {
          ...rawData.risk_assessment,
          weather_risks: await this.processRiskAssessment(rawData.risk_assessment.weather_risks || []),
        } : null,
        management_tips: await this.summarizeManagementTips(rawData.management_tips || []),
        recommendations: await this.prioritizeRecommendations(rawData.recommendations || []),
        processing_metadata: {
          location,
          season,
          timestamp: new Date().toISOString(),
          ai_enhanced: false,
          error: error.message,
          processing_version: '2.0-fallback',
        }
      };
    }
  }

  /**
   * Validate API response structure
   */
  validateApiResponse(data: any): { isValid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (!data) {
      errors.push('No data received from API');
      return { isValid: false, errors };
    }

    if (!data.recommendations || !Array.isArray(data.recommendations)) {
      errors.push('Invalid recommendations data structure');
    }

    if (data.risk_assessment && !data.risk_assessment.weather_risks) {
      errors.push('Missing weather risks in risk assessment');
    }

    if (data.management_tips && !Array.isArray(data.management_tips)) {
      errors.push('Invalid management tips data structure');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }
}

// Export singleton instance
export const cropDataProcessor = new CropDataProcessor();
