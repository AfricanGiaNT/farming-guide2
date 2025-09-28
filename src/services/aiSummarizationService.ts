/**
 * AI Summarization Service
 * Provides AI-powered data summarization and enhancement for crop recommendations
 * Aligns with the bot's AI processing logic
 */

export interface AISummarizationConfig {
  enableAI: boolean;
  maxTokens: number;
  temperature: number;
  model: string;
  cacheEnabled: boolean;
}

export interface SummarizedRisk {
  id: string;
  originalText: string;
  summary: string;
  category: 'weather' | 'pest' | 'disease' | 'other';
  severity: 'low' | 'medium' | 'high';
  priority: number;
  actionableAdvice: string;
  confidence: number;
}

export interface SummarizedManagementTips {
  planting: Array<{
    original: string;
    summary: string;
    priority: number;
    actionable: boolean;
  }>;
  maintenance: Array<{
    original: string;
    summary: string;
    priority: number;
    actionable: boolean;
  }>;
  harvest: Array<{
    original: string;
    summary: string;
    priority: number;
    actionable: boolean;
  }>;
  general: Array<{
    original: string;
    summary: string;
    priority: number;
    actionable: boolean;
  }>;
}

export interface EnhancedRecommendation {
  crop_name: string;
  score: number;
  suitability_level: string;
  ai_summary: string;
  key_benefits: string[];
  potential_challenges: string[];
  actionable_steps: string[];
  seasonal_advice: string;
  confidence_score: number;
}

export class AISummarizationService {
  private config: AISummarizationConfig;
  private cache: Map<string, any> = new Map();
  private apiKey: string | null = null;

  constructor(config: Partial<AISummarizationConfig> = {}) {
    this.config = {
      enableAI: config.enableAI ?? false, // Default to false for now
      maxTokens: config.maxTokens ?? 200,
      temperature: config.temperature ?? 0.3,
      model: config.model ?? 'gpt-3.5-turbo',
      cacheEnabled: config.cacheEnabled ?? true,
    };

    // Get API key from environment
    this.apiKey = process.env.VITE_OPENAI_API_KEY || null;
  }

  /**
   * Summarize weather risks using AI
   */
  async summarizeWeatherRisks(
    risks: string[],
    location: string,
    season: string,
    weatherData: any
  ): Promise<SummarizedRisk[]> {
    if (!this.config.enableAI || !this.apiKey) {
      return this.fallbackRiskSummarization(risks);
    }

    try {
      const cacheKey = this.generateCacheKey('risks', risks, location, season);
      
      if (this.config.cacheEnabled && this.cache.has(cacheKey)) {
        return this.cache.get(cacheKey);
      }

      const prompt = this.createRiskSummarizationPrompt(risks, location, season, weatherData);
      const aiResponse = await this.callOpenAI(prompt);
      const summarizedRisks = this.parseRiskSummarizationResponse(aiResponse, risks);

      if (this.config.cacheEnabled) {
        this.cache.set(cacheKey, summarizedRisks);
      }

      return summarizedRisks;
    } catch (error) {
      console.warn('AI risk summarization failed, using fallback:', error);
      return this.fallbackRiskSummarization(risks);
    }
  }

  /**
   * Summarize management tips using AI
   */
  async summarizeManagementTips(
    tips: string[],
    location: string,
    season: string
  ): Promise<SummarizedManagementTips> {
    if (!this.config.enableAI || !this.apiKey) {
      return this.fallbackManagementTipsSummarization(tips);
    }

    try {
      const cacheKey = this.generateCacheKey('tips', tips, location, season);
      
      if (this.config.cacheEnabled && this.cache.has(cacheKey)) {
        return this.cache.get(cacheKey);
      }

      const prompt = this.createManagementTipsPrompt(tips, location, season);
      const aiResponse = await this.callOpenAI(prompt);
      const summarizedTips = this.parseManagementTipsResponse(aiResponse, tips);

      if (this.config.cacheEnabled) {
        this.cache.set(cacheKey, summarizedTips);
      }

      return summarizedTips;
    } catch (error) {
      console.warn('AI management tips summarization failed, using fallback:', error);
      return this.fallbackManagementTipsSummarization(tips);
    }
  }

