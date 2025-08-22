import React from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface SavingsProjectionChartProps {
  currentCosts: number[];
  projectedSavings: number[];
  months: string[];
  className?: string;
}

export const SavingsProjectionChart: React.FC<SavingsProjectionChartProps> = ({
  currentCosts,
  projectedSavings,
  months,
  className = ''
}) => {
  const optimizedCosts = currentCosts.map((cost, index) => 
    cost - (projectedSavings[index] || 0)
  );

  const data = {
    labels: months,
    datasets: [
      {
        label: 'Current Costs',
        data: currentCosts,
        borderColor: '#EF4444',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        borderWidth: 2,
        fill: true,
        tension: 0.4,
      },
      {
        label: 'Optimized Costs',
        data: optimizedCosts,
        borderColor: '#10B981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        borderWidth: 2,
        fill: true,
        tension: 0.4,
      },
      {
        label: 'Potential Savings',
        data: projectedSavings,
        borderColor: '#3B82F6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        borderWidth: 2,
        fill: false,
        tension: 0.4,
        borderDash: [5, 5],
      },
    ],
  };

  const options = {
    responsive: true,
    interaction: {
      intersect: false,
      mode: 'index' as const,
    },
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Cost Savings Projection',
        font: {
          size: 16,
          weight: 'bold' as const,
        },
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            const label = context.dataset.label || '';
            const value = context.parsed.y;
            return `${label}: $${value.toLocaleString()}`;
          },
          afterBody: function(tooltipItems: any[]) {
            if (tooltipItems.length > 0) {
              const index = tooltipItems[0].dataIndex;
              const savings = projectedSavings[index];
              const currentCost = currentCosts[index];
              const percentageSaving = ((savings / currentCost) * 100).toFixed(1);
              return `Savings: ${percentageSaving}%`;
            }
            return '';
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: function(value: any) {
            return '$' + value.toLocaleString();
          },
        },
        title: {
          display: true,
          text: 'Cost ($)',
        },
      },
      x: {
        title: {
          display: true,
          text: 'Month',
        },
      },
    },
  };

  return (
    <div className={`savings-projection-chart ${className}`}>
      <Line data={data} options={options} />
    </div>
  );
};

export default SavingsProjectionChart;