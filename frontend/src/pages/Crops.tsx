import React, { useState, useEffect } from 'react';
import CropRecommendationCard from '../components/crops/CropRecommendationCard';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { MapPin, Calendar, Droplets, Search, Loader2, ArrowLeft, Cloud } from 'lucide-react';
import { mockCropRecommendations, malawianDistricts } from '../utils/mockData';
import { Season } from '../types';
import { apiService } from '../services/api';
import { useLocation, useNavigate } from 'react-router-dom';

const Crops: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [selectedDistrict, setSelectedDistrict] = useState<string>('Lilongwe');
  const [selectedSeason, setSelectedSeason] = useState<Season>('rainy');
  
  // Form inputs
  const [locationInput, setLocationInput] = useState('');
  const [coordinates, setCoordinates] = useState({ lat: '', lon: '' });
  const [cropSearch, setCropSearch] = useState('');
  
  // API state
  const [cropData, setCropData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentLocation, setCurrentLocation] = useState<string>('');
  
  // Weather context from navigation
  const [weatherContext, setWeatherContext] = useState<any>(null);

  // Handle weather context from navigation
  useEffect(() => {
    if (location.state?.weatherContext) {
      const context = location.state.weatherContext;
      setWeatherContext(context);
      
      // Pre-populate location if available
      if (context.location) {
        setCurrentLocation(context.location);
        if (context.location.includes(',')) {
          // It's coordinates
          const [lat, lon] = context.location.split(',');
          setCoordinates({ lat: lat.trim(), lon: lon.trim() });
        } else {
          // It's a location name
          setLocationInput(context.location);
        }
      }
      
      // Pre-populate crop data if available
      if (context.cropRecommendations) {
        setCropData(context.cropRecommendations);
      }
    }
  }, [location.state]);

  const seasons: { value: Season; label: string; description: string }[] = [
    { value: 'rainy', label: 'Rainy Season', description: 'November - April' },
    { value: 'dry', label: 'Dry Season', description: 'May - September' },
    { value: 'cold', label: 'Cold Season', description: 'June - August' }
  ];

  // Parse coordinates from input
  const parseCoordinates = (input: string) => {
    const coordRegex = /(-?\d+\.?\d*),\s*(-?\d+\.?\d*)/;
    const match = input.match(coordRegex);
    if (match) {
      setCoordinates({ lat: match[1], lon: match[2] });
      setLocationInput('');
    }
  };

  // Get crop recommendations from API
  const handleGetRecommendations = async () => {
    if (!locationInput && (!coordinates.lat || !coordinates.lon)) {
      setError('Please enter either a location name or GPS coordinates');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      let searchLocation = locationInput;
      let searchCoords = null;
      
      // Priority: coordinates over district
      if (coordinates.lat && coordinates.lon) {
        searchLocation = `${coordinates.lat},${coordinates.lon}`;
        searchCoords = { lat: parseFloat(coordinates.lat), lon: parseFloat(coordinates.lon) };
      } else if (locationInput) {
        searchLocation = locationInput;
      }
      
      // Convert season to API format
      const seasonMap: { [key: string]: string } = {
        'rainy': 'rainy',
        'dry': 'dry', 
        'cold': 'current'
      };
      const apiSeason = seasonMap[selectedSeason] || 'current';
      
      // Call API
      const data = await apiService.getCrops(searchLocation, apiSeason as any);
      console.log('API Response:', data); // Debug log
      setCropData(data);
      setCurrentLocation(searchLocation);
      
      // Clear crop search to show all results
      setCropSearch('');
      
    } catch (err) {
      setError('Failed to fetch crop recommendations');
      console.error('Crop fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Transform API data to match CropRecommendationCard interface
  const transformApiData = (apiRecommendations: any[]) => {
    return apiRecommendations.map((item: any) => ({
      crop: item.crop_data?.name || item.crop_name || 'Unknown Crop',
      score: item.score || item.total_score || 0,
      varieties: item.crop_data?.varieties || ['Standard varieties'],
      plantingTime: item.crop_data?.planting_time || 'Seasonal planting',
      yieldPotential: item.crop_data?.yield_potential || 'Good potential',
      requirements: {
        rainfall: `${item.crop_data?.water_requirements?.minimum_rainfall || 500}-${item.crop_data?.water_requirements?.maximum_rainfall || 1200}mm`,
        soil: 'Well-drained soil',
        temperature: `${item.crop_data?.temperature_requirements?.minimum_temp || 15}-${item.crop_data?.temperature_requirements?.maximum_temp || 35}°C`
      },
      benefits: item.guide_recommendations?.slice(0, 3) || ['Suitable for local conditions']
    }));
  };

  // Filter recommendations based on crop search
  const apiRecommendations = cropData?.recommendations || [];
  const transformedRecommendations = transformApiData(apiRecommendations);
  
  const filteredRecommendations = cropSearch.trim() 
    ? transformedRecommendations.filter((crop: any) => 
        crop.crop?.toLowerCase().includes(cropSearch.toLowerCase())
      )
    : transformedRecommendations.length > 0 ? transformedRecommendations : mockCropRecommendations;

  // Note: Removed auto-refresh useEffect to prevent infinite loops
  // Users can manually refresh by clicking the search button

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Crop Recommendations</h1>
        <p className="text-gray-600">
          Get personalized crop recommendations based on your location and season
        </p>
      </div>

      {/* Weather Context Display */}
      {weatherContext && (
        <Card className="bg-gradient-to-r from-blue-50 to-green-50 border-blue-200">
          <CardHeader>
            <CardTitle className="text-blue-800 flex items-center gap-2">
              <Cloud size={20} />
              Weather-Based Analysis
              <button
                onClick={() => navigate('/weather')}
                className="ml-auto flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800"
              >
                <ArrowLeft size={14} />
                Back to Weather
              </button>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-3 gap-4">
              <div>
                <h4 className="font-semibold text-blue-800 mb-2">Location</h4>
                <p className="text-sm text-blue-700">{weatherContext.location}</p>
              </div>
              {weatherContext.weatherData && (
                <div>
                  <h4 className="font-semibold text-blue-800 mb-2">Current Weather</h4>
                  <div className="text-sm text-blue-700 space-y-1">
                    <p>Temperature: {weatherContext.weatherData.current.temperature}°C</p>
                    <p>Rainfall: {weatherContext.weatherData.current.rainfall}mm</p>
                    <p>Humidity: {weatherContext.weatherData.current.humidity}%</p>
                  </div>
                </div>
              )}
              {weatherContext.historicalData && (
                <div>
                  <h4 className="font-semibold text-blue-800 mb-2">Historical Data</h4>
                  <div className="text-sm text-blue-700 space-y-1">
                    <p>Annual Rainfall: {weatherContext.historicalData.climate_summary.total_annual_rainfall.toFixed(0)}mm</p>
                    <p>Wettest Month: {weatherContext.historicalData.climate_summary.wettest_month}</p>
                    <p>Drought Risk: {weatherContext.historicalData.climate_summary.drought_risk}</p>
                  </div>
                </div>
              )}
            </div>
            <div className="mt-4 p-3 bg-blue-100 rounded-lg">
              <p className="text-sm text-blue-800">
                <strong>Note:</strong> These recommendations are enhanced with weather analysis from the Weather page. 
                The data above was used to generate more accurate crop suggestions for your specific location and conditions.
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Search Form */}
      <Card className="bg-green-50 border-green-200">
        <CardHeader>
          <CardTitle className="text-green-800 flex items-center gap-2">
            <MapPin size={20} />
            Location & Crop Search Options
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid md:grid-cols-2 gap-4">
            {/* Location Input */}
            <div>
              <label className="block text-sm font-medium text-green-800 mb-2">
                Location (District/City Name)
              </label>
              <input
                type="text"
                value={locationInput}
                onChange={(e) => {
                  setLocationInput(e.target.value);
                  parseCoordinates(e.target.value);
                }}
                placeholder="e.g., Lilongwe, Blantyre, Mzuzu"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>

            {/* GPS Coordinates */}
            <div>
              <label className="block text-sm font-medium text-green-800 mb-2">
                GPS Coordinates (Latitude, Longitude)
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={coordinates.lat}
                  onChange={(e) => setCoordinates({...coordinates, lat: e.target.value})}
                  placeholder="Latitude"
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                />
                <input
                  type="text"
                  value={coordinates.lon}
                  onChange={(e) => setCoordinates({...coordinates, lon: e.target.value})}
                  placeholder="Longitude"
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            {/* Crop Search */}
            <div>
              <label className="block text-sm font-medium text-green-800 mb-2">
                Search Specific Crops
              </label>
              <input
                type="text"
                value={cropSearch}
                onChange={(e) => setCropSearch(e.target.value)}
                placeholder="e.g., maize, groundnut, beans"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>

            {/* Season Selection */}
            <div>
              <label className="block text-sm font-medium text-green-800 mb-2">
                Season
              </label>
              <div className="flex gap-2">
                <button 
                  onClick={() => setSelectedSeason('cold')}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    selectedSeason === 'cold'
                      ? 'bg-green-600 text-white'
                      : 'bg-white text-green-600 border border-green-600 hover:bg-green-50'
                  }`}
                >
                  Current
                </button>
                <button 
                  onClick={() => setSelectedSeason('rainy')}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    selectedSeason === 'rainy'
                      ? 'bg-green-600 text-white'
                      : 'bg-white text-green-600 border border-green-600 hover:bg-green-50'
                  }`}
                >
                  Rainy
                </button>
                <button 
                  onClick={() => setSelectedSeason('dry')}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    selectedSeason === 'dry'
                      ? 'bg-green-600 text-white'
                      : 'bg-white text-green-600 border border-green-600 hover:bg-green-50'
                  }`}
                >
                  Dry
                </button>
              </div>
            </div>
          </div>

          {/* Search Button */}
          <div className="flex justify-center">
            <button 
              onClick={handleGetRecommendations}
              disabled={loading}
              className="px-6 py-3 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 flex items-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 size={20} className="animate-spin" />
                  Getting Recommendations...
                </>
              ) : (
                <>
                  <MapPin size={20} />
                  Get Crop Recommendations
                </>
              )}
            </button>
          </div>

          {/* Error Display */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
              {error}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Search Results - Show immediately after search form */}
      {cropData && (
        <>
          {/* Environmental Summary */}
          {cropData?.environmental_summary && (
            <Card className="bg-blue-50 border-blue-200">
              <CardHeader>
                <CardTitle className="text-blue-800 flex items-center gap-2">
                  <Droplets size={20} />
                  Environmental Conditions
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-4 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-800">
                      {cropData.environmental_summary.total_7day_rainfall}mm
                    </div>
                    <div className="text-sm text-blue-600">7-Day Rainfall</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-800">
                      {cropData.environmental_summary.current_temperature}°C
                    </div>
                    <div className="text-sm text-blue-600">Temperature</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-800">
                      {cropData.environmental_summary.humidity}%
                    </div>
                    <div className="text-sm text-blue-600">Humidity</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-800 capitalize">
                      {cropData.environmental_summary.current_season}
                    </div>
                    <div className="text-sm text-blue-600">Season</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Recommendations */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Droplets size={20} />
                Recommended Crops for {currentLocation || selectedDistrict}
                {cropData?.mock_data && (
                  <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">
                    Demo Data
                  </span>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="flex justify-center items-center py-8">
                  <Loader2 size={32} className="animate-spin text-green-600" />
                  <span className="ml-2 text-gray-600">Loading recommendations...</span>
                </div>
              ) : (
                <>
                  <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {filteredRecommendations.map((recommendation: any, index: number) => {
                      console.log('Rendering recommendation:', recommendation); // Debug log
                      return (
                        <CropRecommendationCard
                          key={index}
                          recommendation={recommendation}
                          onClick={() => {
                            // Could navigate to detailed view
                            console.log('Selected crop:', recommendation.crop);
                          }}
                        />
                      );
                    })}
                  </div>
                  
                  {cropSearch && filteredRecommendations.length === 0 && (
                    <div className="text-center py-8 text-gray-500">
                      No crops found matching "{cropSearch}"
                    </div>
                  )}
                </>
              )}
            </CardContent>
          </Card>

          {/* Planting Advice */}
          {cropData?.planting_advice && (
            <Card className="bg-green-50 border-green-200">
              <CardHeader>
                <CardTitle className="text-green-800 flex items-center gap-2">
                  <Calendar size={20} />
                  Planting Advice
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div>
                    <span className="font-semibold text-green-800">Optimal Planting Window:</span>
                    <span className="ml-2 text-green-700">
                      {cropData.planting_advice.optimal_planting_window || 'Information not available'}
                    </span>
                  </div>
                  <div>
                    <span className="font-semibold text-green-800">Soil Preparation:</span>
                    <span className="ml-2 text-green-700">
                      {cropData.planting_advice.soil_preparation || 'Standard soil preparation recommended'}
                    </span>
                  </div>
                  <div>
                    <span className="font-semibold text-green-800">Seed Requirements:</span>
                    <span className="ml-2 text-green-700">
                      {cropData.planting_advice.seed_requirements || 'Use certified seeds for best results'}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Risk Assessment */}
          {cropData?.risk_assessment && (
            <Card className="bg-yellow-50 border-yellow-200">
              <CardHeader>
                <CardTitle className="text-yellow-800 flex items-center gap-2">
                  <Search size={20} />
                  Risk Assessment
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div>
                    <span className="font-semibold text-yellow-800">Overall Risk Level:</span>
                    <span className={`ml-2 px-2 py-1 rounded text-sm font-medium ${
                      cropData.risk_assessment.overall_risk_level === 'low' ? 'bg-green-100 text-green-800' :
                      cropData.risk_assessment.overall_risk_level === 'moderate' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {cropData.risk_assessment.overall_risk_level}
                    </span>
                  </div>
                  {cropData.risk_assessment.weather_risks && (
                    <div className="mt-3">
                      <span className="font-semibold text-yellow-800 block mb-2">Weather Risks:</span>
                      <div className="bg-yellow-100 rounded-lg p-3">
                        {cropData.risk_assessment.weather_risks.slice(0, 3).map((risk: string, index: number) => (
                          <div key={index} className="mb-2 last:mb-0">
                            <div className="text-sm text-yellow-800 leading-relaxed">
                              • {risk.length > 150 ? `${risk.substring(0, 150)}...` : risk}
                            </div>
                          </div>
                        ))}
                        {cropData.risk_assessment.weather_risks.length > 3 && (
                          <div className="text-xs text-yellow-600 mt-2 italic">
                            And {cropData.risk_assessment.weather_risks.length - 3} more weather risks...
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                  {cropData.risk_assessment.pest_risks && (
                    <div className="mt-3">
                      <span className="font-semibold text-yellow-800 block mb-2">Pest Risks:</span>
                      <div className="bg-yellow-100 rounded-lg p-3">
                        {cropData.risk_assessment.pest_risks.slice(0, 3).map((risk: string, index: number) => (
                          <div key={index} className="mb-2 last:mb-0">
                            <div className="text-sm text-yellow-800 leading-relaxed">
                              • {risk.length > 150 ? `${risk.substring(0, 150)}...` : risk}
                            </div>
                          </div>
                        ))}
                        {cropData.risk_assessment.pest_risks.length > 3 && (
                          <div className="text-xs text-yellow-600 mt-2 italic">
                            And {cropData.risk_assessment.pest_risks.length - 3} more pest risks...
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Management Tips */}
          {cropData?.management_tips && cropData.management_tips.length > 0 && (
            <Card className="bg-purple-50 border-purple-200">
              <CardHeader>
                <CardTitle className="text-purple-800 flex items-center gap-2">
                  <Droplets size={20} />
                  Agricultural Guidelines
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  {cropData.management_tips.slice(0, 5).map((tip: string, index: number) => (
                    <li key={index} className="flex items-start">
                      <span className="text-purple-600 mr-2 mt-1">•</span>
                      <div className="text-purple-700">
                        {tip.length > 300 ? (
                          <details className="cursor-pointer">
                            <summary className="text-sm leading-relaxed font-medium hover:text-purple-800">
                              {tip.substring(0, 150)}... <span className="text-purple-500">(click to read more)</span>
                            </summary>
                            <p className="text-sm mt-2 leading-relaxed">{tip}</p>
                          </details>
                        ) : (
                          <span className="text-sm leading-relaxed">{tip}</span>
                        )}
                      </div>
                    </li>
                  ))}
                </ul>
                {cropData.management_tips.length > 5 && (
                  <div className="mt-4 p-3 bg-purple-100 rounded-lg">
                    <p className="text-sm text-purple-700">
                      <strong>Note:</strong> Showing top 5 guidelines. {cropData.management_tips.length - 5} more available.
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </>
      )}

      {/* Current Selection Display */}
      <Card className="bg-blue-50 border-blue-200">
        <CardHeader>
          <CardTitle className="text-blue-800 flex items-center gap-2">
            <Calendar size={20} />
            Current Selection
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-blue-800 mb-2">
                Selected District
              </label>
              <select
                value={selectedDistrict}
                onChange={(e) => setSelectedDistrict(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {malawianDistricts.map((district) => (
                  <option key={district} value={district}>
                    {district}
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-blue-800 mb-2">
                Selected Season
              </label>
              <div className="flex gap-2 flex-wrap">
                {seasons.map((season) => (
                  <button
                    key={season.value}
                    onClick={() => setSelectedSeason(season.value)}
                    className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      selectedSeason === season.value
                        ? 'bg-blue-600 text-white'
                        : 'bg-white text-blue-600 border border-blue-600 hover:bg-blue-50'
                    }`}
                  >
                    {season.label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Current Conditions */}
      <Card className="bg-gray-50 border-gray-200">
        <CardContent className="p-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center gap-2">
              <MapPin size={16} className="text-gray-600" />
              <span className="text-sm font-medium text-gray-800">
                {currentLocation || selectedDistrict} District
              </span>
            </div>
            <div className="flex items-center gap-2">
              <Calendar size={16} className="text-gray-600" />
              <span className="text-sm font-medium text-gray-800">{seasons.find(s => s.value === selectedSeason)?.label}</span>
            </div>
            <div className="flex items-center gap-2">
              <Droplets size={16} className="text-gray-600" />
              <span className="text-sm font-medium text-gray-800">
                {cropData?.environmental_summary ? 
                  `${cropData.environmental_summary.total_7day_rainfall}mm rainfall` : 
                  'Good soil moisture'
                }
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Recommendations */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Droplets size={20} />
            Recommended Crops for {currentLocation || selectedDistrict}
            {cropData?.mock_data && (
              <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">
                Demo Data
              </span>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex justify-center items-center py-8">
              <Loader2 size={32} className="animate-spin text-green-600" />
              <span className="ml-2 text-gray-600">Loading recommendations...</span>
            </div>
          ) : (
            <>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {filteredRecommendations.map((recommendation: any, index: number) => (
                  <CropRecommendationCard
                    key={index}
                    recommendation={recommendation}
                    onClick={() => {
                      // Could navigate to detailed view
                      console.log('Selected crop:', recommendation.crop_name || recommendation.crop);
                    }}
                  />
                ))}
              </div>
              
              {cropSearch && filteredRecommendations.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  No crops found matching "{cropSearch}"
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>

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