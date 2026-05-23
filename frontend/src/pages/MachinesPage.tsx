import React, { useEffect, useState } from 'react'
import { apiClient } from '@/services/api'
import { Machine } from '@/types'
import { Plus, Edit2, Trash2, AlertCircle, Zap } from 'lucide-react'

const MachinesPage: React.FC = () => {
  const [machines, setMachines] = useState<Machine[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [formData, setFormData] = useState({
    machine_id: '',
    location: '',
    haha_device_id: '',
    status: 'online' as const,
  })

  useEffect(() => {
    fetchMachines()
  }, [])

  const fetchMachines = async () => {
    try {
      setLoading(true)
      const response = await apiClient.getMachines()
      setMachines(response.machines || [])
      setError('')
    } catch (err: any) {
      setError('Failed to load machines')
      console.error(err)
    } finally {
      setLoading(false)
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

    if (!formData.machine_id || !formData.location) {
      setError('Please fill in all required fields')
      return
    }

    try {
      if (editingId) {
        await apiClient.updateMachine(editingId, formData)
      } else {
        await apiClient.createMachine(formData)
      }
      await fetchMachines()
      setShowForm(false)
      setEditingId(null)
      setFormData({
        machine_id: '',
        location: '',
        haha_device_id: '',
        status: 'online',
      })
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to save machine')
    }
  }

  const handleEdit = (machine: Machine) => {
    setEditingId(machine.id)
    setFormData({
      machine_id: machine.machine_id,
      location: machine.location,
      haha_device_id: machine.id.toString(),
      status: machine.status,
    })
    setShowForm(true)
  }

  const handleDelete = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this machine?')) {
      return
    }

    try {
      await apiClient.deleteMachine(id)
      await fetchMachines()
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to delete machine')
    }
  }

  const handleCancel = () => {
    setShowForm(false)
    setEditingId(null)
    setFormData({
      machine_id: '',
      location: '',
      haha_device_id: '',
      status: 'online',
    })
  }

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
          <h1 className="text-4xl font-bold mb-2">Machine Management</h1>
          <p className="text-gray-400">Manage your vending machines</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="btn-primary flex items-center space-x-2"
        >
          <Plus size={20} />
          <span>Add Machine</span>
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-4 bg-red-900 border border-red-700 rounded-lg flex items-start space-x-3">
          <AlertCircle className="text-red-400 flex-shrink-0 mt-0.5" size={20} />
          <p className="text-red-200">{error}</p>
        </div>
      )}

      {/* Form */}
      {showForm && (
        <div className="card">
          <h2 className="text-2xl font-bold mb-6">
            {editingId ? 'Edit Machine' : 'Add New Machine'}
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="label">Machine ID *</label>
                <input
                  type="text"
                  name="machine_id"
                  value={formData.machine_id}
                  onChange={handleInputChange}
                  placeholder="e.g., MX-1001"
                  className="input"
                />
              </div>
              <div>
                <label className="label">Location *</label>
                <input
                  type="text"
                  name="location"
                  value={formData.location}
                  onChange={handleInputChange}
                  placeholder="e.g., Downtown Mall"
                  className="input"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="label">HAHA Device ID</label>
                <input
                  type="text"
                  name="haha_device_id"
                  value={formData.haha_device_id}
                  onChange={handleInputChange}
                  placeholder="Optional"
                  className="input"
                />
              </div>
              <div>
                <label className="label">Status</label>
                <select
                  name="status"
                  value={formData.status}
                  onChange={handleInputChange}
                  className="input"
                >
                  <option value="online">Online</option>
                  <option value="offline">Offline</option>
                  <option value="maintenance">Maintenance</option>
                </select>
              </div>
            </div>

            <div className="flex space-x-3">
              <button type="submit" className="btn-primary">
                {editingId ? 'Update Machine' : 'Add Machine'}
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

      {/* Machines List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {machines.length > 0 ? (
          machines.map((machine) => (
            <div key={machine.id} className="card-hover">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-snax-red rounded-lg flex items-center justify-center">
                    <Zap size={20} className="text-white" />
                  </div>
                  <div>
                    <h3 className="font-bold">{machine.machine_id}</h3>
                    <p className="text-sm text-gray-400">{machine.location}</p>
                  </div>
                </div>
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

              <div className="space-y-2 mb-4 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">Inventory:</span>
                  <span className="font-medium">{machine.inventory_percentage}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Monthly Revenue:</span>
                  <span className="font-medium">${machine.monthly_revenue.toFixed(2)}</span>
                </div>
                {machine.last_restock && (
                  <div className="flex justify-between">
                    <span className="text-gray-400">Last Restock:</span>
                    <span className="font-medium">
                      {new Date(machine.last_restock).toLocaleDateString()}
                    </span>
                  </div>
                )}
              </div>

              <div className="flex space-x-2">
                <button
                  onClick={() => handleEdit(machine)}
                  className="flex-1 btn-secondary flex items-center justify-center space-x-2 text-sm"
                >
                  <Edit2 size={16} />
                  <span>Edit</span>
                </button>
                <button
                  onClick={() => handleDelete(machine.id)}
                  className="flex-1 bg-red-900 hover:bg-red-800 text-red-200 px-4 py-2 rounded-lg transition-colors flex items-center justify-center space-x-2 text-sm"
                >
                  <Trash2 size={16} />
                  <span>Delete</span>
                </button>
              </div>
            </div>
          ))
        ) : (
          <div className="col-span-full card text-center py-12">
            <Zap className="mx-auto text-gray-600 mb-4" size={48} />
            <p className="text-gray-400 mb-4">No machines found</p>
            <button
              onClick={() => setShowForm(true)}
              className="btn-primary"
            >
              Add Your First Machine
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default MachinesPage
