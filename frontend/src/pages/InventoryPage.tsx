import React, { useEffect, useState } from 'react'
import { apiClient } from '@/services/api'
import { InventoryItem, Machine } from '@/types'
import { Plus, Edit2, Trash2, AlertCircle, Package, AlertTriangle } from 'lucide-react'

const InventoryPage: React.FC = () => {
  const [inventory, setInventory] = useState<InventoryItem[]>([])
  const [machines, setMachines] = useState<Machine[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [selectedMachine, setSelectedMachine] = useState<number | null>(null)
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const [formData, setFormData] = useState({
    machine_id: '',
    product_name: '',
    sku: '',
    quantity: '',
    low_stock_threshold: '10',
  })

  useEffect(() => {
    fetchData()
  }, [])

  useEffect(() => {
    if (selectedMachine) {
      fetchMachineInventory(selectedMachine)
    } else {
      fetchAllInventory()
    }
  }, [selectedMachine])

  const fetchData = async () => {
    try {
      setLoading(true)
      const [inventoryRes, machinesRes] = await Promise.all([
        apiClient.getInventory(),
        apiClient.getMachines(),
      ])
      setInventory(inventoryRes.inventory || [])
      setMachines(machinesRes.machines || [])
      setError('')
    } catch (err: any) {
      setError('Failed to load inventory data')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const fetchAllInventory = async () => {
    try {
      const response = await apiClient.getInventory()
      setInventory(response.inventory || [])
    } catch (err: any) {
      setError('Failed to load inventory')
    }
  }

  const fetchMachineInventory = async (machineId: number) => {
    try {
      const response = await apiClient.getMachineInventory(machineId)
      setInventory(response.inventory || [])
    } catch (err: any) {
      setError('Failed to load machine inventory')
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!formData.machine_id || !formData.product_name || !formData.quantity) {
      setError('Please fill in all required fields')
      return
    }

    try {
      const data = {
        machine_id: parseInt(formData.machine_id),
        product_name: formData.product_name,
        sku: formData.sku,
        quantity: parseInt(formData.quantity),
        low_stock_threshold: parseInt(formData.low_stock_threshold),
      }

      if (editingId) {
        await apiClient.updateInventoryItem(editingId, data)
      } else {
        await apiClient.createInventoryItem(data)
      }

      if (selectedMachine) {
        await fetchMachineInventory(selectedMachine)
      } else {
        await fetchAllInventory()
      }

      setShowForm(false)
      setEditingId(null)
      setFormData({
        machine_id: '',
        product_name: '',
        sku: '',
        quantity: '',
        low_stock_threshold: '10',
      })
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to save inventory item')
    }
  }

  const handleEdit = (item: InventoryItem) => {
    setEditingId(item.id)
    setFormData({
      machine_id: item.id.toString(),
      product_name: item.product_name,
      sku: item.sku,
      quantity: item.quantity.toString(),
      low_stock_threshold: item.low_stock_threshold.toString(),
    })
    setShowForm(true)
  }

  const handleDelete = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this item?')) {
      return
    }

    try {
      await apiClient.deleteInventoryItem(id)
      if (selectedMachine) {
        await fetchMachineInventory(selectedMachine)
      } else {
        await fetchAllInventory()
      }
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to delete item')
    }
  }

  const handleCancel = () => {
    setShowForm(false)
    setEditingId(null)
    setFormData({
      machine_id: '',
      product_name: '',
      sku: '',
      quantity: '',
      low_stock_threshold: '10',
    })
  }

  const filteredInventory = inventory.filter((item) => {
    if (filterStatus === 'all') return true
    return item.status === filterStatus
  })

  const lowStockItems = inventory.filter((item) => item.status === 'low_stock' || item.status === 'out_of_stock')

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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl md:text-4xl font-bold mb-1 md:mb-2">Inventory Management</h1>
          <p className="text-gray-400">Track and manage product inventory</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="btn-primary flex items-center space-x-2 flex-shrink-0"
        >
          <Plus size={20} />
          <span className="hidden sm:inline">Add Item</span>
          <span className="sm:hidden">Add</span>
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-4 bg-red-900 border border-red-700 rounded-lg flex items-start space-x-3">
          <AlertCircle className="text-red-400 flex-shrink-0 mt-0.5" size={20} />
          <p className="text-red-200">{error}</p>
        </div>
      )}

      {/* Low Stock Alert */}
      {lowStockItems.length > 0 && (
        <div className="p-4 bg-yellow-900 border border-yellow-700 rounded-lg flex items-start space-x-3">
          <AlertTriangle className="text-yellow-400 flex-shrink-0 mt-0.5" size={20} />
          <div>
            <p className="text-yellow-200 font-medium">Low Stock Alert</p>
            <p className="text-yellow-300 text-sm">{lowStockItems.length} items need attention</p>
          </div>
        </div>
      )}

      {/* Form */}
      {showForm && (
        <div className="card">
          <h2 className="text-2xl font-bold mb-6">
            {editingId ? 'Edit Inventory Item' : 'Add New Item'}
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="label">Machine *</label>
              <select
                name="machine_id"
                value={formData.machine_id}
                onChange={handleInputChange}
                className="input"
              >
                <option value="">Select a machine</option>
                {machines.map((machine) => (
                  <option key={machine.id} value={machine.id}>
                    {machine.machine_id} - {machine.location}
                  </option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="label">Product Name *</label>
                <input
                  type="text"
                  name="product_name"
                  value={formData.product_name}
                  onChange={handleInputChange}
                  placeholder="e.g., Coca-Cola"
                  className="input"
                />
              </div>
              <div>
                <label className="label">SKU</label>
                <input
                  type="text"
                  name="sku"
                  value={formData.sku}
                  onChange={handleInputChange}
                  placeholder="e.g., COKE-001"
                  className="input"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="label">Quantity *</label>
                <input
                  type="number"
                  name="quantity"
                  value={formData.quantity}
                  onChange={handleInputChange}
                  placeholder="0"
                  className="input"
                  min="0"
                />
              </div>
              <div>
                <label className="label">Low Stock Threshold</label>
                <input
                  type="number"
                  name="low_stock_threshold"
                  value={formData.low_stock_threshold}
                  onChange={handleInputChange}
                  placeholder="10"
                  className="input"
                  min="0"
                />
              </div>
            </div>

            <div className="flex space-x-3">
              <button type="submit" className="btn-primary">
                {editingId ? 'Update Item' : 'Add Item'}
              </button>
              <button
                type="button"
                onClick={handleCancel}
                className="btn-secondary"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Filters */}
      <div className="flex flex-col md:flex-row gap-4">
        <div>
          <label className="label">Filter by Machine</label>
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
          <label className="label">Filter by Status</label>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="input"
          >
            <option value="all">All Items</option>
            <option value="in_stock">In Stock</option>
            <option value="low_stock">Low Stock</option>
            <option value="out_of_stock">Out of Stock</option>
          </select>
        </div>
      </div>

      {/* Inventory Table - Desktop */}
      <div className="card hidden md:block overflow-x-auto">
        {filteredInventory.length > 0 ? (
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-700">
                <th className="text-left py-3 px-4 text-gray-400 font-medium">Product</th>
                <th className="text-left py-3 px-4 text-gray-400 font-medium">SKU</th>
                <th className="text-left py-3 px-4 text-gray-400 font-medium">Quantity</th>
                <th className="text-left py-3 px-4 text-gray-400 font-medium">Threshold</th>
                <th className="text-left py-3 px-4 text-gray-400 font-medium">Status</th>
                <th className="text-left py-3 px-4 text-gray-400 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredInventory.map((item) => (
                <tr key={item.id} className="border-b border-gray-700 hover:bg-gray-800 transition-colors">
                  <td className="py-3 px-4 font-medium">{item.product_name}</td>
                  <td className="py-3 px-4 text-gray-400">{item.sku || '-'}</td>
                  <td className="py-3 px-4">{item.quantity}</td>
                  <td className="py-3 px-4 text-gray-400">{item.low_stock_threshold}</td>
                  <td className="py-3 px-4">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                      item.status === 'in_stock' ? 'bg-green-900 text-green-200'
                      : item.status === 'low_stock' ? 'bg-yellow-900 text-yellow-200'
                      : 'bg-red-900 text-red-200'
                    }`}>
                      {item.status.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <div className="flex space-x-2">
                      <button onClick={() => handleEdit(item)} className="text-snax-red hover:text-red-400 transition-colors"><Edit2 size={18} /></button>
                      <button onClick={() => handleDelete(item.id)} className="text-red-500 hover:text-red-400 transition-colors"><Trash2 size={18} /></button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="text-center py-12">
            <Package className="mx-auto text-gray-600 mb-4" size={48} />
            <p className="text-gray-400 mb-4">No inventory items found</p>
            <button onClick={() => setShowForm(true)} className="btn-primary">Add Your First Item</button>
          </div>
        )}
      </div>

      {/* Inventory Cards - Mobile */}
      <div className="md:hidden space-y-3">
        {filteredInventory.length > 0 ? filteredInventory.map((item) => (
          <div key={item.id} className="card p-4">
            <div className="flex items-start justify-between mb-2">
              <div className="flex-1 min-w-0">
                <p className="font-semibold truncate">{item.product_name}</p>
                <p className="text-xs text-gray-400">{item.sku || 'No SKU'}</p>
              </div>
              <span className={`ml-2 flex-shrink-0 px-2 py-0.5 rounded-full text-xs font-medium ${
                item.status === 'in_stock' ? 'bg-green-900 text-green-200'
                : item.status === 'low_stock' ? 'bg-yellow-900 text-yellow-200'
                : 'bg-red-900 text-red-200'
              }`}>
                {item.status.replace('_', ' ')}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex space-x-4 text-sm">
                <span className="text-gray-400">Qty: <span className="text-white font-medium">{item.quantity}</span></span>
                <span className="text-gray-400">Min: <span className="text-white font-medium">{item.low_stock_threshold}</span></span>
              </div>
              <div className="flex space-x-3">
                <button onClick={() => handleEdit(item)} className="text-snax-red hover:text-red-400 transition-colors p-1"><Edit2 size={16} /></button>
                <button onClick={() => handleDelete(item.id)} className="text-red-500 hover:text-red-400 transition-colors p-1"><Trash2 size={16} /></button>
              </div>
            </div>
          </div>
        )) : (
          <div className="card text-center py-12">
            <Package className="mx-auto text-gray-600 mb-4" size={48} />
            <p className="text-gray-400 mb-4">No inventory items found</p>
            <button onClick={() => setShowForm(true)} className="btn-primary">Add Your First Item</button>
          </div>
        )}
      </div>
    </div>
  )
}

export default InventoryPage
