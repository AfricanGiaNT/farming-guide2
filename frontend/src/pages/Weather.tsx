import React, { useState, useEffect } from 'react';
import WeatherWidget from '../components/weather/WeatherWidget';
import ForecastChart from '../components/weather/ForecastChart';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Cloud, Sun, CloudRain, MapPin, Calendar, Loader2, Search, TrendingUp, Sprout } from 'lucide-react';
import { apiService, WeatherData, CropResponse, HistoricalWeatherData } from '../services/api';

const Weather: React.FC = () => {
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
  const [historicalYears, setHistoricalYears] = useState(5);
  const [dataType, setDataType] = useState<'current' | 'historical'>('current');
  
  // Current location for display
  const [currentLocation, setCurrentLocation] = useState<string>('');

  const getWeatherIcon = (iconName: string) => {
    switch (iconName) {
      case 'sun': return Sun;
      case 'cloud': return Cloud;
      case 'cloud-rain': return CloudRain;
      default: return Cloud;
    }
  };

  // Search for weather data
  const handleWeatherSearch = async () => {
    if (!locationInput && (!coordinates.lat || !coordinates.lon)) {
      setError('Please enter either a location name or GPS coordinates');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      let searchLocation = locationInput;
      if (coordinates.lat && coordinates.lon) {
        searchLocation = `${coordinates.lat},${coordinates.lon}`;
      }
      
      if (dataType === 'current') {
        const data = await apiService.getWeather(searchLocation);
        setWeatherData(data);
        setHistoricalData(null);
      } else {
        const data = await apiService.getHistoricalWeather(searchLocation, historicalYears);
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

  // Search for crop recommendations based on weather
  const handleCropSearch = async (location?: string) => {
    const searchLocation = location || currentLocation;
    if (!searchLocation) return;

    try {
      setLoadingCrops(true);
      const cropData = await apiService.getCrops(searchLocation, 'current');
      setCropRecommendations(cropData);
    } catch (err) {
      console.error('Crop fetch error:', err);
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
          <div className="grid md:grid-cols-2 gap-4">
            {/* Location Input */}
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

            {/* GPS Coordinates */}
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
          </div>

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
              </CardTitle>
              {(historicalData as any).period_start && (historicalData as any).period_end && (
                <p className="text-sm text-gray-600 mt-1">
                  Analysis Period: {new Date((historicalData as any).period_start).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })} to {new Date((historicalData as any).period_end).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}
                </p>
              )}
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-4 gap-4 mb-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-800">
                    {historicalData.climate_summary.total_annual_rainfall.toFixed(0)}mm
                  </div>
                  <div className="text-sm text-blue-600">Annual Rainfall</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-800">
                    {historicalData.climate_summary.wettest_month}
                  </div>
                  <div className="text-sm text-green-600">Wettest Month</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-red-800">
                    {historicalData.climate_summary.driest_month}
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
                
                {historicalData.years_analyzed > 1 ? (
                  // Simplified view for multi-year data
                  <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-3">
                    {Object.entries(historicalData.key_monthly_averages || historicalData.monthly_averages).map(([month, data]) => (
                      <div key={month} className="bg-gray-50 p-3 rounded-lg">
                        <div className="font-semibold text-gray-800 text-sm mb-1">{month}</div>
                        <div className="text-xs text-gray-600 space-y-1">
                          <div>Rainfall: {data.average_rainfall}mm</div>
                          <div>Temp: {data.average_temperature}°C</div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  // Full view for single year data
                  <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                    {Object.entries(historicalData.monthly_averages).map(([month, data]) => (
                      <div key={month} className="bg-gray-50 p-3 rounded-lg">
                        <div className="font-semibold text-gray-800 text-sm mb-1">{month}</div>
                        <div className="text-xs text-gray-600 space-y-1">
                          <div>Rainfall: {data.average_rainfall}mm</div>
                          <div>Temp: {data.average_temperature}°C</div>
                          <div className="text-xs text-gray-500">
                            Range: {data.min_rainfall}-{data.max_rainfall}mm
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              
              {/* Yearly Breakdown for Multi-Year Data */}
              {historicalData.years_analyzed > 1 && historicalData.yearly_breakdown && (
                <div className="mt-6">
                  <h4 className="font-semibold text-gray-800 mb-3">Year-by-Year Breakdown</h4>
                  <div className="space-y-4">
                    {historicalData.yearly_breakdown.map((yearData) => (
                      <div key={yearData.year} className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                        <div className="flex items-center justify-between mb-3">
                          <h5 className="font-semibold text-blue-800 text-lg">{yearData.year}</h5>
                          <div className="text-sm text-blue-600">
                            Avg Temp: {yearData.avg_temperature}°C
                          </div>
                        </div>
                        
                        <div className="grid md:grid-cols-4 gap-4 mb-3">
                          <div className="text-center">
                            <div className="text-xl font-bold text-blue-800">
                              {yearData.annual_rainfall}mm
                            </div>
                            <div className="text-xs text-blue-600">Annual Rainfall</div>
                          </div>
                          <div className="text-center">
                            <div className="text-lg font-semibold text-green-800">
                              {yearData.wettest_month}
                            </div>
                            <div className="text-xs text-green-600">Wettest Month</div>
                          </div>
                          <div className="text-center">
                            <div className="text-lg font-semibold text-red-800">
                              {yearData.driest_month}
                            </div>
                            <div className="text-xs text-red-600">Driest Month</div>
                          </div>
                          <div className="text-center">
                            <div className="text-sm text-gray-700">
                              <div>Wet Season: {yearData.monthly_summary.wet_season_total.toFixed(0)}mm</div>
                              <div>Dry Season: {yearData.monthly_summary.dry_season_total.toFixed(0)}mm</div>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </>
      )}

      {/* Crop Recommendations */}
      {cropRecommendations && (
        <Card className="bg-yellow-50 border-yellow-200">
          <CardHeader>
            <CardTitle className="text-yellow-800 flex items-center gap-2">
              <Sprout size={20} />
              Crop Recommendations Based on Weather Data
              {loadingCrops && <Loader2 size={16} className="animate-spin" />}
              {cropRecommendations.mock_data && (
                <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">
                  Demo Data
                </span>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-yellow-700 mb-4">
              Based on weather conditions for <strong>{cropRecommendations.location}</strong>, here are the recommended crops:
            </p>
            
            <div className="grid md:grid-cols-2 gap-4">
              {cropRecommendations.recommendations.slice(0, 6).map((crop, index) => (
                <div key={index} className="bg-white p-4 rounded-lg border border-yellow-200">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold text-yellow-800 capitalize">
                      {crop.crop_data?.name || crop.crop || 'Unknown Crop'}
                    </h4>
                    <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded">
                      {crop.score || crop.total_score || 0}% match
                    </span>
                  </div>
                  
                  <div className="space-y-1 text-sm text-gray-700">
                    <p><strong>Category:</strong> {crop.crop_data?.category || 'Not specified'}</p>
                    <p><strong>Description:</strong> {crop.crop_data?.description || 'No description available'}</p>
                    <p><strong>Suitability:</strong> {crop.suitability_level || 'Unknown'}</p>
                    <p><strong>Sources:</strong> {crop.sources?.length || 0} guide(s)</p>
                  </div>
                </div>
              ))}
            </div>

            {cropRecommendations.recommendations.length > 6 && (
              <div className="mt-4 text-center">
                <button
                  onClick={() => window.location.href = '/crops'}
                  className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 text-sm"
                >
                  View All {cropRecommendations.recommendations.length} Recommendations
                </button>
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