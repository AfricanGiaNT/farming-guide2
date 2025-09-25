import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card';
import { Sprout, TrendingUp, Calendar, Target } from 'lucide-react';
import { CropRecommendation } from '../../types';

interface CropRecommendationCardProps {
  recommendation: CropRecommendation;
  onClick?: () => void;
}

const CropRecommendationCard: React.FC<CropRecommendationCardProps> = ({ 
  recommendation, 
  onClick 
}) => {
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-100';
    if (score >= 60) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  return (
    <Card onClick={onClick} className="hover:shadow-lg transition-all duration-200">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Sprout size={20} className="text-green-600" />
            {recommendation.crop}
          </CardTitle>
          <div className={`px-2 py-1 rounded-full text-xs font-bold ${getScoreColor(recommendation.score)}`}>
            {recommendation.score}%
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="flex items-center gap-2">
            <Calendar size={16} className="text-gray-500" />
            <div>
              <p className="text-xs text-gray-500">Planting Time</p>
              <p className="text-sm font-medium">{recommendation.plantingTime}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Target size={16} className="text-gray-500" />
            <div>
              <p className="text-xs text-gray-500">Yield Potential</p>
              <p className="text-sm font-medium">{recommendation.yieldPotential}</p>
            </div>
          </div>
        </div>

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
      </CardContent>
    </Card>
  );
};

export default CropRecommendationCard;