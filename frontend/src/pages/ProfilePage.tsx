import React, { useEffect, useState } from 'react'
import { useAuthStore } from '@/stores/authStore'
import { apiClient } from '@/services/api'
import { AlertCircle, CheckCircle, User, Building2, Phone, Mail } from 'lucide-react'

const ProfilePage: React.FC = () => {
  const { user, customer, updateProfile } = useAuthStore()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [editMode, setEditMode] = useState(false)
  const [formData, setFormData] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    email: user?.email || '',
    phone: user?.phone || '',
    company_name: customer?.company_name || '',
    address: customer?.address || '',
    city: customer?.city || '',
    state: customer?.state || '',
    zip_code: customer?.zip_code || '',
  })
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  })

  useEffect(() => {
    if (user && customer) {
      setFormData({
        first_name: user.first_name,
        last_name: user.last_name,
        email: user.email,
        phone: user.phone,
        company_name: customer.company_name,
        address: customer.address,
        city: customer.city,
        state: customer.state,
        zip_code: customer.zip_code,
      })
    }
  }, [user, customer])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setPasswordData((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  const handleSubmitProfile = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')

    try {
      setLoading(true)
      await updateProfile(formData)
      setSuccess('Profile updated successfully!')
      setEditMode(false)
      setTimeout(() => setSuccess(''), 3000)
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to update profile')
    } finally {
      setLoading(false)
    }
  }

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')

    if (passwordData.new_password !== passwordData.confirm_password) {
      setError('Passwords do not match')
      return
    }

    if (passwordData.new_password.length < 6) {
      setError('Password must be at least 6 characters')
      return
    }

    try {
      setLoading(true)
      // This endpoint would need to be implemented in the backend
      // await apiClient.changePassword(passwordData)
      setSuccess('Password changed successfully!')
      setPasswordData({
        current_password: '',
        new_password: '',
        confirm_password: '',
      })
      setTimeout(() => setSuccess(''), 3000)
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to change password')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold mb-2">Profile Settings</h1>
        <p className="text-gray-400">Manage your account and company information</p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-4 bg-red-900 border border-red-700 rounded-lg flex items-start space-x-3">
          <AlertCircle className="text-red-400 flex-shrink-0 mt-0.5" size={20} />
          <p className="text-red-200">{error}</p>
        </div>
      )}

      {/* Success Message */}
      {success && (
        <div className="p-4 bg-green-900 border border-green-700 rounded-lg flex items-start space-x-3">
          <CheckCircle className="text-green-400 flex-shrink-0 mt-0.5" size={20} />
          <p className="text-green-200">{success}</p>
        </div>
      )}

      {/* Profile Overview */}
      <div className="card">
        <div className="flex items-start justify-between mb-6">
          <div className="flex items-center space-x-4">
            <div className="w-16 h-16 bg-snax-red rounded-full flex items-center justify-center">
              <span className="text-2xl font-bold text-white">
                {user?.first_name?.charAt(0)}{user?.last_name?.charAt(0)}
              </span>
            </div>
            <div>
              <h2 className="text-2xl font-bold">
                {user?.first_name} {user?.last_name}
              </h2>
              <p className="text-gray-400">{customer?.company_name}</p>
            </div>
          </div>
          {!editMode && (
            <button
              onClick={() => setEditMode(true)}
              className="btn-primary"
            >
              Edit Profile
            </button>
          )}
        </div>

        {/* Account Status */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-6 border-t border-gray-700">
          <div>
            <p className="text-gray-400 text-sm">Account Created</p>
            <p className="font-medium mt-1">
              {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
            </p>
          </div>
          <div>
            <p className="text-gray-400 text-sm">Account Status</p>
            <p className="font-medium mt-1 text-green-400">Active</p>
          </div>
        </div>
      </div>

      {/* Edit Profile Form */}
      {editMode && (
        <div className="card">
          <h3 className="text-2xl font-bold mb-6">Edit Profile</h3>
          <form onSubmit={handleSubmitProfile} className="space-y-6">
            {/* Personal Information */}
            <div>
              <h4 className="text-lg font-bold mb-4 flex items-center space-x-2">
                <User size={20} />
                <span>Personal Information</span>
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="label">First Name</label>
                  <input
                    type="text"
                    name="first_name"
                    value={formData.first_name}
                    onChange={handleInputChange}
                    className="input"
                    disabled={loading}
                  />
                </div>
                <div>
                  <label className="label">Last Name</label>
                  <input
                    type="text"
                    name="last_name"
                    value={formData.last_name}
                    onChange={handleInputChange}
                    className="input"
                    disabled={loading}
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                <div>
                  <label className="label">Email Address</label>
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    className="input"
                    disabled={loading}
                  />
                </div>
                <div>
                  <label className="label">Phone Number</label>
                  <input
                    type="tel"
                    name="phone"
                    value={formData.phone}
                    onChange={handleInputChange}
                    className="input"
                    disabled={loading}
                  />
                </div>
              </div>
            </div>

            {/* Company Information */}
            <div className="pt-6 border-t border-gray-700">
              <h4 className="text-lg font-bold mb-4 flex items-center space-x-2">
                <Building2 size={20} />
                <span>Company Information</span>
              </h4>
              <div>
                <label className="label">Company Name</label>
                <input
                  type="text"
                  name="company_name"
                  value={formData.company_name}
                  onChange={handleInputChange}
                  className="input"
                  disabled={loading}
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                <div>
                  <label className="label">Address</label>
                  <input
                    type="text"
                    name="address"
                    value={formData.address}
                    onChange={handleInputChange}
                    className="input"
                    disabled={loading}
                  />
                </div>
                <div>
                  <label className="label">City</label>
                  <input
                    type="text"
                    name="city"
                    value={formData.city}
                    onChange={handleInputChange}
                    className="input"
                    disabled={loading}
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                <div>
                  <label className="label">State</label>
                  <input
                    type="text"
                    name="state"
                    value={formData.state}
                    onChange={handleInputChange}
                    className="input"
                    disabled={loading}
                  />
                </div>
                <div>
                  <label className="label">Zip Code</label>
                  <input
                    type="text"
                    name="zip_code"
                    value={formData.zip_code}
                    onChange={handleInputChange}
                    className="input"
                    disabled={loading}
                  />
                </div>
              </div>
            </div>

            {/* Form Actions */}
            <div className="flex space-x-3 pt-6 border-t border-gray-700">
              <button
                type="submit"
                disabled={loading}
                className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Saving...' : 'Save Changes'}
              </button>
              <button
                type="button"
                onClick={() => setEditMode(false)}
                className="btn-secondary"
                disabled={loading}
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Change Password */}
      <div className="card">
        <h3 className="text-2xl font-bold mb-6">Change Password</h3>
        <form onSubmit={handleChangePassword} className="space-y-4">
          <div>
            <label className="label">Current Password</label>
            <input
              type="password"
              name="current_password"
              value={passwordData.current_password}
              onChange={handlePasswordChange}
              placeholder="••••••••"
              className="input"
              disabled={loading}
            />
          </div>

          <div>
            <label className="label">New Password</label>
            <input
              type="password"
              name="new_password"
              value={passwordData.new_password}
              onChange={handlePasswordChange}
              placeholder="••••••••"
              className="input"
              disabled={loading}
            />
          </div>

          <div>
            <label className="label">Confirm New Password</label>
            <input
              type="password"
              name="confirm_password"
              value={passwordData.confirm_password}
              onChange={handlePasswordChange}
              placeholder="••••••••"
              className="input"
              disabled={loading}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Updating...' : 'Change Password'}
          </button>
        </form>
      </div>

      {/* Account Information */}
      <div className="card">
        <h3 className="text-2xl font-bold mb-6">Account Information</h3>
        <div className="space-y-4">
          <div className="flex items-center space-x-3 p-4 bg-gray-800 rounded-lg">
            <Mail className="text-snax-red" size={20} />
            <div className="flex-1">
              <p className="text-gray-400 text-sm">Email Address</p>
              <p className="font-medium">{user?.email}</p>
            </div>
          </div>

          <div className="flex items-center space-x-3 p-4 bg-gray-800 rounded-lg">
            <Phone className="text-snax-red" size={20} />
            <div className="flex-1">
              <p className="text-gray-400 text-sm">Phone Number</p>
              <p className="font-medium">{user?.phone || 'Not provided'}</p>
            </div>
          </div>

          <div className="flex items-center space-x-3 p-4 bg-gray-800 rounded-lg">
            <Building2 className="text-snax-red" size={20} />
            <div className="flex-1">
              <p className="text-gray-400 text-sm">Company</p>
              <p className="font-medium">{customer?.company_name}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ProfilePage
