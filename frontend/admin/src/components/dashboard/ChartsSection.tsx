import React from 'react';
import { useQuery } from 'react-query';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { Line, Doughnut } from 'react-chartjs-2';
import LoadingSpinner from '../ui/LoadingSpinner';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const fetchChartData = async () => {
  // Mock data for now
  await new Promise(resolve => setTimeout(resolve, 400));
  
  return {
    uploadActivity: {
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
      datasets: [
        {
          label: 'Documents Uploaded',
          data: [12, 19, 8, 15, 23, 18],
          borderColor: 'rgb(34, 197, 94)',
          backgroundColor: 'rgba(34, 197, 94, 0.2)',
          tension: 0.4,
        },
      ],
    },
    varietyDistribution: {
      labels: ['Maize', 'Groundnut', 'Beans', 'Sorghum', 'Rice', 'Others'],
      datasets: [
        {
          data: [45, 25, 15, 8, 4, 3],
          backgroundColor: [
            '#10B981',
            '#3B82F6',
            '#8B5CF6',
            '#F59E0B',
            '#EF4444',
            '#6B7280',
          ],
          borderWidth: 0,
        },
      ],
    },
  };
};

function ChartsSection() {
  const { data: chartData, isLoading } = useQuery(
    'chart-data',
    fetchChartData,
    {
      refetchInterval: 5 * 60 * 1000, // Refresh every 5 minutes
    }
  );

  const lineOptions = {
    responsive: true,
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: false,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(156, 163, 175, 0.1)',
        },
        ticks: {
          color: 'rgba(156, 163, 175, 0.8)',
        },
      },
      x: {
        grid: {
          color: 'rgba(156, 163, 175, 0.1)',
        },
        ticks: {
          color: 'rgba(156, 163, 175, 0.8)',
        },
      },
    },
  };

  const doughnutOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'bottom' as const,
        labels: {
          padding: 20,
          usePointStyle: true,
          color: 'rgba(156, 163, 175, 0.8)',
        },
      },
      title: {
        display: false,
      },
    },
    maintainAspectRatio: false,
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="card">
          <div className="card-body flex items-center justify-center h-64">
            <LoadingSpinner />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Upload Activity Chart */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
            Upload Activity
          </h3>
        </div>
        <div className="card-body">
          <div className="h-64">
            {chartData?.uploadActivity && (
              <Line data={chartData.uploadActivity} options={lineOptions} />
            )}
          </div>
        </div>
      </div>

      {/* Variety Distribution Chart */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
            Crop Variety Distribution
          </h3>
        </div>
        <div className="card-body">
          <div className="h-64">
            {chartData?.varietyDistribution && (
              <Doughnut data={chartData.varietyDistribution} options={doughnutOptions} />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default ChartsSection;