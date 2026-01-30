import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'

interface CostChartProps {
  data: Array<{ date: string; cost: number }>
  title?: string
}

export default function CostChart({ data, title = 'Cost Trend' }: CostChartProps) {
  return (
    <div className="bg-ey-grey-dark rounded-lg p-6 border border-ey-grey-light">
      <h3 className="text-lg font-semibold text-white mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#3a3a3a" />
          <XAxis
            dataKey="date"
            stroke="#9ca3af"
            tick={{ fill: '#9ca3af' }}
          />
          <YAxis
            stroke="#9ca3af"
            tick={{ fill: '#9ca3af' }}
            tickFormatter={(value) => `$${value.toFixed(0)}`}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1a1a1a',
              border: '1px solid #3a3a3a',
              borderRadius: '0.5rem',
              color: '#fff',
            }}
            formatter={(value: number) => [`$${value.toFixed(2)}`, 'Cost']}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="cost"
            stroke="#FFE600"
            strokeWidth={2}
            dot={{ fill: '#FFE600', r: 4 }}
            activeDot={{ r: 6 }}
            name="Daily Cost"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
