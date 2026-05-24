import React, { useEffect, useState } from 'react'
import { apiClient } from '@/services/api'
import { SupportTicket, Machine } from '@/types'
import { Plus, Edit2, Trash2, AlertCircle, Ticket, MessageSquare } from 'lucide-react'

const SupportTicketsPage: React.FC = () => {
  const [tickets, setTickets] = useState<SupportTicket[]>([])
  const [machines, setMachines] = useState<Machine[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const [filterPriority, setFilterPriority] = useState<string>('all')
  const [formData, setFormData] = useState({
    subject: '',
    description: '',
    priority: 'medium' as const,
    machine_id: '',
  })

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      const [ticketsRes, machinesRes] = await Promise.all([
        apiClient.getSupportTickets(),
        apiClient.getMachines(),
      ])
      setTickets(ticketsRes.tickets || [])
      setMachines(machinesRes.machines || [])
      setError('')
    } catch (err: any) {
      setError('Failed to load support tickets')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!formData.subject || !formData.description) {
      setError('Please fill in all required fields')
      return
    }

    try {
      const data = {
        subject: formData.subject,
        description: formData.description,
        priority: formData.priority,
        machine_id: formData.machine_id ? parseInt(formData.machine_id) : null,
      }

      if (editingId) {
        await apiClient.updateSupportTicket(editingId, data)
      } else {
        await apiClient.createSupportTicket(data)
      }

      await fetchData()
      setShowForm(false)
      setEditingId(null)
      setFormData({
        subject: '',
        description: '',
        priority: 'medium',
        machine_id: '',
      })
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to save ticket')
    }
  }

  const handleEdit = (ticket: SupportTicket) => {
    setEditingId(ticket.id)
    setFormData({
      subject: ticket.subject,
      description: ticket.description,
      priority: ticket.priority,
      machine_id: '',
    })
    setShowForm(true)
  }

  const handleDelete = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this ticket?')) {
      return
    }

    try {
      await apiClient.deleteSupportTicket(id)
      await fetchData()
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to delete ticket')
    }
  }

  const handleStatusChange = async (ticketId: number, newStatus: string) => {
    try {
      await apiClient.updateSupportTicket(ticketId, { status: newStatus })
      await fetchData()
    } catch (err: any) {
      setError('Failed to update ticket status')
    }
  }

  const handleCancel = () => {
    setShowForm(false)
    setEditingId(null)
    setFormData({
      subject: '',
      description: '',
      priority: 'medium',
      machine_id: '',
    })
  }

  const filteredTickets = tickets.filter((ticket) => {
    const statusMatch = filterStatus === 'all' || ticket.status === filterStatus
    const priorityMatch = filterPriority === 'all' || ticket.priority === filterPriority
    return statusMatch && priorityMatch
  })

  const openTickets = tickets.filter((t) => t.status === 'open' || t.status === 'in_progress')
  const resolvedTickets = tickets.filter((t) => t.status === 'resolved' || t.status === 'closed')

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
          <h1 className="text-2xl md:text-4xl font-bold mb-1 md:mb-2">Support Tickets</h1>
          <p className="text-gray-400">Manage your support requests</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="btn-primary flex items-center space-x-2 flex-shrink-0"
        >
          <Plus size={20} />
          <span className="hidden sm:inline">New Ticket</span>
          <span className="sm:hidden">New</span>
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-4 bg-red-900 border border-red-700 rounded-lg flex items-start space-x-3">
          <AlertCircle className="text-red-400 flex-shrink-0 mt-0.5" size={20} />
          <p className="text-red-200">{error}</p>
        </div>
      )}

      {/* Statistics */}
      <div className="grid grid-cols-3 gap-3 md:gap-4">
        <div className="card-hover">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Total Tickets</p>
              <p className="text-2xl md:text-3xl font-bold mt-1 md:mt-2">{tickets.length}</p>
            </div>
            <Ticket className="text-snax-red hidden sm:block" size={36} />
          </div>
        </div>

        <div className="card-hover">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Open</p>
              <p className="text-2xl md:text-3xl font-bold mt-1 md:mt-2">{openTickets.length}</p>
            </div>
            <MessageSquare className="text-yellow-500 hidden sm:block" size={36} />
          </div>
        </div>

        <div className="card-hover">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Resolved</p>
              <p className="text-2xl md:text-3xl font-bold mt-1 md:mt-2">{resolvedTickets.length}</p>
            </div>
            <MessageSquare className="text-green-500 hidden sm:block" size={36} />
          </div>
        </div>
      </div>

      {/* Form */}
      {showForm && (
        <div className="card">
          <h2 className="text-2xl font-bold mb-6">
            {editingId ? 'Edit Ticket' : 'Create New Ticket'}
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="label">Subject *</label>
              <input
                type="text"
                name="subject"
                value={formData.subject}
                onChange={handleInputChange}
                placeholder="Brief description of the issue"
                className="input"
              />
            </div>

            <div>
              <label className="label">Description *</label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                placeholder="Detailed description of the issue"
                className="input"
                rows={5}
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="label">Priority</label>
                <select
                  name="priority"
                  value={formData.priority}
                  onChange={handleInputChange}
                  className="input"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="urgent">Urgent</option>
                </select>
              </div>

              <div>
                <label className="label">Related Machine (Optional)</label>
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
            </div>

            <div className="flex space-x-3">
              <button type="submit" className="btn-primary">
                {editingId ? 'Update Ticket' : 'Create Ticket'}
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
          <label className="label">Filter by Status</label>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="input"
          >
            <option value="all">All Statuses</option>
            <option value="open">Open</option>
            <option value="in_progress">In Progress</option>
            <option value="resolved">Resolved</option>
            <option value="closed">Closed</option>
          </select>
        </div>
        <div>
          <label className="label">Filter by Priority</label>
          <select
            value={filterPriority}
            onChange={(e) => setFilterPriority(e.target.value)}
            className="input"
          >
            <option value="all">All Priorities</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="urgent">Urgent</option>
          </select>
        </div>
      </div>

      {/* Tickets List */}
      <div className="space-y-4">
        {filteredTickets.length > 0 ? (
          filteredTickets.map((ticket) => (
            <div key={ticket.id} className="card-hover">
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1 min-w-0">
                  <div className="flex flex-wrap items-center gap-2 mb-2">
                    <h3 className="text-base md:text-lg font-bold truncate">{ticket.subject}</h3>
                    <span
                      className={`px-3 py-1 rounded-full text-sm font-medium ${
                        ticket.priority === 'urgent'
                          ? 'bg-red-900 text-red-200'
                          : ticket.priority === 'high'
                          ? 'bg-orange-900 text-orange-200'
                          : ticket.priority === 'medium'
                          ? 'bg-yellow-900 text-yellow-200'
                          : 'bg-blue-900 text-blue-200'
                      }`}
                    >
                      {ticket.priority}
                    </span>
                  </div>
                  <p className="text-gray-400 text-sm mb-3">{ticket.description}</p>
                  <p className="text-xs text-gray-500">
                    Ticket #{ticket.ticket_number} • Created {new Date(ticket.created_at).toLocaleDateString()}
                  </p>
                </div>

                <div className="flex items-center space-x-2 ml-2 flex-shrink-0">
                  <select
                    value={ticket.status}
                    onChange={(e) => handleStatusChange(ticket.id, e.target.value)}
                    className={`px-3 py-1 rounded-full text-sm font-medium border-none cursor-pointer ${
                      ticket.status === 'open'
                        ? 'bg-blue-900 text-blue-200'
                        : ticket.status === 'in_progress'
                        ? 'bg-yellow-900 text-yellow-200'
                        : ticket.status === 'resolved'
                        ? 'bg-green-900 text-green-200'
                        : 'bg-gray-700 text-gray-200'
                    }`}
                  >
                    <option value="open">Open</option>
                    <option value="in_progress">In Progress</option>
                    <option value="resolved">Resolved</option>
                    <option value="closed">Closed</option>
                  </select>
                </div>
              </div>

              <div className="flex space-x-2 pt-4 border-t border-gray-700">
                <button
                  onClick={() => handleEdit(ticket)}
                  className="text-snax-red hover:text-red-400 transition-colors flex items-center space-x-1"
                >
                  <Edit2 size={18} />
                  <span className="text-sm">Edit</span>
                </button>
                <button
                  onClick={() => handleDelete(ticket.id)}
                  className="text-red-500 hover:text-red-400 transition-colors flex items-center space-x-1"
                >
                  <Trash2 size={18} />
                  <span className="text-sm">Delete</span>
                </button>
              </div>
            </div>
          ))
        ) : (
          <div className="card text-center py-12">
            <Ticket className="mx-auto text-gray-600 mb-4" size={48} />
            <p className="text-gray-400 mb-4">No tickets found</p>
            <button
              onClick={() => setShowForm(true)}
              className="btn-primary"
            >
              Create Your First Ticket
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default SupportTicketsPage
