import React from 'react';
import { Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  TooltipItem,
} from 'chart.js';
import type { ServiceCost } from '@/types/cost.types';

ChartJS.register(ArcElement, Tooltip, Legend);

interface ServiceBreakdownChartProps {
  data: ServiceCost[];
  className?: string;
}

export const ServiceBreakdownChart: React.FC<ServiceBreakdownChartProps> = ({
  data,
  className = ''
}) => {
  const colors = [
    '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6',
    '#06B6D4', '#84CC16', '#F97316', '#EC4899', '#6B7280'
  ];

  const chartData = {
    labels: data.map(item => item.service),
    datasets: [
      {
        data: data.map(item => item.cost),
        backgroundColor: colors.slice(0, data.length),
        borderColor: colors.slice(0, data.length).map(color => color + '80'),
        borderWidth: 2,
        hoverOffset: 4,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'bottom' as const,
        labels: {
          padding: 20,
          usePointStyle: true,
          font: {
            size: 12,
          },
        },
      },
      tooltip: {
        callbacks: {
          label: function(context: TooltipItem<'doughnut'>) {
            const label = context.label || '';
            const value = context.parsed;
            const percentage = data[context.dataIndex]?.percentage || 0;
            return `${label}: $${value.toLocaleString()} (${percentage.toFixed(1)}%)`;
          },
        },
      },
    },
    maintainAspectRatio: false,
  };

  return (
    <div className={`service-breakdown-chart ${className}`}>
      <div className="h-80">
        <Doughnut data={chartData} options={options} />
      </div>
    </div>
  );
};

export default ServiceBreakdownChart;