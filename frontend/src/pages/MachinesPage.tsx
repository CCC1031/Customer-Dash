import React, { useState, useEffect } from 'react'
import { apiClient } from '@/services/api'
import { AlertCircle, Zap, TrendingUp, ShoppingCart, Clock, RefreshCw } from 'lucide-react'

interface HahaMachine {
  sticker_num: string
  device_name: string
  order_count: number
  total_revenue: number
  last_order_time: string | null
}

const MachinesPage: React.FC = () => {
  const [machines, setMachines] = useState<HahaMachine[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [refreshing, setRefreshing] = useState(false)

  useEffect(() => {
    fetchMachines()
  }, [])

  const fetchMachines = async (isRefresh = false) => {
    try {
      if (isRefresh) setRefreshing(true)
      else setLoading(true)
      const response = await apiClient.getHahaMachines()
      setMachines(response.machines || [])
      setError('')
    } catch (err: any) {
      setError('Failed to load machines from HAHA API')
      console.error(err)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  const formatRevenue = (val: number) =>
    `$${val.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`

  const formatTime = (t: string | null) => {
    if (!t) return 'No recent orders'
    const d = new Date(t.replace(' ', 'T'))
    return d.toLocaleString('en-US', {
      month: 'short', day: 'numeric',
      hour: 'numeric', minute: '2-digit', hour12: true,
    })
  }

  // Determine status based on last order time
  const getMachineStatus = (lastOrder: string | null) => {
    if (!lastOrder) return { label: 'Inactive', color: 'bg-gray-700 text-gray-300' }
    const diff = Date.now() - new Date(lastOrder.replace(' ', 'T')).getTime()
    const hours = diff / (1000 * 60 * 60)
    if (hours < 24) return { label: 'Active', color: 'bg-green-900 text-green-200' }
    if (hours < 72) return { label: 'Idle', color: 'bg-yellow-900 text-yellow-200' }
    return { label: 'Offline', color: 'bg-red-900 text-red-200' }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="w-10 h-10 border-2 border-snax-red border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
          <p className="text-gray-400">Loading machines from HAHA API...</p>
        </div>
      </div>
    )
  }

  const totalRevenue = machines.reduce((sum, m) => sum + m.total_revenue, 0)
  const totalOrders = machines.reduce((sum, m) => sum + m.order_count, 0)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl md:text-4xl font-bold mb-1 md:mb-2">Machines</h1>
          <p className="text-gray-400">Live data from HAHA vending network — last 30 days</p>
        </div>
        <button
          onClick={() => fetchMachines(true)}
          disabled={refreshing}
          className="btn-secondary flex items-center space-x-2"
        >
          <RefreshCw size={16} className={refreshing ? 'animate-spin' : ''} />
          <span>{refreshing ? 'Refreshing...' : 'Refresh'}</span>
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="p-4 bg-red-900 border border-red-700 rounded-lg flex items-start space-x-3">
          <AlertCircle className="text-red-400 flex-shrink-0 mt-0.5" size={20} />
          <p className="text-red-200">{error}</p>
        </div>
      )}

      {/* Summary Row */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        <div className="card text-center">
          <p className="text-gray-400 text-sm mb-1">Total Machines</p>
          <p className="text-3xl font-bold text-snax-red">{machines.length}</p>
        </div>
        <div className="card text-center">
          <p className="text-gray-400 text-sm mb-1">30-Day Revenue</p>
          <p className="text-3xl font-bold text-green-400">{formatRevenue(totalRevenue)}</p>
        </div>
        <div className="card text-center col-span-2 md:col-span-1">
          <p className="text-gray-400 text-sm mb-1">Total Orders</p>
          <p className="text-3xl font-bold">{totalOrders.toLocaleString()}</p>
        </div>
      </div>

      {/* Machine Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {machines.length > 0 ? (
          machines.map((machine) => {
            const status = getMachineStatus(machine.last_order_time)
            const revenueShare = totalRevenue > 0
              ? ((machine.total_revenue / totalRevenue) * 100).toFixed(1)
              : '0.0'
            return (
              <div key={machine.sticker_num} className="card-hover">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-snax-red rounded-lg flex items-center justify-center flex-shrink-0">
                      <Zap size={20} className="text-white" />
                    </div>
                    <div>
                      <h3 className="font-bold leading-tight">{machine.device_name}</h3>
                      <p className="text-xs text-gray-500 font-mono">{machine.sticker_num}</p>
                    </div>
                  </div>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium flex-shrink-0 ${status.color}`}>
                    {status.label}
                  </span>
                </div>

                <div className="space-y-3 mb-4">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400 flex items-center space-x-1">
                      <TrendingUp size={14} />
                      <span>30-Day Revenue</span>
                    </span>
                    <span className="font-bold text-green-400">{formatRevenue(machine.total_revenue)}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400 flex items-center space-x-1">
                      <ShoppingCart size={14} />
                      <span>Orders</span>
                    </span>
                    <span className="font-medium">{machine.order_count.toLocaleString()}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400 flex items-center space-x-1">
                      <Clock size={14} />
                      <span>Last Sale</span>
                    </span>
                    <span className="font-medium text-xs text-right">{formatTime(machine.last_order_time)}</span>
                  </div>
                </div>

                {/* Revenue share bar */}
                <div>
                  <div className="flex justify-between text-xs text-gray-500 mb-1">
                    <span>Revenue share</span>
                    <span>{revenueShare}%</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-1.5">
                    <div
                      className="bg-snax-red h-1.5 rounded-full transition-all duration-500"
                      style={{ width: `${revenueShare}%` }}
                    />
                  </div>
                </div>
              </div>
            )
          })
        ) : (
          <div className="col-span-full card text-center py-12">
            <Zap className="mx-auto text-gray-600 mb-4" size={48} />
            <p className="text-gray-400">No machines found in HAHA API</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default MachinesPage
