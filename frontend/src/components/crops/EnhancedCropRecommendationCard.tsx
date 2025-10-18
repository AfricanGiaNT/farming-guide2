import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card';
import { Sprout, TrendingUp, Calendar, Target, Droplets, Package, ArrowRight } from 'lucide-react';
import { CropRecommendation as ApiCropRecommendation } from '../../services/api';

interface EnhancedCropRecommendationCardProps {
  recommendation: ApiCropRecommendation;
  weatherData?: {
    temperature: number;
    rainfall: number;
    humidity: number;
  };
  historicalData?: {
    average_rainfall: number;
    wettest_month: string;
    driest_month: string;
  };
  onClick?: () => void;
}

const EnhancedCropRecommendationCard: React.FC<EnhancedCropRecommendationCardProps> = ({ 
  recommendation, 
  weatherData,
  historicalData,
  onClick 
}) => {
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-100';
    if (score >= 60) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  // Calculate weather-based yield potential
  const calculateWeatherBasedYield = () => {
    if (!weatherData || !recommendation.crop_data?.water_requirements) return null;
    
    const optimalRainfall = recommendation.crop_data.water_requirements.optimal_rainfall || 0;
    const currentRainfall = weatherData.rainfall;
    
    if (optimalRainfall === 0) return null;
    
    const rainfallRatio = currentRainfall / optimalRainfall;
    let yieldMultiplier = 1;
    
    if (rainfallRatio >= 0.8 && rainfallRatio <= 1.2) {
      yieldMultiplier = 1.0; // Optimal
    } else if (rainfallRatio >= 0.6 && rainfallRatio < 0.8) {
      yieldMultiplier = 0.8; // Below optimal
    } else if (rainfallRatio > 1.2 && rainfallRatio <= 1.5) {
      yieldMultiplier = 0.9; // Above optimal
    } else {
      yieldMultiplier = 0.6; // Poor conditions
    }
    
    return `${Math.round(yieldMultiplier * 100)}%`;
  };

  // Calculate average rainfall required
  const getAverageRainfallRequired = () => {
    if (!recommendation.crop_data?.water_requirements) return null;
    
    const minRainfall = recommendation.crop_data.water_requirements.minimum_rainfall || 0;
    const maxRainfall = recommendation.crop_data.water_requirements.maximum_rainfall || 0;
    const optimalRainfall = recommendation.crop_data.water_requirements.optimal_rainfall || 0;
    
    if (minRainfall === 0 && maxRainfall === 0 && optimalRainfall === 0) return null;
    
    const avgRainfall = optimalRainfall || (minRainfall + maxRainfall) / 2;
    return `${avgRainfall.toFixed(0)}mm`;
  };

  // Get additional inputs needed
  const getAdditionalInputs = () => {
    const inputs = [];
    
    if (weatherData) {
      // Check if rainfall is below optimal
      if (recommendation.crop_data?.water_requirements?.optimal_rainfall) {
        const optimalRainfall = recommendation.crop_data.water_requirements.optimal_rainfall;
        if (weatherData.rainfall < optimalRainfall * 0.8) {
          inputs.push('Irrigation system');
        }
      }
      
      // Check temperature conditions
      if (recommendation.crop_data?.temperature_requirements) {
        const { minimum_temp, maximum_temp, optimal_temp } = recommendation.crop_data.temperature_requirements;
        if (weatherData.temperature < minimum_temp) {
          inputs.push('Greenhouse or protective covering');
        } else if (weatherData.temperature > maximum_temp) {
          inputs.push('Shade netting');
        }
      }
    }
    
    // Add common inputs based on crop type
    if (recommendation.crop_data?.category) {
      const category = recommendation.crop_data.category.toLowerCase();
      if (category.includes('vegetable') || category.includes('legume')) {
        inputs.push('Organic fertilizer', 'Pest control measures');
      } else if (category.includes('cereal') || category.includes('grain')) {
        inputs.push('NPK fertilizer', 'Weed control');
      }
    }
    
    return inputs.slice(0, 3); // Limit to 3 most important inputs
  };

  const weatherBasedYield = calculateWeatherBasedYield();
  const averageRainfallRequired = getAverageRainfallRequired();
  const additionalInputs = getAdditionalInputs();

  return (
    <Card onClick={onClick} className="hover:shadow-lg transition-all duration-200 cursor-pointer">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Sprout size={20} className="text-green-600" />
            {recommendation.crop_data?.name || recommendation.crop || 'Unknown Crop'}
          </CardTitle>
          <div className={`px-2 py-1 rounded-full text-xs font-bold ${getScoreColor(recommendation.score || recommendation.total_score || 0)}`}>
            {recommendation.score || recommendation.total_score || 0}%
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Yield Information */}
        <div className="grid grid-cols-2 gap-4">
          <div className="flex items-center gap-2">
            <Target size={16} className="text-gray-500" />
            <div>
              <p className="text-xs text-gray-500">Expected Yield</p>
              <p className="text-sm font-medium">{recommendation.yieldPotential || 'High'}</p>
            </div>
          </div>
          {weatherBasedYield && (
            <div className="flex items-center gap-2">
              <TrendingUp size={16} className="text-blue-500" />
              <div>
                <p className="text-xs text-gray-500">Weather-Based</p>
                <p className="text-sm font-medium text-blue-600">{weatherBasedYield}</p>
              </div>
            </div>
          )}
        </div>

        {/* Rainfall Requirements */}
        {averageRainfallRequired && (
          <div className="flex items-center gap-2">
            <Droplets size={16} className="text-blue-500" />
            <div>
              <p className="text-xs text-gray-500">Avg Rainfall Required</p>
              <p className="text-sm font-medium">{averageRainfallRequired}</p>
            </div>
          </div>
        )}

        {/* Planting Time */}
        {recommendation.plantingTime && (
          <div className="flex items-center gap-2">
            <Calendar size={16} className="text-gray-500" />
            <div>
              <p className="text-xs text-gray-500">Planting Time</p>
              <p className="text-sm font-medium">{recommendation.plantingTime}</p>
            </div>
          </div>
        )}

        {/* Additional Inputs */}
        {additionalInputs.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-1">
              <Package size={14} />
              Additional Inputs Needed
            </h4>
            <div className="flex flex-wrap gap-2">
              {additionalInputs.map((input, index) => (
                <span 
                  key={index}
                  className="px-2 py-1 bg-orange-50 text-orange-700 text-xs rounded-md font-medium"
                >
                  {input}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Recommended Varieties */}
        {recommendation.varieties && recommendation.varieties.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-gray-700 mb-2">Recommended Varieties</h4>
            <div className="flex flex-wrap gap-2">
              {recommendation.varieties.slice(0, 3).map((variety, index) => (
                <span 
                  key={index}
                  className="px-2 py-1 bg-green-50 text-green-700 text-xs rounded-md font-medium"
                >
                  {variety}
                </span>
              ))}
              {recommendation.varieties.length > 3 && (
                <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-md">
                  +{recommendation.varieties.length - 3} more
                </span>
              )}
            </div>
          </div>
        )}

        {/* Key Benefits */}
        {recommendation.benefits && recommendation.benefits.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-gray-700 mb-2">Key Benefits</h4>
            <div className="space-y-1">
              {recommendation.benefits.slice(0, 2).map((benefit, index) => (
                <div key={index} className="flex items-center gap-2">
                  <TrendingUp size={12} className="text-green-500" />
                  <span className="text-xs text-gray-600">{benefit}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Click indicator */}
        {onClick && (
          <div className="flex items-center justify-end pt-2 border-t border-gray-100">
            <span className="text-xs text-gray-500 flex items-center gap-1">
              View details <ArrowRight size={12} />
            </span>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default EnhancedCropRecommendationCard;


