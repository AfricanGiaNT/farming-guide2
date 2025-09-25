import React, { useState } from 'react';
import CropRecommendationCard from '../components/crops/CropRecommendationCard';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { MapPin, Calendar, Droplets } from 'lucide-react';
import { mockCropRecommendations, malawianDistricts } from '../utils/mockData';
import { Season } from '../types';

const Crops: React.FC = () => {
  const [selectedDistrict, setSelectedDistrict] = useState<string>('Lilongwe');
  const [selectedSeason, setSelectedSeason] = useState<Season>('rainy');

  const seasons: { value: Season; label: string; description: string }[] = [
    { value: 'rainy', label: 'Rainy Season', description: 'November - April' },
    { value: 'dry', label: 'Dry Season', description: 'May - September' },
    { value: 'cold', label: 'Cold Season', description: 'June - August' }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Crop Recommendations</h1>
        <p className="text-gray-600">
          Get personalized crop recommendations based on your location and season
        </p>
      </div>

      {/* Location and Season Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MapPin size={20} className="text-green-600" />
            Location & Season
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select District
              </label>
              <select
                value={selectedDistrict}
                onChange={(e) => setSelectedDistrict(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              >
                {malawianDistricts.map((district) => (
                  <option key={district} value={district}>
                    {district}
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Farming Season
              </label>
              <div className="grid grid-cols-1 gap-2">
                {seasons.map((season) => (
                  <label key={season.value} className="flex items-center">
                    <input
                      type="radio"
                      name="season"
                      value={season.value}
                      checked={selectedSeason === season.value}
                      onChange={(e) => setSelectedSeason(e.target.value as Season)}
                      className="w-4 h-4 text-green-600 border-gray-300 focus:ring-green-500"
                    />
                    <div className="ml-3">
                      <span className="text-sm font-medium text-gray-900">{season.label}</span>
                      <span className="text-xs text-gray-500 ml-2">{season.description}</span>
                    </div>
                  </label>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Current Conditions */}
      <Card className="bg-blue-50 border-blue-200">
        <CardContent className="p-4">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <MapPin size={16} className="text-blue-600" />
              <span className="text-sm font-medium text-blue-800">{selectedDistrict} District</span>
            </div>
            <div className="flex items-center gap-2">
              <Calendar size={16} className="text-blue-600" />
              <span className="text-sm font-medium text-blue-800">{seasons.find(s => s.value === selectedSeason)?.label}</span>
            </div>
            <div className="flex items-center gap-2">
              <Droplets size={16} className="text-blue-600" />
              <span className="text-sm font-medium text-blue-800">Good soil moisture</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Recommendations */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Recommended Crops for {selectedDistrict}
        </h2>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {mockCropRecommendations.map((recommendation, index) => (
            <CropRecommendationCard
              key={index}
              recommendation={recommendation}
              onClick={() => {
                // Could navigate to detailed view
                console.log('Selected crop:', recommendation.crop);
              }}
            />
          ))}
        </div>
      </div>

      {/* Additional Information */}
      <div className="grid md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-green-700">Planting Calendar</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div>
                <h4 className="font-medium text-gray-900">Current Month (January)</h4>
                <p className="text-sm text-gray-600">Peak planting time for maize and groundnuts</p>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">Next Month (February)</h4>
                <p className="text-sm text-gray-600">Last chance for short-season varieties</p>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">March-April</h4>
                <p className="text-sm text-gray-600">Focus on crop management and weeding</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-blue-700">Market Insights</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div>
                <h4 className="font-medium text-gray-900">High Demand Crops</h4>
                <p className="text-sm text-gray-600">Soybeans, groundnuts showing strong prices</p>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">Export Opportunities</h4>
                <p className="text-sm text-gray-600">Soybean processing plants seeking suppliers</p>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">Local Markets</h4>
                <p className="text-sm text-gray-600">Good demand for traditional varieties</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Crops;