  /**
   * Enhance crop recommendations with AI insights
   */
  async enhanceCropRecommendations(
    recommendations: any[],
    location: string,
    season: string,
    weatherData: any
  ): Promise<EnhancedRecommendation[]> {
    if (!this.config.enableAI || !this.apiKey) {
      return this.fallbackRecommendationEnhancement(recommendations);
    }

    try {
      const cacheKey = this.generateCacheKey('recommendations', recommendations, location, season);
      
      if (this.config.cacheEnabled && this.cache.has(cacheKey)) {
        return this.cache.get(cacheKey);
      }

      const prompt = this.createRecommendationEnhancementPrompt(recommendations, location, season, weatherData);
      const aiResponse = await this.callOpenAI(prompt);
      const enhancedRecommendations = this.parseRecommendationEnhancementResponse(aiResponse, recommendations);

      if (this.config.cacheEnabled) {
        this.cache.set(cacheKey, enhancedRecommendations);
      }

      return enhancedRecommendations;
    } catch (error) {
      console.warn('AI recommendation enhancement failed, using fallback:', error);
      return this.fallbackRecommendationEnhancement(recommendations);
    }
  }

  /**
   * Create risk summarization prompt
   */
  private createRiskSummarizationPrompt(
    risks: string[],
    location: string,
    season: string,
    weatherData: any
  ): string {
    const weatherContext = `
Current Conditions:
- Temperature: ${weatherData?.temperature || 25}°C
- Rainfall: ${weatherData?.rainfall || 0}mm
- Humidity: ${weatherData?.humidity || 50}%
- Season: ${season}
`;

    return `As an agricultural advisor for ${location}, analyze these weather risks and provide concise summaries:

${weatherContext}

Weather Risks to Analyze:
${risks.map((risk, i) => `${i + 1}. ${risk}`).join('\n')}

For each risk, provide:
1. Concise summary (max 50 words)
2. Category (weather/pest/disease/other)
3. Severity (low/medium/high)
4. Priority (1-10)
5. Actionable advice (max 30 words)
6. Confidence (0-1)

Format as JSON array with fields: summary, category, severity, priority, actionableAdvice, confidence`;
  }

  /**
   * Create management tips prompt
   */
  private createManagementTipsPrompt(tips: string[], location: string, season: string): string {
    return `As an agricultural advisor for ${location} during ${season}, categorize and summarize these management tips:

Management Tips:
${tips.map((tip, i) => `${i + 1}. ${tip}`).join('\n')}

Categorize each tip into: planting, maintenance, harvest, or general
For each tip, provide:
1. Concise summary (max 40 words)
2. Priority (1-10)
3. Whether it's actionable (true/false)

Format as JSON with categories as keys, each containing arrays of objects with fields: summary, priority, actionable`;
  }

  /**
   * Create recommendation enhancement prompt
   */
  private createRecommendationEnhancementPrompt(
    recommendations: any[],
    location: string,
    season: string,
    weatherData: any
  ): string {
    const topCrops = recommendations.slice(0, 3);
    
    return `As an agricultural advisor for ${location} during ${season}, enhance these crop recommendations:

Current Conditions:
- Temperature: ${weatherData?.temperature || 25}°C
- Rainfall: ${weatherData?.rainfall || 0}mm
- Season: ${season}

Top Crop Recommendations:
${topCrops.map((crop, i) => `${i + 1}. ${crop.crop_name} (Score: ${crop.score}%)`).join('\n')}

For each crop, provide:
1. AI summary (max 60 words)
2. Key benefits (3-5 points)
3. Potential challenges (2-3 points)
4. Actionable steps (3-4 steps)
5. Seasonal advice (max 40 words)
6. Confidence score (0-1)

Format as JSON array with fields: crop_name, ai_summary, key_benefits, potential_challenges, actionable_steps, seasonal_advice, confidence_score`;
  }

