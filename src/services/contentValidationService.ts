/**
 * Content Validation Service
 * Ensures data quality and validates content before processing
 * Aligns with bot's data validation logic
 */

export interface ValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
  suggestions: string[];
  qualityScore: number; // 0-1 scale
}

export interface ContentQualityMetrics {
  completeness: number; // 0-1
  accuracy: number; // 0-1
  relevance: number; // 0-1
  clarity: number; // 0-1
  overall: number; // 0-1
}

export interface ValidationRules {
  minRiskTextLength: number;
  maxRiskTextLength: number;
  minManagementTipLength: number;
  maxManagementTipLength: number;
  maxRecommendationsCount: number;
  requiredFields: string[];
  forbiddenPatterns: RegExp[];
  agriculturalKeywords: string[];
}

export class ContentValidationService {
  private rules: ValidationRules;

  constructor() {
    this.rules = {
      minRiskTextLength: 10,
      maxRiskTextLength: 500,
      minManagementTipLength: 15,
      maxManagementTipLength: 200,
      maxRecommendationsCount: 20,
      requiredFields: ['crop_name', 'score', 'suitability_level'],
      forbiddenPatterns: [
        /^[0-9]+\./, // Starts with numbers
        /^[A-Z_]+:/, // Database field names
        /^table|column|row|id:/i, // Database terms
        /^[{}[\]()]+/, // JSON-like structures
        /^[a-z]+_[a-z]+/, // Snake_case patterns
        /^[A-Z]+_[A-Z]+/, // CONSTANT_CASE patterns
        /^[0-9]+$/, // Pure numbers
        /^[^a-zA-Z]*$/, // No letters
      ],
      agriculturalKeywords: [
        'rain', 'drought', 'flood', 'temperature', 'weather', 'climate',
        'pest', 'disease', 'insect', 'fungus', 'bacteria', 'virus',
        'crop', 'plant', 'seed', 'soil', 'fertilizer', 'irrigation',
        'harvest', 'yield', 'growth', 'maturity', 'planting', 'cultivation',
        'maize', 'groundnut', 'bean', 'cassava', 'sorghum', 'rice',
        'malawi', 'agriculture', 'farming', 'farmer'
      ]
    };
  }

