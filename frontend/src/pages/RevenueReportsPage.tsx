import React, { useEffect, useState } from 'react'
import { apiClient } from '@/services/api'
import { Machine, RevenueRecord } from '@/types'
import { AlertCircle, TrendingUp, BarChart3, Calendar } from 'lucide-react'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts'

const RevenueReportsPage: React.FC = () => {
  const [machines, setMachines] = useState<Machine[]>([])
  const [revenue, setRevenue] = useState<RevenueRecord[]>([])
  const [selectedMachine, setSelectedMachine] = useState<number | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [dateRange, setDateRange] = useState({
    startDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    endDate: new Date().toISOString().split('T')[0],
  })

  useEffect(() => {
    fetchData()
  }, [])

  useEffect(() => {
    if (selectedMachine) {
      fetchMachineRevenue(selectedMachine)
    } else {
      fetchAllRevenue()
    }
  }, [selectedMachine])

  const fetchData = async () => {
    try {
      setLoading(true)
      const machinesRes = await apiClient.getMachines()
      setMachines(machinesRes.machines || [])
      await fetchAllRevenue()
    } catch (err: any) {
      setError('Failed to load revenue data')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const fetchAllRevenue = async () => {
    try {
      const response = await apiClient.getRevenue()
      setRevenue(response.revenue || [])
    } catch (err: any) {
      setError('Failed to load revenue data')
    }
  }

  const fetchMachineRevenue = async (machineId: number) => {
    try {
      const response = await apiClient.getMachineRevenue(machineId)
      setRevenue(response.revenue || [])
    } catch (err: any) {
      setError('Failed to load machine revenue')
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="spinner spinner-border"></div>
      </div>
    )
  }

  // Calculate statistics
  const totalRevenue = revenue.reduce((sum, r) => sum + r.total_revenue, 0)
  const totalUnits = revenue.reduce((sum, r) => sum + r.units_sold, 0)
  const avgTransaction = revenue.length > 0 ? totalRevenue / totalUnits : 0
  const dailyAverage = revenue.length > 0 ? totalRevenue / revenue.length : 0

  // Prepare chart data
  const chartData = revenue
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
    .map((r) => ({
      date: new Date(r.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      revenue: r.total_revenue,
      units: r.units_sold,
      average: r.average_transaction,
    }))

  // Machine revenue breakdown
  const machineRevenue = machines
    .filter((m) => revenue.some((r) => r.id === m.id))
    .map((m) => ({
      name: m.machine_id,
      revenue: revenue
        .filter((r) => r.id === m.id)
        .reduce((sum, r) => sum + r.total_revenue, 0),
    }))
    .sort((a, b) => b.revenue - a.revenue)

  const COLORS = ['#E31E24', '#DC2626', '#B91C1C', '#991B1B', '#7F1D1D']

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold mb-2">Revenue Reports</h1>
        <p className="text-gray-400">Analyze your revenue performance</p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-4 bg-red-900 border border-red-700 rounded-lg flex items-start space-x-3">
          <AlertCircle className="text-red-400 flex-shrink-0 mt-0.5" size={20} />
          <p className="text-red-200">{error}</p>
        </div>
      )}

      {/* Filters */}
      <div className="card">
        <h3 className="text-lg font-bold mb-4">Filters</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="label">Machine</label>
            <select
              value={selectedMachine || ''}
              onChange={(e) => setSelectedMachine(e.target.value ? parseInt(e.target.value) : null)}
              className="input"
            >
              <option value="">All Machines</option>
              {machines.map((machine) => (
                <option key={machine.id} value={machine.id}>
                  {machine.machine_id} - {machine.location}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="label">Start Date</label>
            <input
              type="date"
              value={dateRange.startDate}
              onChange={(e) => setDateRange((prev) => ({ ...prev, startDate: e.target.value }))}
              className="input"
            />
          </div>
          <div>
            <label className="label">End Date</label>
            <input
              type="date"
              value={dateRange.endDate}
              onChange={(e) => setDateRange((prev) => ({ ...prev, endDate: e.target.value }))}
              className="input"
            />
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="card-hover">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Total Revenue</p>
              <p className="text-3xl font-bold mt-2">${totalRevenue.toFixed(2)}</p>
            </div>
            <TrendingUp className="text-snax-red" size={40} />
          </div>
        </div>

        <div className="card-hover">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Total Units Sold</p>
              <p className="text-3xl font-bold mt-2">{totalUnits}</p>
            </div>
            <BarChart3 className="text-snax-red" size={40} />
          </div>
        </div>

        <div className="card-hover">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Avg Transaction</p>
              <p className="text-3xl font-bold mt-2">${avgTransaction.toFixed(2)}</p>
            </div>
            <TrendingUp className="text-snax-red" size={40} />
          </div>
        </div>

        <div className="card-hover">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Daily Average</p>
              <p className="text-3xl font-bold mt-2">${dailyAverage.toFixed(2)}</p>
            </div>
            <Calendar className="text-snax-red" size={40} />
          </div>
        </div>
      </div>

      {/* Revenue Trend Chart */}
      {chartData.length > 0 && (
        <div className="card">
          <h2 className="text-xl font-bold mb-4">Revenue Trend</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="date" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip
                contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }}
                labelStyle={{ color: '#F3F4F6' }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="revenue"
                stroke="#E31E24"
                strokeWidth={2}
                dot={false}
                name="Revenue ($)"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Units Sold Chart */}
      {chartData.length > 0 && (
        <div className="card">
          <h2 className="text-xl font-bold mb-4">Units Sold</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="date" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip
                contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }}
                labelStyle={{ color: '#F3F4F6' }}
              />
              <Bar dataKey="units" fill="#E31E24" name="Units Sold" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Machine Revenue Breakdown */}
      {machineRevenue.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card">
            <h2 className="text-xl font-bold mb-4">Revenue by Machine</h2>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={machineRevenue}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, revenue }) => `${name}: $${revenue.toFixed(0)}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="revenue"
                >
                  {machineRevenue.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }}
                  labelStyle={{ color: '#F3F4F6' }}
                  formatter={(value) => `$${value.toFixed(2)}`}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="card">
            <h2 className="text-xl font-bold mb-4">Machine Rankings</h2>
            <div className="space-y-3">
              {machineRevenue.map((machine, index) => (
                <div key={machine.name} className="flex items-center justify-between p-3 bg-gray-800 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div
                      className="w-4 h-4 rounded"
                      style={{ backgroundColor: COLORS[index % COLORS.length] }}
                    ></div>
                    <span className="font-medium">{machine.name}</span>
                  </div>
                  <span className="text-snax-red font-bold">${machine.revenue.toFixed(2)}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Detailed Revenue Table */}
      {revenue.length > 0 && (
        <div className="card overflow-x-auto">
          <h2 className="text-xl font-bold mb-4">Detailed Revenue</h2>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-700">
                <th className="text-left py-3 px-4 text-gray-400 font-medium">Date</th>
                <th className="text-left py-3 px-4 text-gray-400 font-medium">Units Sold</th>
                <th className="text-left py-3 px-4 text-gray-400 font-medium">Total Revenue</th>
                <th className="text-left py-3 px-4 text-gray-400 font-medium">Avg Transaction</th>
              </tr>
            </thead>
            <tbody>
              {revenue
                .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
                .slice(0, 30)
                .map((r) => (
                  <tr key={r.id} className="border-b border-gray-700 hover:bg-gray-800 transition-colors">
                    <td className="py-3 px-4">{new Date(r.date).toLocaleDateString()}</td>
                    <td className="py-3 px-4">{r.units_sold}</td>
                    <td className="py-3 px-4 font-medium">${r.total_revenue.toFixed(2)}</td>
                    <td className="py-3 px-4">${r.average_transaction.toFixed(2)}</td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default RevenueReportsPage
