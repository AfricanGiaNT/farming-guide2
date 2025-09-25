import React from 'react';
import { Link } from 'react-router-dom';
import WeatherWidget from '../components/weather/WeatherWidget';
import { Card, CardContent, CardTitle } from '../components/ui/Card';
import { Cloud, Sprout, Search, Database, TrendingUp, Users } from 'lucide-react';
import { mockWeatherData } from '../utils/mockData';

const Home: React.FC = () => {
  const quickActions = [
    {
      title: 'Weather Forecast',
      description: 'Check 7-day weather',
      icon: Cloud,
      link: '/weather',
      color: 'bg-blue-500 hover:bg-blue-600'
    },
    {
      title: 'Crop Advice',
      description: 'Get recommendations',
      icon: Sprout,
      link: '/crops',
      color: 'bg-green-500 hover:bg-green-600'
    },
    {
      title: 'Find Varieties',
      description: 'Search crop varieties',
      icon: Database,
      link: '/varieties',
      color: 'bg-purple-500 hover:bg-purple-600'
    },
    {
      title: 'Knowledge Base',
      description: 'Search guides & tips',
      icon: Search,
      link: '/search',
      color: 'bg-orange-500 hover:bg-orange-600'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center md:text-left">
        <h1 className="text-2xl md:text-3xl font-bold text-gray-900 mb-2">
          Welcome to Mlangizi wa Ulimi
        </h1>
        <p className="text-gray-600">
          Your agricultural advisory companion for better farming in Malawi
        </p>
      </div>

      {/* Weather Widget */}
      <WeatherWidget weather={mockWeatherData} />

      {/* Quick Actions */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {quickActions.map((action, index) => (
            <Link key={index} to={action.link}>
              <Card className="text-center hover:shadow-lg transition-all duration-200 hover:scale-105">
                <CardContent className="p-4">
                  <div className={`w-12 h-12 ${action.color} rounded-lg flex items-center justify-center mx-auto mb-3 transition-colors`}>
                    <action.icon size={24} className="text-white" />
                  </div>
                  <CardTitle className="text-sm font-semibold text-gray-900 mb-1">
                    {action.title}
                  </CardTitle>
                  <p className="text-xs text-gray-600">{action.description}</p>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </div>

      {/* Recent Activity & Stats */}
      <div className="grid md:grid-cols-2 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-3 mb-4">
              <TrendingUp className="text-green-600" size={24} />
              <div>
                <h3 className="font-semibold text-gray-900">Farming Season Progress</h3>
                <p className="text-sm text-gray-600">Rainy season insights</p>
              </div>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Planting Window</span>
                <span className="text-sm font-medium text-green-600">Active</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Rainfall This Month</span>
                <span className="text-sm font-medium">45mm</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Best Crops Now</span>
                <span className="text-sm font-medium">Maize, Groundnuts</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-3 mb-4">
              <Users className="text-blue-600" size={24} />
              <div>
                <h3 className="font-semibold text-gray-900">Community Insights</h3>
                <p className="text-sm text-gray-600">What farmers are doing</p>
              </div>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Popular Searches</span>
                <span className="text-sm font-medium">Fall Armyworm</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Trending Varieties</span>
                <span className="text-sm font-medium">SC627, DK8053</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Active Farmers</span>
                <span className="text-sm font-medium text-green-600">1,234</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Home;