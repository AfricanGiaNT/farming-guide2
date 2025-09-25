import React, { useState } from 'react';
import WeatherWidget from '../components/weather/WeatherWidget';
import ForecastChart from '../components/weather/ForecastChart';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Cloud, Sun, CloudRain, MapPin, Calendar } from 'lucide-react';
import { mockWeatherData } from '../utils/mockData';

const Weather: React.FC = () => {
  const [chartType, setChartType] = useState<'temperature' | 'rainfall'>('temperature');

  const getWeatherIcon = (iconName: string) => {
    switch (iconName) {
      case 'sun': return Sun;
      case 'cloud': return Cloud;
      case 'cloud-rain': return CloudRain;
      default: return Cloud;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Weather Forecast</h1>
          <div className="flex items-center gap-2 text-gray-600">
            <MapPin size={16} />
            <span className="text-sm">{mockWeatherData.location}, Malawi</span>
          </div>
        </div>
      </div>

      {/* Current Weather */}
      <WeatherWidget weather={mockWeatherData} />

      {/* Chart Controls */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>7-Day Forecast</CardTitle>
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
          <ForecastChart forecast={mockWeatherData.forecast} type={chartType} />
        </CardContent>
      </Card>

      {/* Daily Forecast Cards */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Daily Details</h3>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {mockWeatherData.forecast.map((day, index) => {
            const WeatherIcon = getWeatherIcon(day.icon);
            return (
              <Card key={index}>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <Calendar size={16} className="text-gray-500" />
                      <span className="text-sm font-medium">
                        {new Date(day.date).toLocaleDateString('en-GB', { 
                          weekday: 'short', 
                          day: 'numeric',
                          month: 'short'
                        })}
                      </span>
                    </div>
                    <WeatherIcon size={20} className="text-gray-600" />
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">High / Low</span>
                      <span className="font-semibold">{day.tempHigh}° / {day.tempLow}°</span>
                    </div>
                    
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Rain Chance</span>
                      <span className="font-semibold text-blue-600">{day.rainChance}%</span>
                    </div>
                    
                    {day.rainfall > 0 && (
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">Expected Rain</span>
                        <span className="font-semibold text-blue-600">{day.rainfall}mm</span>
                      </div>
                    )}
                    
                    <p className="text-xs text-gray-600 mt-2">{day.description}</p>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>

      {/* Agricultural Insights */}
      <Card className="bg-green-50 border-green-200">
        <CardHeader>
          <CardTitle className="text-green-800 flex items-center gap-2">
            <Sun size={20} />
            Agricultural Insights
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <h4 className="font-semibold text-green-800 mb-2">This Week's Recommendations</h4>
              <ul className="text-sm text-green-700 space-y-1">
                <li>• Good week for land preparation</li>
                <li>• Heavy rain expected Wed-Thu</li>
                <li>• Consider delaying fertilizer application</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-green-800 mb-2">Crop Activities</h4>
              <ul className="text-sm text-green-700 space-y-1">
                <li>• Maize: Continue planting window</li>
                <li>• Groundnuts: Ideal conditions</li>
                <li>• Monitor for pest pressure after rain</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Weather;