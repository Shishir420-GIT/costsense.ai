import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Activity, TrendingUp, TrendingDown, DollarSign, AlertCircle, FileText } from 'lucide-react'
import { costsAPI, investigationsAPI, ticketsAPI } from '../services/api'
import CostChart from '../components/CostChart'

export default function Dashboard() {
  const [health, setHealth] = useState<any>(null)
  const [wsStatus, setWsStatus] = useState<'connected' | 'disconnected'>('disconnected')

  // Fetch cost summary
  const { data: costSummary } = useQuery({
    queryKey: ['cost-summary'],
    queryFn: () => costsAPI.getSummary(30),
  })

  // Fetch cost trend
  const { data: costTrend } = useQuery({
    queryKey: ['cost-trend'],
    queryFn: () => costsAPI.getTrend(30),
  })

  // Fetch investigations
  const { data: investigations } = useQuery({
    queryKey: ['investigations'],
    queryFn: () => investigationsAPI.list(undefined, 5),
  })

  // Fetch tickets
  const { data: tickets } = useQuery({
    queryKey: ['tickets'],
    queryFn: () => ticketsAPI.list(undefined, 5),
  })

  useEffect(() => {
    fetch('/health')
      .then(res => res.json())
      .then(data => setHealth(data))
      .catch(err => console.error('Health check failed:', err))

    const ws = new WebSocket(`ws://${window.location.hostname}:8000/ws`)

    ws.onopen = () => {
      setWsStatus('connected')
      ws.send('ping')
    }

    ws.onmessage = (event) => {
      console.log('WebSocket message:', event.data)
    }

    ws.onclose = () => {
      setWsStatus('disconnected')
    }

    return () => {
      ws.close()
    }
  }, [])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-white">Cost Overview</h1>
        <div className="flex items-center space-x-2">
          <Activity className={`h-5 w-5 ${wsStatus === 'connected' ? 'text-green-400' : 'text-red-400'}`} />
          <span className="text-sm text-gray-400">
            {wsStatus === 'connected' ? 'Live' : 'Disconnected'}
          </span>
        </div>
      </div>

      {health && (
        <div className="bg-ey-grey-dark rounded-lg p-4 border border-ey-grey-light">
          <div className="flex items-center space-x-2">
            <div className="h-3 w-3 bg-ey-yellow rounded-full"></div>
            <span className="text-gray-300">Backend: {health.status}</span>
            <span className="text-gray-500">v{health.version}</span>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard
          title="Total Monthly Cost"
          value={`$${costSummary?.data?.total_cost?.toFixed(2) || '0.00'}`}
          change="+0%"
          trend="up"
          icon={<DollarSign className="h-6 w-6" />}
        />
        <StatCard
          title="Potential Savings"
          value="$0.00"
          change="0%"
          trend="down"
          icon={<TrendingDown className="h-6 w-6" />}
        />
        <StatCard
          title="Resources Tracked"
          value={costSummary?.data?.record_count?.toString() || '0'}
          change="+0"
          trend="neutral"
          icon={<Activity className="h-6 w-6" />}
        />
      </div>

      {/* Cost Trend Chart */}
      {costTrend?.data?.trend && costTrend.data.trend.length > 0 && (
        <CostChart data={costTrend.data.trend} title="30-Day Cost Trend" />
      )}

      {/* Recent Activity */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Recent Investigations */}
        <div className="bg-ey-grey-dark rounded-lg p-6 border border-ey-grey-light">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white flex items-center">
              <AlertCircle className="h-5 w-5 text-ey-yellow mr-2" />
              Recent Investigations
            </h3>
          </div>
          {investigations?.data?.length > 0 ? (
            <div className="space-y-3">
              {investigations.data.slice(0, 5).map((inv: any) => (
                <div key={inv.id} className="border-l-4 border-ey-yellow pl-3">
                  <p className="text-white text-sm font-medium">{inv.title}</p>
                  <p className="text-gray-400 text-xs mt-1">Status: {inv.status}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-400 text-sm">No investigations yet</p>
          )}
        </div>

        {/* Recent Tickets */}
        <div className="bg-ey-grey-dark rounded-lg p-6 border border-ey-grey-light">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white flex items-center">
              <FileText className="h-5 w-5 text-ey-yellow mr-2" />
              Recent Tickets
            </h3>
          </div>
          {tickets?.data?.length > 0 ? (
            <div className="space-y-3">
              {tickets.data.slice(0, 5).map((ticket: any) => (
                <div key={ticket.id} className="border-l-4 border-ey-yellow pl-3">
                  <p className="text-white text-sm font-medium">{ticket.title}</p>
                  <p className="text-gray-400 text-xs mt-1">
                    {ticket.ticket_number || 'Draft'} • {ticket.status}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-400 text-sm">No tickets yet</p>
          )}
        </div>
      </div>

      <div className="bg-ey-grey-dark rounded-lg p-6 border border-ey-grey-light">
        <h2 className="text-xl font-semibold text-white mb-4">Welcome to CostSense AI</h2>
        <p className="text-gray-300 mb-4">
          Your multi-cloud cost intelligence platform is ready. Connect your cloud providers to start tracking costs and discovering optimization opportunities.
        </p>
        <div className="flex space-x-4">
          <button className="px-4 py-2 bg-ey-yellow hover:bg-ey-yellow-dark text-black font-semibold rounded-lg transition-colors">
            Connect AWS
          </button>
          <button className="px-4 py-2 bg-ey-grey-medium hover:bg-ey-grey-light text-white rounded-lg transition-colors border border-ey-grey-light">
            Connect Azure
          </button>
          <button className="px-4 py-2 bg-ey-grey-medium hover:bg-ey-grey-light text-white rounded-lg transition-colors border border-ey-grey-light">
            Connect GCP
          </button>
        </div>
      </div>
    </div>
  )
}

interface StatCardProps {
  title: string
  value: string
  change: string
  trend: 'up' | 'down' | 'neutral'
  icon: React.ReactNode
}

function StatCard({ title, value, change, trend, icon }: StatCardProps) {
  const trendColor = trend === 'up' ? 'text-red-400' : trend === 'down' ? 'text-ey-yellow' : 'text-gray-400'

  return (
    <div className="bg-ey-grey-dark rounded-lg p-6 border border-ey-grey-light">
      <div className="flex items-center justify-between mb-2">
        <span className="text-gray-400 text-sm font-medium">{title}</span>
        <div className={trendColor}>{icon}</div>
      </div>
      <div className="text-3xl font-bold text-white mb-1">{value}</div>
      <div className={`text-sm ${trendColor}`}>{change} from last month</div>
    </div>
  )
}
