import React, { useEffect, useState } from 'react'
import { apiClient } from '@/services/api'
import { useAuthStore } from '@/stores/authStore'
import { DashboardOverview, RevenueSummary, MachineStatus } from '@/types'
import { BarChart3, Zap, Package, AlertCircle, TrendingUp, Activity } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

const DashboardPage: React.FC = () => {
  const { customer } = useAuthStore()
  const [overview, setOverview] = useState<DashboardOverview | null>(null)
  const [revenueSummary, setRevenueSummary] = useState<RevenueSummary | null>(null)
  const [machineStatus, setMachineStatus] = useState<MachineStatus[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true)
        const [overviewData, revenueData, statusData] = await Promise.all([
          apiClient.getDashboardOverview(),
          apiClient.getRevenueSummary(),
          apiClient.getMachineStatus(),
        ])
        setOverview(overviewData)
        setRevenueSummary(revenueData)
        setMachineStatus(statusData.machines || [])
      } catch (err: any) {
        setError('Failed to load dashboard data')
        console.error(err)
      } finally {
        setLoading(false)
      }
    }

    fetchDashboardData()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="spinner spinner-border"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold mb-2">Dashboard</h1>
        <p className="text-gray-400">Welcome back, {customer?.company_name}</p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-4 bg-red-900 border border-red-700 rounded-lg flex items-start space-x-3">
          <AlertCircle className="text-red-400 flex-shrink-0 mt-0.5" size={20} />
          <p className="text-red-200">{error}</p>
        </div>
      )}

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Machines */}
        <div className="card-hover">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Total Machines</p>
              <p className="text-3xl font-bold mt-2">{overview?.total_machines || 0}</p>
              <p className="text-xs text-green-400 mt-1">
                {overview?.online_machines || 0} online
              </p>
            </div>
            <Zap className="text-snax-red" size={40} />
          </div>
        </div>

        {/* Revenue (30 days) */}
        <div className="card-hover">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Revenue (30 Days)</p>
              <p className="text-3xl font-bold mt-2">
                ${(overview?.revenue_30_days || 0).toFixed(2)}
              </p>
              <p className="text-xs text-gray-400 mt-1">Total earnings</p>
            </div>
            <TrendingUp className="text-snax-red" size={40} />
          </div>
        </div>

        {/* Low Stock Alerts */}
        <div className="card-hover">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Low Stock Alerts</p>
              <p className="text-3xl font-bold mt-2">{overview?.low_stock_alerts || 0}</p>
              <p className="text-xs text-yellow-400 mt-1">Items to restock</p>
            </div>
            <Package className="text-snax-red" size={40} />
          </div>
        </div>

        {/* Open Tickets */}
        <div className="card-hover">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Open Tickets</p>
              <p className="text-3xl font-bold mt-2">{overview?.open_tickets || 0}</p>
              <p className="text-xs text-blue-400 mt-1">Support requests</p>
            </div>
            <AlertCircle className="text-snax-red" size={40} />
          </div>
        </div>
      </div>

      {/* Revenue Chart */}
      {revenueSummary && revenueSummary.daily_revenue.length > 0 && (
        <div className="card">
          <h2 className="text-xl font-bold mb-4">Revenue Trend (Last 30 Days)</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={revenueSummary.daily_revenue}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="date" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip
                contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }}
                labelStyle={{ color: '#F3F4F6' }}
              />
              <Line
                type="monotone"
                dataKey="revenue"
                stroke="#E31E24"
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Machine Status */}
      <div className="card">
        <h2 className="text-xl font-bold mb-4">Machine Status</h2>
        {machineStatus.length > 0 ? (
          <div className="space-y-3">
            {machineStatus.map((machine) => (
              <div key={machine.id} className="flex items-center justify-between p-4 bg-gray-800 rounded-lg">
                <div className="flex-1">
                  <p className="font-medium">{machine.machine_id}</p>
                  <p className="text-sm text-gray-400">{machine.location}</p>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="text-right">
                    <p className="text-sm text-gray-400">Inventory</p>
                    <p className="font-bold">{machine.inventory_percentage}%</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-400">Revenue</p>
                    <p className="font-bold">${machine.monthly_revenue.toFixed(2)}</p>
                  </div>
                  <div>
                    <span
                      className={`px-3 py-1 rounded-full text-sm font-medium ${
                        machine.status === 'online'
                          ? 'bg-green-900 text-green-200'
                          : machine.status === 'offline'
                          ? 'bg-red-900 text-red-200'
                          : 'bg-yellow-900 text-yellow-200'
                      }`}
                    >
                      {machine.status}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-400">No machines found</p>
        )}
      </div>

      {/* Recent Activities */}
      {overview && overview.recent_activities.length > 0 && (
        <div className="card">
          <h2 className="text-xl font-bold mb-4">Recent Activities</h2>
          <div className="space-y-3">
            {overview.recent_activities.slice(0, 5).map((activity) => (
              <div key={activity.id} className="flex items-start space-x-3 p-3 bg-gray-800 rounded-lg">
                <Activity className="text-snax-red flex-shrink-0 mt-1" size={18} />
                <div className="flex-1">
                  <p className="text-sm font-medium">{activity.description}</p>
                  <p className="text-xs text-gray-400 mt-1">
                    {new Date(activity.created_at).toLocaleString()}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default DashboardPage
