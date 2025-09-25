import React from 'react';
import { Card, CardContent } from '../ui/Card';
import { Cloud, Droplets, Wind, Sun } from 'lucide-react';
import { WeatherData } from '../../types';

interface WeatherWidgetProps {
  weather: WeatherData;
  compact?: boolean;
}

const WeatherWidget: React.FC<WeatherWidgetProps> = ({ weather, compact = false }) => {
  const { current, location } = weather;

  if (compact) {
    return (
      <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white">
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm">{location}</p>
              <p className="text-2xl font-bold">{current.temperature}°C</p>
              <p className="text-blue-100 text-sm">{current.description}</p>
            </div>
            <div className="text-right">
              <Cloud size={32} className="text-blue-100 mb-2" />
              <div className="flex items-center gap-2 text-sm text-blue-100">
                <Droplets size={14} />
                <span>{current.humidity}%</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white">
      <CardContent className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold mb-1">Current Weather</h3>
            <p className="text-blue-100">{location}</p>
          </div>
          <Cloud size={40} className="text-blue-200" />
        </div>

        <div className="mb-4">
          <div className="text-3xl font-bold mb-1">{current.temperature}°C</div>
          <p className="text-blue-100">{current.description}</p>
        </div>

        <div className="grid grid-cols-3 gap-4">
          <div className="flex items-center gap-2">
            <Droplets size={16} className="text-blue-200" />
            <div>
              <p className="text-xs text-blue-200">Humidity</p>
              <p className="font-semibold">{current.humidity}%</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Wind size={16} className="text-blue-200" />
            <div>
              <p className="text-xs text-blue-200">Wind</p>
              <p className="font-semibold">{current.windSpeed}km/h</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Sun size={16} className="text-blue-200" />
            <div>
              <p className="text-xs text-blue-200">UV Index</p>
              <p className="font-semibold">{current.uvIndex}</p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default WeatherWidget;