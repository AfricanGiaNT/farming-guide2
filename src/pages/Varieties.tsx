import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Search, Filter, Clock, Target, Shield, Sprout } from 'lucide-react';
import { mockCropVarieties } from '../utils/mockData';

const Varieties: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCrop, setSelectedCrop] = useState<string>('all');

  const crops = ['all', 'Maize', 'Groundnuts', 'Soybeans', 'Rice', 'Beans'];
  
  const filteredVarieties = mockCropVarieties.filter(variety => {
    const matchesSearch = variety.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         variety.crop.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCrop = selectedCrop === 'all' || variety.crop === selectedCrop;
    return matchesSearch && matchesCrop;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Crop Varieties</h1>
        <p className="text-gray-600">
          Search and compare different crop varieties to find the best fit for your farm
        </p>
      </div>

      {/* Search and Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="space-y-4">
            {/* Search Bar */}
            <div className="relative">
              <Search size={20} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search varieties by name or crop..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              />
            </div>

            {/* Crop Filter */}
            <div className="flex items-center gap-4 flex-wrap">
              <div className="flex items-center gap-2">
                <Filter size={16} className="text-gray-500" />
                <span className="text-sm font-medium text-gray-700">Filter by crop:</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {crops.map((crop) => (
                  <button
                    key={crop}
                    onClick={() => setSelectedCrop(crop)}
                    className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                      selectedCrop === crop
                        ? 'bg-green-100 text-green-700 border border-green-300'
                        : 'bg-gray-100 text-gray-700 border border-gray-300 hover:bg-gray-200'
                    }`}
                  >
                    {crop === 'all' ? 'All Crops' : crop}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Results Count */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-gray-600">
          {filteredVarieties.length} varieties found
        </p>
      </div>

      {/* Varieties Grid */}
      <div className="grid gap-6 md:grid-cols-2">
        {filteredVarieties.length > 0 ? (
          filteredVarieties.map((variety) => (
            <Card key={variety.id} className="hover:shadow-lg transition-all duration-200">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <Sprout size={20} className="text-green-600" />
                    {variety.name}
                  </CardTitle>
                  <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-md font-medium">
                    {variety.crop}
                  </span>
                </div>
              </CardHeader>
              
              <CardContent className="space-y-4">
                <p className="text-sm text-gray-600">{variety.description}</p>

                {/* Key Metrics */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="flex items-center gap-2">
                    <Clock size={16} className="text-gray-500" />
                    <div>
                      <p className="text-xs text-gray-500">Maturity</p>
                      <p className="text-sm font-medium">{variety.maturityDays} days</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Target size={16} className="text-gray-500" />
                    <div>
                      <p className="text-xs text-gray-500">Yield Potential</p>
                      <p className="text-sm font-medium">{variety.yieldPotential}</p>
                    </div>
                  </div>
                </div>

                {/* Disease Resistance */}
                {variety.diseaseResistance.length > 0 && (
                  <div>
                    <h4 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                      <Shield size={16} className="text-green-600" />
                      Disease Resistance
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {variety.diseaseResistance.map((disease, index) => (
                        <span
                          key={index}
                          className="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded-md"
                        >
                          {disease}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Characteristics */}
                <div>
                  <h4 className="text-sm font-semibold text-gray-700 mb-2">Key Characteristics</h4>
                  <div className="flex flex-wrap gap-2">
                    {variety.characteristics.map((char, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-green-50 text-green-700 text-xs rounded-md"
                      >
                        {char}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Recommendations */}
                {variety.recommendations.length > 0 && (
                  <div>
                    <h4 className="text-sm font-semibold text-gray-700 mb-2">Growing Tips</h4>
                    <ul className="text-xs text-gray-600 space-y-1">
                      {variety.recommendations.slice(0, 2).map((tip, index) => (
                        <li key={index} className="flex items-start gap-1">
                          <span className="text-green-600 mt-1">•</span>
                          <span>{tip}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </CardContent>
            </Card>
          ))
        ) : (
          <div className="col-span-full text-center py-12">
            <Search size={48} className="text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No varieties found</h3>
            <p className="text-gray-500">
              Try adjusting your search terms or selecting a different crop filter.
            </p>
          </div>
        )}
      </div>

      {/* Information Card */}
      <Card className="bg-yellow-50 border-yellow-200">
        <CardContent className="p-6">
          <h3 className="font-semibold text-yellow-800 mb-2">💡 Choosing the Right Variety</h3>
          <div className="grid md:grid-cols-3 gap-4 text-sm text-yellow-700">
            <div>
              <h4 className="font-medium mb-1">Consider Your Conditions</h4>
              <p>Match varieties to your soil type, rainfall, and climate conditions.</p>
            </div>
            <div>
              <h4 className="font-medium mb-1">Market Demand</h4>
              <p>Choose varieties with good market acceptance and pricing.</p>
            </div>
            <div>
              <h4 className="font-medium mb-1">Risk Management</h4>
              <p>Select disease-resistant varieties to reduce crop losses.</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Varieties;