  /**
   * Call OpenAI API with performance monitoring
   */
  private async callOpenAI(prompt: string): Promise<string> {
    if (!this.apiKey) {
      throw new Error('OpenAI API key not available');
    }

    const startTime = performance.now()
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.apiKey}`,
      },
      body: JSON.stringify({
        model: this.config.model,
        messages: [
          {
            role: 'system',
            content: 'You are a practical agricultural advisor specializing in Malawi farming. Provide concise, actionable advice focused on local conditions and resources. Always respond with valid JSON.'
          },
          {
            role: 'user',
            content: prompt
          }
        ],
        max_tokens: this.config.maxTokens,
        temperature: this.config.temperature,
      }),
    });

    if (!response.ok) {
      throw new Error(`OpenAI API error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    const endTime = performance.now()
    const duration = endTime - startTime
    
    // Log performance metrics
    console.log(`OpenAI API call completed in ${duration.toFixed(2)}ms`)
    
    return data.choices[0]?.message?.content || '';
  }

  /**
   * Parse AI response for risk summarization
   */
  private parseRiskSummarizationResponse(response: string, originalRisks: string[]): SummarizedRisk[] {
    try {
      const parsed = JSON.parse(response);
      return parsed.map((item: any, index: number) => ({
        id: `risk_${index}`,
        originalText: originalRisks[index] || '',
        summary: item.summary || '',
        category: item.category || 'other',
        severity: item.severity || 'medium',
        priority: item.priority || 5,
        actionableAdvice: item.actionableAdvice || '',
        confidence: item.confidence || 0.7,
      }));
    } catch (error) {
      console.warn('Failed to parse AI risk response:', error);
      return this.fallbackRiskSummarization(originalRisks);
    }
  }

  /**
   * Parse AI response for management tips
   */
  private parseManagementTipsResponse(response: string, originalTips: string[]): SummarizedManagementTips {
    try {
      const parsed = JSON.parse(response);
      return {
        planting: parsed.planting || [],
        maintenance: parsed.maintenance || [],
        harvest: parsed.harvest || [],
        general: parsed.general || [],
      };
    } catch (error) {
      console.warn('Failed to parse AI management tips response:', error);
      return this.fallbackManagementTipsSummarization(originalTips);
    }
  }

  /**
   * Parse AI response for recommendation enhancement
   */
  private parseRecommendationEnhancementResponse(response: string, originalRecommendations: any[]): EnhancedRecommendation[] {
    try {
      const parsed = JSON.parse(response);
      return parsed.map((item: any, index: number) => ({
        ...originalRecommendations[index],
        ai_summary: item.ai_summary || '',
        key_benefits: item.key_benefits || [],
        potential_challenges: item.potential_challenges || [],
        actionable_steps: item.actionable_steps || [],
        seasonal_advice: item.seasonal_advice || '',
        confidence_score: item.confidence_score || 0.7,
      }));
    } catch (error) {
      console.warn('Failed to parse AI recommendation response:', error);
      return this.fallbackRecommendationEnhancement(originalRecommendations);
    }
  }

  /**
   * Fallback risk summarization (no AI)
   */
  private fallbackRiskSummarization(risks: string[]): SummarizedRisk[] {
    return risks.slice(0, 5).map((risk, index) => ({
      id: `risk_${index}`,
      originalText: risk,
      summary: risk.length > 50 ? risk.substring(0, 47) + '...' : risk,
      category: this.categorizeRisk(risk),
      severity: this.assessSeverity(risk),
      priority: this.calculatePriority(risk),
      actionableAdvice: this.generateActionableAdvice(risk),
      confidence: 0.6,
    }));
  }

  /**
   * Fallback management tips summarization (no AI)
   */
  private fallbackManagementTipsSummarization(tips: string[]): SummarizedManagementTips {
    const categorized = {
      planting: [] as any[],
      maintenance: [] as any[],
      harvest: [] as any[],
      general: [] as any[],
    };

    tips.forEach((tip, index) => {
      const category = this.categorizeManagementTip(tip);
      categorized[category].push({
        original: tip,
        summary: tip.length > 40 ? tip.substring(0, 37) + '...' : tip,
        priority: this.calculateTipPriority(tip),
        actionable: this.isActionableTip(tip),
      });
    });

    return categorized;
  }

  /**
   * Fallback recommendation enhancement (no AI)
   */
  private fallbackRecommendationEnhancement(recommendations: any[]): EnhancedRecommendation[] {
    return recommendations.map(rec => ({
      ...rec,
      ai_summary: `${rec.crop_name} is ${rec.suitability_level} for current conditions with ${rec.score}% suitability score.`,
      key_benefits: [
        `High ${rec.rainfall_match} rainfall match`,
        `Excellent ${rec.temperature_match} temperature suitability`,
        `Good ${rec.season_suitability} seasonal fit`
      ],
      potential_challenges: [
        'Monitor weather conditions regularly',
        'Ensure proper soil preparation',
        'Follow recommended planting schedule'
      ],
      actionable_steps: [
        'Prepare soil according to recommendations',
        'Source quality seeds',
        'Follow planting schedule',
        'Monitor crop development'
      ],
      seasonal_advice: `Best planted during ${rec.planting_time || 'optimal season'}`,
      confidence_score: 0.6,
    }));
  }

  /**
   * Helper methods for categorization and analysis
   */
  private categorizeRisk(risk: string): 'weather' | 'pest' | 'disease' | 'other' {
    const lower = risk.toLowerCase();
    if (lower.includes('rain') || lower.includes('drought') || lower.includes('temperature')) return 'weather';
    if (lower.includes('pest') || lower.includes('insect')) return 'pest';
    if (lower.includes('disease') || lower.includes('fungus')) return 'disease';
    return 'other';
  }

  private assessSeverity(risk: string): 'low' | 'medium' | 'high' {
    const lower = risk.toLowerCase();
    if (lower.includes('severe') || lower.includes('critical')) return 'high';
    if (lower.includes('moderate') || lower.includes('possible')) return 'medium';
    return 'low';
  }

  private calculatePriority(risk: string): number {
    const severity = this.assessSeverity(risk);
    const category = this.categorizeRisk(risk);
    
    let priority = 5; // Base priority
    if (severity === 'high') priority += 3;
    if (severity === 'medium') priority += 1;
    if (category === 'weather') priority += 2;
    if (category === 'disease') priority += 1;
    
    return Math.min(priority, 10);
  }

  private generateActionableAdvice(risk: string): string {
    const category = this.categorizeRisk(risk);
    const severity = this.assessSeverity(risk);
    
    if (category === 'weather') {
      return severity === 'high' ? 'Take immediate protective measures' : 'Monitor conditions closely';
    }
    if (category === 'pest') {
      return 'Implement pest control measures';
    }
    if (category === 'disease') {
      return 'Apply preventive treatments';
    }
    return 'Follow recommended practices';
  }

  private categorizeManagementTip(tip: string): 'planting' | 'maintenance' | 'harvest' | 'general' {
    const lower = tip.toLowerCase();
    if (lower.includes('plant') || lower.includes('seed')) return 'planting';
    if (lower.includes('fertiliz') || lower.includes('weed') || lower.includes('irrigat')) return 'maintenance';
    if (lower.includes('harvest') || lower.includes('pick')) return 'harvest';
    return 'general';
  }

  private calculateTipPriority(tip: string): number {
    const category = this.categorizeManagementTip(tip);
    let priority = 5;
    if (category === 'planting') priority += 2;
    if (category === 'maintenance') priority += 1;
    return Math.min(priority, 10);
  }

  private isActionableTip(tip: string): boolean {
    const lower = tip.toLowerCase();
    return lower.includes('apply') || lower.includes('use') || lower.includes('plant') || 
           lower.includes('harvest') || lower.includes('monitor') || lower.includes('control');
  }

  private generateCacheKey(type: string, data: any, location: string, season: string): string {
    const dataHash = JSON.stringify(data).slice(0, 100);
    return `${type}_${location}_${season}_${dataHash}`;
  }
}

// Export singleton instance
export const aiSummarizationService = new AISummarizationService({
  enableAI: false, // Start disabled, can be enabled via environment variable
  cacheEnabled: true,
});
