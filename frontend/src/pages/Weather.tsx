import React, { useState, useEffect } from 'react';
import WeatherWidget from '../components/weather/WeatherWidget';
import ForecastChart from '../components/weather/ForecastChart';
import EnhancedCropRecommendationCard from '../components/crops/EnhancedCropRecommendationCard';
import YearCard from '../components/weather/YearCard';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Cloud, Sun, CloudRain, MapPin, Calendar, Loader2, Search, TrendingUp, Sprout, ArrowRight } from 'lucide-react';
import { apiService, WeatherData, CropResponse, HistoricalWeatherData, GoogleMapsExtractionResponse } from '../services/api';
import { getSortedMonths, getSeasonColor } from '../utils/monthOrder';
import { useNavigate } from 'react-router-dom';

const Weather: React.FC = () => {
  const navigate = useNavigate();
  const [chartType, setChartType] = useState<'temperature' | 'rainfall'>('temperature');
  const [weatherData, setWeatherData] = useState<WeatherData | null>(null);
  const [historicalData, setHistoricalData] = useState<HistoricalWeatherData | null>(null);
  const [cropRecommendations, setCropRecommendations] = useState<CropResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingCrops, setLoadingCrops] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Form inputs
  const [locationInput, setLocationInput] = useState('');
  const [coordinates, setCoordinates] = useState({ lat: '', lon: '' });
  const [googleMapsUrl, setGoogleMapsUrl] = useState('');
  const [historicalYears, setHistoricalYears] = useState(1);
  const [dataType, setDataType] = useState<'current' | 'historical'>('current');
  const [inputType, setInputType] = useState<'location' | 'coordinates' | 'google_maps'>('location');
  
  // Current location for display
  const [currentLocation, setCurrentLocation] = useState<string>('');
  
  // Google Maps extraction state
  const [extractingCoordinates, setExtractingCoordinates] = useState(false);
  const [extractionResult, setExtractionResult] = useState<GoogleMapsExtractionResponse | null>(null);

  // Navigate to crops page with weather context
  const handleViewMoreCrops = () => {
    // Create weather context object
    const weatherContext = {
      location: currentLocation,
      weatherData: weatherData,
      historicalData: historicalData,
      cropRecommendations: cropRecommendations,
      timestamp: new Date().toISOString()
    };
    
    // Navigate to crops page with context
    navigate('/crops', { 
      state: { weatherContext },
      replace: false 
    });
  };

  // Search for weather data
  const handleWeatherSearch = async () => {
    // Validate input based on selected input type
    if (inputType === 'location' && !locationInput.trim()) {
      setError('Please enter a location name');
      return;
    }
    if (inputType === 'coordinates' && (!coordinates.lat || !coordinates.lon)) {
      setError('Please enter both latitude and longitude');
      return;
    }
    if (inputType === 'google_maps' && (!extractionResult || !coordinates.lat || !coordinates.lon)) {
      setError('Please extract coordinates from a Google Maps URL first');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      let searchLocation = locationInput;
      if (inputType === 'coordinates' || inputType === 'google_maps') {
        searchLocation = `${coordinates.lat},${coordinates.lon}`;
      }
      
      if (dataType === 'current') {
        const data = await apiService.getWeather(searchLocation);
        setWeatherData(data);
        setHistoricalData(null);
      } else {
        const data = await apiService.getEnhancedHistoricalWeather(searchLocation, historicalYears);
        setHistoricalData(data);
        setWeatherData(null);
      }
      
      setCurrentLocation(searchLocation);
      
      // Auto-fetch crop recommendations
      await handleCropSearch(searchLocation);
      
    } catch (err) {
      setError('Failed to fetch weather data');
      console.error('Weather fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Search for crop recommendations based on weather using enhanced smart crops
  const handleCropSearch = async (location?: string) => {
    const searchLocation = location || currentLocation;
    if (!searchLocation) return;

    try {
      setLoadingCrops(true);
      // Use enhanced smart crops API for better recommendations
      const smartCropData = await apiService.getSmartCrops(
        searchLocation, 
        'rain', // Default to rainy season for weather page
        'balanced', // Default risk tolerance
        'medium', // Default budget
        6 // Max crops to show
      );
      
      // Transform smart crop data to match expected format
      if (smartCropData.status === 'success' && smartCropData.data) {
        const enhancedData = smartCropData.data;
        const transformedRecommendations = enhancedData.recommendations?.map((rec: any, index: number) => ({
          crop_data: {
            name: rec.crop?.name || 'Unknown Crop',
            category: rec.crop?.category || 'Cereals',
            description: rec.recommendation_reason || `${rec.crop?.name} recommendations from enhanced agricultural analysis`,
            temperature_requirements: {
              minimum_temp: 15,
              maximum_temp: 35,
              optimal_temp: 25
            },
            water_requirements: {
              minimum_rainfall: 400,
              maximum_rainfall: 1200,
              optimal_rainfall: 800
            }
          },
          score: rec.composite_score || 0,
          total_score: 100,
          suitability_level: rec.confidence_level || 'good',
          suitability_score: rec.composite_score || 0,
          sources: ['Enhanced Recommendation Engine'],
          guide_recommendations: rec.key_insights || [],
          reasons: [rec.recommendation_reason || 'Intelligent recommendation based on comprehensive analysis'],
          score_components: {
            content_quality: rec.score_breakdown?.profitability || 0,
            guide_relevance: rec.score_breakdown?.ease_of_farming || 0,
            seasonal_match: rec.score_breakdown?.regional_suitability || 0
          },
          source: 'enhanced_engine',
          // Enhanced features
          composite_score: rec.composite_score,
          confidence_score: rec.confidence_score,
          risk_assessment: rec.risk_assessment,
          profit_analysis: rec.profit_analysis,
          implementation_plan: rec.implementation_plan,
          ml_predictions: rec.ml_predictions
        })) || [];

        setCropRecommendations({
          location: searchLocation,
          season: 'rain',
          recommendations: transformedRecommendations,
          enhanced_features: smartCropData.enhanced_features,
          summary: enhancedData.summary,
          farmer_guidance: enhancedData.farmer_guidance
        });
      } else {
        // Fallback to regular crops API
        const cropData = await apiService.getCrops(searchLocation, 'current');
        setCropRecommendations(cropData);
      }
    } catch (err) {
      console.error('Crop fetch error:', err);
      // Fallback to regular crops API on error
      try {
        const cropData = await apiService.getCrops(searchLocation, 'current');
        setCropRecommendations(cropData);
      } catch (fallbackErr) {
        console.error('Fallback crop fetch error:', fallbackErr);
      }
    } finally {
      setLoadingCrops(false);
    }
  };

  // Parse coordinates from input
  const parseCoordinates = (input: string) => {
    const coordRegex = /(-?\d+\.?\d*),\s*(-?\d+\.?\d*)/;
    const match = input.match(coordRegex);
    if (match) {
      setCoordinates({ lat: match[1], lon: match[2] });
      setLocationInput('');
    }
  };

  // Extract coordinates from Google Maps URL
  const handleGoogleMapsExtraction = async () => {
    if (!googleMapsUrl.trim()) {
      setError('Please enter a Google Maps URL');
      return;
    }

    try {
      setExtractingCoordinates(true);
      setError(null);
      
      const result = await apiService.extractCoordinatesFromGoogleMaps(googleMapsUrl.trim());
      
      if (result.success) {
        setExtractionResult(result);
        setCoordinates({
          lat: result.coordinates.latitude.toString(),
          lon: result.coordinates.longitude.toString()
        });
        setLocationInput('');
        setError(null);
      } else {
        setError('Failed to extract coordinates from Google Maps URL');
      }
    } catch (err) {
      setError('Failed to extract coordinates from Google Maps URL');
      console.error('Google Maps extraction error:', err);
    } finally {
      setExtractingCoordinates(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Weather & Crop Analysis</h1>
        <p className="text-gray-600">Get weather data and crop recommendations for any location in Malawi</p>
      </div>

      {/* Search Form */}
      <Card className="bg-blue-50 border-blue-200">
        <CardHeader>
          <CardTitle className="text-blue-800 flex items-center gap-2">
            <Search size={20} />
            Location & Data Options
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Input Type Selection */}
          <div>
            <label className="block text-sm font-medium text-blue-800 mb-2">
              Location Input Method
            </label>
            <div className="flex gap-2 flex-wrap">
              <button
                onClick={() => setInputType('location')}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  inputType === 'location'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-blue-600 border border-blue-600 hover:bg-blue-50'
                }`}
              >
                📍 Location Name
              </button>
              <button
                onClick={() => setInputType('coordinates')}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  inputType === 'coordinates'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-blue-600 border border-blue-600 hover:bg-blue-50'
                }`}
              >
                🗺️ GPS Coordinates
              </button>
              <button
                onClick={() => setInputType('google_maps')}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  inputType === 'google_maps'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-blue-600 border border-blue-600 hover:bg-blue-50'
                }`}
              >
                🔗 Google Maps Link
              </button>
            </div>
          </div>

          {/* Location Input */}
          {inputType === 'location' && (
            <div>
              <label className="block text-sm font-medium text-blue-800 mb-2">
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
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          )}

          {/* GPS Coordinates */}
          {inputType === 'coordinates' && (
            <div>
              <label className="block text-sm font-medium text-blue-800 mb-2">
                GPS Coordinates (Latitude, Longitude)
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={coordinates.lat}
                  onChange={(e) => setCoordinates({...coordinates, lat: e.target.value})}
                  placeholder="Latitude"
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <input
                  type="text"
                  value={coordinates.lon}
                  onChange={(e) => setCoordinates({...coordinates, lon: e.target.value})}
                  placeholder="Longitude"
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          )}

          {/* Google Maps URL */}
          {inputType === 'google_maps' && (
            <div>
              <label className="block text-sm font-medium text-blue-800 mb-2">
                Google Maps URL
              </label>
              <div className="space-y-2">
                <input
                  type="url"
                  value={googleMapsUrl}
                  onChange={(e) => setGoogleMapsUrl(e.target.value)}
                  placeholder="Paste your Google Maps sharing link here..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                  onClick={handleGoogleMapsExtraction}
                  disabled={extractingCoordinates || !googleMapsUrl.trim()}
                  className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  {extractingCoordinates ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Extracting...
                    </>
                  ) : (
                    <>
                      🔍 Extract Coordinates
                    </>
                  )}
                </button>
                
                {/* Show extraction result */}
                {extractionResult && (
                  <div className="p-3 bg-green-50 border border-green-200 rounded-md">
                    <p className="text-sm text-green-800">
                      ✅ Coordinates extracted: {extractionResult.coordinates.latitude}, {extractionResult.coordinates.longitude}
                    </p>
                    <p className="text-xs text-green-600 mt-1">
                      Format: {extractionResult.metadata.format_detected} | 
                      Confidence: {Math.round(extractionResult.metadata.confidence * 100)}%
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          <div className="grid md:grid-cols-2 gap-4">
            {/* Data Type Selection */}
            <div>
              <label className="block text-sm font-medium text-blue-800 mb-2">
                Data Type
              </label>
              <div className="flex gap-2">
                <button
                  onClick={() => setDataType('current')}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    dataType === 'current'
                      ? 'bg-blue-600 text-white'
                      : 'bg-white text-blue-600 border border-blue-600 hover:bg-blue-50'
                  }`}
                >
                  7-Day Forecast
                </button>
                <button
                  onClick={() => setDataType('historical')}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    dataType === 'historical'
                      ? 'bg-blue-600 text-white'
                      : 'bg-white text-blue-600 border border-blue-600 hover:bg-blue-50'
                  }`}
                >
                  Historical Data
                </button>
              </div>
            </div>

            {/* Historical Years Selection */}
            {dataType === 'historical' && (
              <div>
                <label className="block text-sm font-medium text-blue-800 mb-2">
                  Historical Years (1-10)
                </label>
                <select
                  value={historicalYears}
                  onChange={(e) => setHistoricalYears(Number(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(year => (
                    <option key={year} value={year}>{year} Year{year > 1 ? 's' : ''}</option>
                  ))}
                </select>
              </div>
            )}
          </div>

          {/* Search Button */}
          <div className="flex justify-center">
            <button
              onClick={handleWeatherSearch}
              disabled={loading}
              className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 size={20} className="animate-spin" />
                  Searching...
                </>
              ) : (
                <>
                  <Search size={20} />
                  Get Weather & Crop Data
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

      {/* Weather Data Results */}
      {weatherData && (
        <>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp size={20} />
                Weather Data for {currentLocation}
                {weatherData.mock_data && (
                  <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">
                    Demo Data
                  </span>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <WeatherWidget weather={weatherData} />
            </CardContent>
          </Card>

          {/* 7-Day Rainfall Analysis */}
          <Card className="bg-green-50 border-green-200">
            <CardHeader>
              <CardTitle className="text-green-800 flex items-center gap-2">
                <CloudRain size={20} />
                7-Day Rainfall Analysis
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-3 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-800">
                    {weatherData.forecast.reduce((total, day) => total + (day.rain_chance * 0.1), 0).toFixed(1)}mm
                  </div>
                  <div className="text-sm text-green-600">Expected Rainfall</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-800">
                    {weatherData.forecast.filter(day => day.rain_chance > 50).length}
                  </div>
                  <div className="text-sm text-green-600">Rainy Days</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-800">
                    {weatherData.forecast.reduce((max, day) => Math.max(max, day.rain_chance), 0)}%
                  </div>
                  <div className="text-sm text-green-600">Max Rain Chance</div>
                </div>
              </div>
              
              <div className="mt-4 p-3 bg-green-100 rounded-lg">
                <h4 className="font-semibold text-green-800 mb-2">Agricultural Impact</h4>
                <div className="text-sm text-green-700 space-y-1">
                  {weatherData.forecast.reduce((total, day) => total + (day.rain_chance * 0.1), 0) > 50 ? (
                    <>
                      <p>• Excellent rainfall expected - perfect for planting</p>
                      <p>• Consider planting rain-fed crops</p>
                    </>
                  ) : weatherData.forecast.reduce((total, day) => total + (day.rain_chance * 0.1), 0) > 20 ? (
                    <>
                      <p>• Good rainfall expected - suitable for most crops</p>
                      <p>• Monitor soil moisture levels</p>
                    </>
                  ) : (
                    <>
                      <p>• Light rainfall expected - irrigation recommended</p>
                      <p>• Choose drought-resistant varieties</p>
                    </>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Forecast Chart */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>7-Day Forecast Chart</CardTitle>
                <div className="flex gap-2">
                  <button
                    onClick={() => setChartType('temperature')}
                    className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                      chartType === 'temperature'
                        ? 'bg-blue-100 text-blue-700'
                        : 'text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    Temperature
                  </button>
                  <button
                    onClick={() => setChartType('rainfall')}
                    className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                      chartType === 'rainfall'
                        ? 'bg-blue-100 text-blue-700'
                        : 'text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    Rainfall
                  </button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <ForecastChart forecast={weatherData.forecast} type={chartType} />
            </CardContent>
          </Card>
        </>
      )}

      {/* Historical Weather Data Results */}
      {historicalData && (
        <>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 flex-wrap">
                <TrendingUp size={20} />
                <span>Historical Weather Data for {currentLocation}</span>
                <span className="text-sm font-normal text-gray-600">
                  ({historicalData.years_analyzed} year{historicalData.years_analyzed > 1 ? 's' : ''})
                </span>
                {historicalData.mock_data && (
                  <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">
                    Demo Data
                  </span>
                )}
                {/* Data Source Indicator */}
                {(historicalData as any).data_source && (
                  <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded flex items-center gap-1">
                    📡 {(historicalData as any).data_source}
                  </span>
                )}
              </CardTitle>
              {(historicalData as any).period_start && (historicalData as any).period_end && (
                <div className="space-y-1 mt-1">
                  <p className="text-sm text-gray-600">
                    Analysis Period: {new Date((historicalData as any).period_start).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })} to {new Date((historicalData as any).period_end).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}
                  </p>
                  {/* Data Quality Note */}
                  {(historicalData as any).climate_summary?.data_note && (
                    <p className="text-xs text-gray-500">
                      ℹ️ {(historicalData as any).climate_summary.data_note}
                    </p>
                  )}
                </div>
              )}
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-4 gap-4 mb-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-800">
                    {(historicalData as any).annual_rainfall || historicalData.climate_summary.total_annual_rainfall.toFixed(0)}mm
                  </div>
                  <div className="text-sm text-blue-600">Annual Rainfall</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-800">
                    {(historicalData as any).wettest_month || historicalData.climate_summary.wettest_month}
                  </div>
                  <div className="text-sm text-green-600">Wettest Month</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-red-800">
                    {(historicalData as any).driest_month || historicalData.climate_summary.driest_month}
                  </div>
                  <div className="text-sm text-red-600">Driest Month</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-800 capitalize">
                    {historicalData.climate_summary.drought_risk}
                  </div>
                  <div className="text-sm text-purple-600">Drought Risk</div>
                </div>
              </div>

              {/* Data Quality & Source Information */}
              {(historicalData as any).data_source && (
                <div className="bg-green-50 border border-green-200 p-4 rounded-lg mb-4">
                  <h4 className="font-semibold text-green-800 mb-2 flex items-center gap-2">
                    ✓ Data Quality & Reliability
                  </h4>
                  <div className="grid md:grid-cols-2 gap-4 text-sm text-green-700">
                    <div>
                      <p className="font-medium mb-1">Data Source:</p>
                      <p>{(historicalData as any).data_source}</p>
                      {(historicalData as any).climate_summary?.data_note && (
                        <p className="text-xs mt-1 text-green-600">
                          {(historicalData as any).climate_summary.data_note}
                        </p>
                      )}
                    </div>
                    <div>
                      <p className="font-medium mb-1">Data Confidence:</p>
                      <div className="flex items-center gap-2">
                        <div className="flex-1 bg-green-200 h-2 rounded-full overflow-hidden">
                          <div 
                            className="bg-green-600 h-full"
                            style={{ width: historicalData.mock_data ? '50%' : '95%' }}
                          ></div>
                        </div>
                        <span className="font-medium">
                          {historicalData.mock_data ? 'Medium' : 'High'}
                        </span>
                      </div>
                      <p className="text-xs mt-1 text-green-600">
                        {historicalData.mock_data 
                          ? 'Scientifically modeled data'
                          : 'Real historical measurements'
                        }
                      </p>
                    </div>
                  </div>
                </div>
              )}

              <div className="bg-blue-50 p-4 rounded-lg mb-4">
                <h4 className="font-semibold text-blue-800 mb-2">Agricultural Implications</h4>
                <div className="grid md:grid-cols-2 gap-4 text-sm text-blue-700">
                  <div>
                    <p><strong>Wet Season:</strong> {historicalData.agricultural_implications.wet_season}</p>
                    <p><strong>Dry Season:</strong> {historicalData.agricultural_implications.dry_season}</p>
                  </div>
                  <div>
                    <p><strong>Planting Window:</strong> {historicalData.agricultural_implications.planting_window}</p>
                    <p><strong>Harvest Period:</strong> {historicalData.agricultural_implications.harvest_period}</p>
                  </div>
                </div>
              </div>

              {/* Monthly Breakdown - Simplified for Multi-Year Data */}
              <div>
                <h4 className="font-semibold text-gray-800 mb-3">
                  {historicalData.years_analyzed > 1 ? 'Key Monthly Averages' : 'Monthly Historical Averages'}
                </h4>
                
                {(() => {
                  // Get monthly data and sort by chronological order
                  const monthlyData = historicalData.key_monthly_averages || historicalData.monthly_averages;
                  const sortedMonths = getSortedMonths(monthlyData);
                  
                  return historicalData.years_analyzed > 1 ? (
                    // Simplified view for multi-year data
                    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
                      {sortedMonths.map((month) => {
                        const data = monthlyData[month];
                        const seasonColor = getSeasonColor(month);
                        return (
                          <div key={month} className={`${seasonColor} p-3 rounded-lg border`}>
                            <div className="font-semibold text-sm mb-1">{month}</div>
                            <div className="text-xs space-y-1">
                              <div>Rainfall: {(data as any).total_rainfall || data.average_rainfall}mm</div>
                              <div>Temp: {data.average_temperature}°C</div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  ) : (
                    // Full view for single year data
                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                      {sortedMonths.map((month) => {
                        const data = monthlyData[month];
                        const seasonColor = getSeasonColor(month);
                        return (
                          <div key={month} className={`${seasonColor} p-3 rounded-lg border`}>
                            <div className="font-semibold text-sm mb-1">{month}</div>
                            <div className="text-xs space-y-1">
                              <div>Rainfall: {(data as any).total_rainfall || data.average_rainfall}mm</div>
                              <div>Temp: {data.average_temperature}°C</div>
                              <div className="text-xs opacity-75">
                                Range: {data.min_rainfall}-{data.max_rainfall}mm
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  );
                })()}
              </div>
              
              {/* Yearly Breakdown for Multi-Year Data */}
              {historicalData.years_analyzed > 1 && historicalData.yearly_breakdown && (
                <div className="mt-6">
                  <h4 className="font-semibold text-gray-800 mb-3">Year-by-Year Breakdown</h4>
                  <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {historicalData.yearly_breakdown
                      ?.sort((a, b) => b.year - a.year) // Sort by most recent first
                      ?.map((yearData, index) => (
                        <YearCard
                          key={index}
                          year={yearData.year}
                          annualRainfall={yearData.annual_rainfall}
                          avgTemperature={yearData.avg_temperature}
                          wettestMonth={yearData.wettest_month}
                          driestMonth={yearData.driest_month}
                          monthlySummary={yearData.monthly_summary}
                          monthlyData={historicalData.monthly_averages}
                        />
                      ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </>
      )}

      {/* Enhanced Crop Recommendations */}
      {cropRecommendations && (
        <Card className="bg-gradient-to-r from-green-50 to-yellow-50 border-green-200">
          <CardHeader>
            <CardTitle className="text-green-800 flex items-center gap-2">
              <Sprout size={20} />
              Crop Recommendations Based on Weather Data
              {loadingCrops && <Loader2 size={16} className="animate-spin" />}
              {cropRecommendations.mock_data && (
                <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">
                  Demo Data
                </span>
              )}
              {cropRecommendations.enhanced_features && (
                <span className="text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded">
                  ✨ Enhanced AI
                </span>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-green-700 mb-6">
              Based on weather conditions for <strong>{cropRecommendations.location}</strong>, here are the top recommended crops:
            </p>
            
            {/* Top 3 Crop Recommendations in Card Format */}
            <div className="grid md:grid-cols-3 gap-4 mb-6">
              {cropRecommendations.recommendations.slice(0, 3).map((crop, index) => (
                <EnhancedCropRecommendationCard
                  key={index}
                  recommendation={crop}
                  weatherData={weatherData ? {
                    temperature: weatherData.current.temperature,
                    rainfall: weatherData.current.rainfall,
                    humidity: weatherData.current.humidity
                  } : undefined}
                  historicalData={historicalData ? {
                    average_rainfall: historicalData.climate_summary.total_annual_rainfall,
                    wettest_month: historicalData.climate_summary.wettest_month,
                    driest_month: historicalData.climate_summary.driest_month
                  } : undefined}
                  onClick={() => handleViewMoreCrops()}
                />
              ))}
            </div>

            {/* See More Button */}
            {cropRecommendations.recommendations.length > 3 && (
              <div className="text-center">
                <button
                  onClick={handleViewMoreCrops}
                  className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors duration-200 flex items-center gap-2 mx-auto"
                >
                  <span>See More Recommendations</span>
                  <ArrowRight size={16} />
                </button>
                <p className="text-xs text-gray-600 mt-2">
                  View all {cropRecommendations.recommendations.length} recommendations with detailed analysis
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Getting Started Guide */}
      {!weatherData && !historicalData && !loading && (
        <Card className="bg-gray-50 border-gray-200">
          <CardHeader>
            <CardTitle className="text-gray-800 flex items-center gap-2">
              <MapPin size={20} />
              Getting Started
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <h4 className="font-semibold text-gray-800 mb-2">Location Options</h4>
                <ul className="text-sm text-gray-700 space-y-1">
                  <li>• Enter district name (e.g., "Lilongwe", "Blantyre")</li>
                  <li>• Use GPS coordinates (-13.9833, 33.7833)</li>
                  <li>• Supports all Malawi districts</li>
                </ul>
              </div>
              <div>
                <h4 className="font-semibold text-gray-800 mb-2">Data Types Available</h4>
                <ul className="text-sm text-gray-700 space-y-1">
                  <li>• 7-Day Weather Forecast</li>
                  <li>• Historical Data (1-10 years)</li>
                  <li>• Crop Recommendations</li>
                  <li>• Agricultural Impact Analysis</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default Weather;