import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  BarElement,
} from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';
import { DailyForecast } from '../../types';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface ForecastChartProps {
  forecast: DailyForecast[];
  type: 'temperature' | 'rainfall';
}

const ForecastChart: React.FC<ForecastChartProps> = ({ forecast, type }) => {
  const labels = forecast.map(day => 
    new Date(day.date).toLocaleDateString('en-GB', { 
      weekday: 'short', 
      day: 'numeric' 
    })
  );

  if (type === 'temperature') {
    const data = {
      labels,
      datasets: [
        {
          label: 'High',
          data: forecast.map(day => day.tempHigh),
          borderColor: '#F97316',
          backgroundColor: '#FED7AA',
          fill: '+1',
        },
        {
          label: 'Low',
          data: forecast.map(day => day.tempLow),
          borderColor: '#3B82F6',
          backgroundColor: '#DBEAFE',
          fill: 'origin',
        },
      ],
    };

    const options = {
      responsive: true,
      plugins: {
        legend: {
          position: 'top' as const,
        },
        title: {
          display: true,
          text: '7-Day Temperature Forecast',
        },
      },
      scales: {
        y: {
          beginAtZero: false,
          title: {
            display: true,
            text: 'Temperature (°C)',
          },
        },
      },
    };

    return <Line data={data} options={options} />;
  }

  const data = {
    labels,
    datasets: [
      {
        label: 'Rainfall (mm)',
        data: forecast.map(day => day.rainfall),
        backgroundColor: '#3B82F6',
        borderColor: '#1D4ED8',
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: '7-Day Rainfall Forecast',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Rainfall (mm)',
        },
      },
    },
  };

  return <Bar data={data} options={options} />;
};

export default ForecastChart;