  /**
   * Validate crop recommendations data structure
   */
  validateCropRecommendations(data: any): ValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];
    const suggestions: string[] = [];

    // Check if data exists
    if (!data) {
      errors.push('No data received from API');
      return this.createValidationResult(false, errors, warnings, suggestions);
    }

    // Validate recommendations array
    if (!data.recommendations || !Array.isArray(data.recommendations)) {
      errors.push('Invalid recommendations data structure');
    } else {
      // Validate each recommendation
      data.recommendations.forEach((rec: any, index: number) => {
        const recValidation = this.validateRecommendation(rec, index);
        errors.push(...recValidation.errors);
        warnings.push(...recValidation.warnings);
        suggestions.push(...recValidation.suggestions);
      });

      // Check recommendation count
      if (data.recommendations.length > this.rules.maxRecommendationsCount) {
        warnings.push(`Too many recommendations (${data.recommendations.length}), consider pagination`);
      }
    }

    // Validate risk assessment
    if (data.risk_assessment) {
      const riskValidation = this.validateRiskAssessment(data.risk_assessment);
      errors.push(...riskValidation.errors);
      warnings.push(...riskValidation.warnings);
      suggestions.push(...riskValidation.suggestions);
    }

    // Validate management tips
    if (data.management_tips) {
      const tipsValidation = this.validateManagementTips(data.management_tips);
      errors.push(...tipsValidation.errors);
      warnings.push(...tipsValidation.warnings);
      suggestions.push(...tipsValidation.suggestions);
    }

    // Validate environmental summary
    if (data.environmental_summary) {
      const envValidation = this.validateEnvironmentalSummary(data.environmental_summary);
      errors.push(...envValidation.errors);
      warnings.push(...envValidation.warnings);
      suggestions.push(...envValidation.suggestions);
    }

    const isValid = errors.length === 0;
    const qualityScore = this.calculateQualityScore(data, errors, warnings);

    return this.createValidationResult(isValid, errors, warnings, suggestions, qualityScore);
  }

  /**
   * Validate individual recommendation
   */
  private validateRecommendation(rec: any, index: number): ValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];
    const suggestions: string[] = [];

    // Check required fields
    this.rules.requiredFields.forEach(field => {
      if (!rec[field]) {
        errors.push(`Recommendation ${index + 1}: Missing required field '${field}'`);
      }
    });

    // Validate crop name
    if (rec.crop_name) {
      if (typeof rec.crop_name !== 'string' || rec.crop_name.trim().length === 0) {
        errors.push(`Recommendation ${index + 1}: Invalid crop name`);
      } else if (!this.containsAgriculturalKeywords(rec.crop_name)) {
        warnings.push(`Recommendation ${index + 1}: Crop name '${rec.crop_name}' may not be agricultural`);
      }
    }

    // Validate score
    if (rec.score !== undefined) {
      if (typeof rec.score !== 'number' || rec.score < 0 || rec.score > 100) {
        errors.push(`Recommendation ${index + 1}: Invalid score (must be 0-100)`);
      }
    }

    // Validate suitability level
    if (rec.suitability_level) {
      const validLevels = ['excellent', 'very_good', 'good', 'fair', 'poor'];
      if (!validLevels.includes(rec.suitability_level)) {
        errors.push(`Recommendation ${index + 1}: Invalid suitability level '${rec.suitability_level}'`);
      }
    }

    // Validate guide recommendations
    if (rec.guide_recommendations && Array.isArray(rec.guide_recommendations)) {
      rec.guide_recommendations.forEach((tip: string, tipIndex: number) => {
        const tipValidation = this.validateTextContent(tip, `Recommendation ${index + 1}, Tip ${tipIndex + 1}`);
        errors.push(...tipValidation.errors);
        warnings.push(...tipValidation.warnings);
      });
    }

    return this.createValidationResult(errors.length === 0, errors, warnings, suggestions);
  }

  /**
   * Validate risk assessment
   */
  private validateRiskAssessment(riskAssessment: any): ValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];
    const suggestions: string[] = [];

    // Validate overall risk level
    if (riskAssessment.overall_risk_level) {
      const validLevels = ['low', 'moderate', 'medium', 'high', 'critical'];
      if (!validLevels.includes(riskAssessment.overall_risk_level.toLowerCase())) {
        errors.push(`Invalid overall risk level: '${riskAssessment.overall_risk_level}'`);
      }
    }

    // Validate weather risks
    if (riskAssessment.weather_risks && Array.isArray(riskAssessment.weather_risks)) {
      if (riskAssessment.weather_risks.length > 15) {
        warnings.push(`Too many weather risks (${riskAssessment.weather_risks.length}), consider filtering`);
      }

      riskAssessment.weather_risks.forEach((risk: string, index: number) => {
        const riskValidation = this.validateTextContent(risk, `Weather Risk ${index + 1}`);
        errors.push(...riskValidation.errors);
        warnings.push(...riskValidation.warnings);
      });
    }

    // Validate pest risks
    if (riskAssessment.pest_risks && Array.isArray(riskAssessment.pest_risks)) {
      riskAssessment.pest_risks.forEach((risk: string, index: number) => {
        const riskValidation = this.validateTextContent(risk, `Pest Risk ${index + 1}`);
        errors.push(...riskValidation.errors);
        warnings.push(...riskValidation.warnings);
      });
    }

    return this.createValidationResult(errors.length === 0, errors, warnings, suggestions);
  }

  /**
   * Validate management tips
   */
  private validateManagementTips(tips: any): ValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];
    const suggestions: string[] = [];

    if (!Array.isArray(tips)) {
      errors.push('Management tips must be an array');
      return this.createValidationResult(false, errors, warnings, suggestions);
    }

    if (tips.length > 20) {
      warnings.push(`Too many management tips (${tips.length}), consider categorization`);
    }

    tips.forEach((tip: string, index: number) => {
      const tipValidation = this.validateTextContent(tip, `Management Tip ${index + 1}`);
      errors.push(...tipValidation.errors);
      warnings.push(...tipValidation.warnings);
    });

    return this.createValidationResult(errors.length === 0, errors, warnings, suggestions);
  }

  /**
   * Validate environmental summary
   */
  private validateEnvironmentalSummary(envSummary: any): ValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];
    const suggestions: string[] = [];

    // Validate temperature
    if (envSummary.current_temperature !== undefined) {
      if (typeof envSummary.current_temperature !== 'number' || 
          envSummary.current_temperature < -50 || 
          envSummary.current_temperature > 60) {
        errors.push('Invalid temperature value');
      }
    }

    // Validate rainfall
    if (envSummary.total_7day_rainfall !== undefined) {
      if (typeof envSummary.total_7day_rainfall !== 'number' || 
          envSummary.total_7day_rainfall < 0 || 
          envSummary.total_7day_rainfall > 1000) {
        errors.push('Invalid rainfall value');
      }
    }

    // Validate humidity
    if (envSummary.humidity !== undefined) {
      if (typeof envSummary.humidity !== 'number' || 
          envSummary.humidity < 0 || 
          envSummary.humidity > 100) {
        errors.push('Invalid humidity value');
      }
    }

    return this.createValidationResult(errors.length === 0, errors, warnings, suggestions);
  }

  /**
   * Validate text content
   */
  private validateTextContent(text: string, context: string): ValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];
    const suggestions: string[] = [];

    if (typeof text !== 'string') {
      errors.push(`${context}: Text must be a string`);
      return this.createValidationResult(false, errors, warnings, suggestions);
    }

    const trimmedText = text.trim();

    // Check for forbidden patterns
    this.rules.forbiddenPatterns.forEach(pattern => {
      if (pattern.test(trimmedText)) {
        errors.push(`${context}: Contains forbidden pattern (likely database fragment)`);
      }
    });

    // Check length constraints (context-specific)
    if (context.includes('Risk')) {
      if (trimmedText.length < this.rules.minRiskTextLength) {
        errors.push(`${context}: Text too short (minimum ${this.rules.minRiskTextLength} characters)`);
      }
      if (trimmedText.length > this.rules.maxRiskTextLength) {
        warnings.push(`${context}: Text very long (${trimmedText.length} characters)`);
      }
    } else if (context.includes('Tip')) {
      if (trimmedText.length < this.rules.minManagementTipLength) {
        errors.push(`${context}: Text too short (minimum ${this.rules.minManagementTipLength} characters)`);
      }
      if (trimmedText.length > this.rules.maxManagementTipLength) {
        warnings.push(`${context}: Text very long (${trimmedText.length} characters)`);
      }
    }

    // Check for agricultural content
    if (!this.containsAgriculturalKeywords(trimmedText)) {
      warnings.push(`${context}: May not contain agricultural content`);
    }

    // Check for actionable content
    if (!this.isActionableContent(trimmedText)) {
      suggestions.push(`${context}: Consider making content more actionable`);
    }

    return this.createValidationResult(errors.length === 0, errors, warnings, suggestions);
  }

  /**
   * Check if text contains agricultural keywords
   */
  private containsAgriculturalKeywords(text: string): boolean {
    const lowerText = text.toLowerCase();
    return this.rules.agriculturalKeywords.some(keyword => lowerText.includes(keyword));
  }

  /**
   * Check if content is actionable
   */
  private isActionableContent(text: string): boolean {
    const actionWords = ['apply', 'use', 'plant', 'harvest', 'monitor', 'control', 'prepare', 'ensure'];
    const lowerText = text.toLowerCase();
    return actionWords.some(word => lowerText.includes(word));
  }

  /**
   * Calculate overall quality score
   */
  private calculateQualityScore(data: any, errors: string[], warnings: string[]): number {
    let score = 1.0;

    // Deduct for errors
    score -= errors.length * 0.2;

    // Deduct for warnings
    score -= warnings.length * 0.05;

    // Bonus for complete data
    if (data.recommendations && data.recommendations.length > 0) score += 0.1;
    if (data.risk_assessment) score += 0.1;
    if (data.management_tips && data.management_tips.length > 0) score += 0.1;
    if (data.environmental_summary) score += 0.1;

    return Math.max(0, Math.min(1, score));
  }

  /**
   * Create validation result
   */
  private createValidationResult(
    isValid: boolean, 
    errors: string[], 
    warnings: string[], 
    suggestions: string[], 
    qualityScore?: number
  ): ValidationResult {
    return {
      isValid,
      errors: [...new Set(errors)], // Remove duplicates
      warnings: [...new Set(warnings)],
      suggestions: [...new Set(suggestions)],
      qualityScore: qualityScore ?? (isValid ? 0.8 : 0.3)
    };
  }

  /**
   * Get content quality metrics
   */
  getContentQualityMetrics(data: any): ContentQualityMetrics {
    const validation = this.validateCropRecommendations(data);
    
    const completeness = this.calculateCompleteness(data);
    const accuracy = this.calculateAccuracy(data, validation.errors);
    const relevance = this.calculateRelevance(data);
    const clarity = this.calculateClarity(data);

    return {
      completeness,
      accuracy,
      relevance,
      clarity,
      overall: (completeness + accuracy + relevance + clarity) / 4
    };
  }

  private calculateCompleteness(data: any): number {
    let score = 0;
    const requiredComponents = ['recommendations', 'risk_assessment', 'management_tips', 'environmental_summary'];
    
    requiredComponents.forEach(component => {
      if (data[component]) score += 0.25;
    });

    return score;
  }

  private calculateAccuracy(data: any, errors: string[]): number {
    const errorCount = errors.length;
    if (errorCount === 0) return 1.0;
    if (errorCount <= 2) return 0.8;
    if (errorCount <= 5) return 0.6;
    return 0.3;
  }

  private calculateRelevance(data: any): number {
    let score = 0.5; // Base score

    // Check if recommendations contain agricultural content
    if (data.recommendations && Array.isArray(data.recommendations)) {
      const agriculturalCount = data.recommendations.filter((rec: any) => 
        this.containsAgriculturalKeywords(rec.crop_name || '')
      ).length;
      score += (agriculturalCount / data.recommendations.length) * 0.5;
    }

    return Math.min(1, score);
  }

  private calculateClarity(data: any): number {
    let score = 0.5; // Base score

    // Check text clarity in various components
    const textComponents = [
      ...(data.risk_assessment?.weather_risks || []),
      ...(data.management_tips || []),
      ...(data.recommendations?.map((r: any) => r.guide_recommendations || []).flat() || [])
    ];

    const clearTextCount = textComponents.filter(text => 
      typeof text === 'string' && 
      text.length > 20 && 
      text.length < 200 &&
      !this.rules.forbiddenPatterns.some(pattern => pattern.test(text))
    ).length;

    if (textComponents.length > 0) {
      score += (clearTextCount / textComponents.length) * 0.5;
    }

    return Math.min(1, score);
  }
}

// Export singleton instance
export const contentValidationService = new ContentValidationService();
