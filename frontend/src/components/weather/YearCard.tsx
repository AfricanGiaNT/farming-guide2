import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card';
import { TrendingUp, Droplets, Thermometer, Calendar } from 'lucide-react';
import { getSortedMonths, getSeasonColor } from '../../utils/monthOrder';

interface YearCardProps {
  year: number;
  annualRainfall: number;
  avgTemperature: number;
  wettestMonth: string;
  driestMonth: string;
  monthlySummary: {
    wet_season_total: number;
    dry_season_total: number;
  };
  monthlyData: {
    [month: string]: {
      average_rainfall: number;
      min_rainfall: number;
      max_rainfall: number;
      average_temperature: number;
      years_analyzed: number;
    };
  };
}

const YearCard: React.FC<YearCardProps> = ({
  year,
  annualRainfall,
  avgTemperature,
  wettestMonth,
  driestMonth,
  monthlySummary,
  monthlyData
}) => {
  const sortedMonths = getSortedMonths(monthlyData);

  return (
    <Card className="hover:shadow-lg transition-all duration-200">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2">
          <Calendar size={20} className="text-blue-600" />
          <span className="text-lg font-bold">{year}</span>
        </CardTitle>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Key Metrics */}
        <div className="grid grid-cols-2 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-800">
              {annualRainfall.toFixed(0)}mm
            </div>
            <div className="text-sm text-blue-600 flex items-center justify-center gap-1">
              <Droplets size={14} />
              Annual Rainfall
            </div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-800">
              {avgTemperature.toFixed(1)}°C
            </div>
            <div className="text-sm text-green-600 flex items-center justify-center gap-1">
              <Thermometer size={14} />
              Avg Temperature
            </div>
          </div>
        </div>

        {/* Season Breakdown */}
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-green-50 p-3 rounded-lg border border-green-200">
            <div className="text-sm font-semibold text-green-800 mb-1">Wet Season</div>
            <div className="text-lg font-bold text-green-700">
              {monthlySummary.wet_season_total.toFixed(0)}mm
            </div>
            <div className="text-xs text-green-600">Nov - Apr</div>
          </div>
          <div className="bg-orange-50 p-3 rounded-lg border border-orange-200">
            <div className="text-sm font-semibold text-orange-800 mb-1">Dry Season</div>
            <div className="text-lg font-bold text-orange-700">
              {monthlySummary.dry_season_total.toFixed(0)}mm
            </div>
            <div className="text-xs text-orange-600">May - Oct</div>
          </div>
        </div>

        {/* Monthly Averages */}
        <div>
          <h4 className="text-sm font-semibold text-gray-700 mb-2">Monthly Averages</h4>
          <div className="grid grid-cols-3 gap-2">
            {sortedMonths.slice(0, 6).map((month) => {
              const data = monthlyData[month];
              const seasonColor = getSeasonColor(month);
              return (
                <div key={month} className={`${seasonColor} p-2 rounded text-center`}>
                  <div className="text-xs font-semibold">{month}</div>
                  <div className="text-xs">
                    {data.average_rainfall.toFixed(0)}mm
                  </div>
                  <div className="text-xs">
                    {data.average_temperature.toFixed(0)}°C
                  </div>
                </div>
              );
            })}
          </div>
          {sortedMonths.length > 6 && (
            <div className="text-center mt-2">
              <span className="text-xs text-gray-500">
                +{sortedMonths.length - 6} more months
              </span>
            </div>
          )}
        </div>

        {/* Weather Extremes */}
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-blue-50 p-2 rounded border border-blue-200">
            <div className="text-xs font-semibold text-blue-800">Wettest</div>
            <div className="text-sm font-bold text-blue-700">{wettestMonth}</div>
          </div>
          <div className="bg-red-50 p-2 rounded border border-red-200">
            <div className="text-xs font-semibold text-red-800">Driest</div>
            <div className="text-sm font-bold text-red-700">{driestMonth}</div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default YearCard;

