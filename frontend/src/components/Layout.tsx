import React, { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { Menu, X, LogOut, User, BarChart3, Package, Ticket, Zap, DollarSign } from 'lucide-react'

interface LayoutProps {
  children: React.ReactNode
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  const isActive = (path: string) => location.pathname === path

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: BarChart3 },
    { path: '/machines', label: 'Machines', icon: Zap },
    { path: '/inventory', label: 'Inventory', icon: Package },
    { path: '/revenue', label: 'Revenue', icon: DollarSign },
    { path: '/support', label: 'Support', icon: Ticket },
  ]

  return (
    <div className="flex h-screen bg-snax-dark text-white">
      {/* Desktop Sidebar */}
      <div
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-gray-900 shadow-lg transform transition-transform duration-300 ease-in-out ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        } md:relative md:translate-x-0 md:flex md:flex-col`}
      >
        {/* Header */}
        <div className="flex items-center justify-between h-16 px-6 border-b border-gray-700 flex-shrink-0">
          <Link to="/" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-snax-red rounded-lg flex items-center justify-center font-bold text-sm">
              S
            </div>
            <span className="font-bold text-lg">Snaxology</span>
          </Link>
          <button
            onClick={() => setSidebarOpen(false)}
            className="md:hidden text-gray-400 hover:text-white p-1"
            aria-label="Close menu"
          >
            <X size={20} />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon
            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setSidebarOpen(false)}
                className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                  isActive(item.path)
                    ? 'bg-snax-red text-white'
                    : 'text-gray-400 hover:text-white hover:bg-gray-800'
                }`}
              >
                <Icon size={20} />
                <span>{item.label}</span>
              </Link>
            )
          })}
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-gray-700 space-y-1 flex-shrink-0">
          <Link
            to="/profile"
            onClick={() => setSidebarOpen(false)}
            className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
              isActive('/profile')
                ? 'bg-snax-red text-white'
                : 'text-gray-400 hover:text-white hover:bg-gray-800'
            }`}
          >
            <User size={20} />
            <span>Profile</span>
          </Link>
          <button
            onClick={handleLogout}
            className="w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800 transition-colors"
          >
            <LogOut size={20} />
            <span>Logout</span>
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden min-w-0">
        {/* Top Bar */}
        <header className="h-16 bg-gray-900 border-b border-gray-700 flex items-center justify-between px-4 md:px-6 flex-shrink-0">
          <button
            onClick={() => setSidebarOpen(true)}
            className="md:hidden text-gray-400 hover:text-white p-1 -ml-1"
            aria-label="Open menu"
          >
            <Menu size={24} />
          </button>
          {/* Page title on mobile */}
          <div className="md:hidden flex-1 ml-3">
            <span className="font-semibold text-sm">
              {navItems.find(n => isActive(n.path))?.label || 'Snaxology'}
            </span>
          </div>
          <div className="hidden md:block flex-1" />
          <div className="flex items-center space-x-3">
            <div className="text-right hidden sm:block">
              <p className="text-sm font-medium leading-tight">{user?.first_name} {user?.last_name}</p>
              <p className="text-xs text-gray-400 leading-tight">{user?.email}</p>
            </div>
            <div className="w-9 h-9 bg-snax-red rounded-full flex items-center justify-center font-bold text-sm flex-shrink-0">
              {user?.first_name?.charAt(0)}{user?.last_name?.charAt(0)}
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-auto bg-snax-dark pb-16 md:pb-0">
          <div className="p-4 md:p-6">
            {children}
          </div>
        </main>
      </div>

      {/* Mobile Bottom Navigation */}
      <nav className="fixed bottom-0 left-0 right-0 z-40 bg-gray-900 border-t border-gray-700 md:hidden">
        <div className="flex items-center justify-around h-16">
          {navItems.map((item) => {
            const Icon = item.icon
            const active = isActive(item.path)
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex flex-col items-center justify-center flex-1 h-full space-y-1 transition-colors ${
                  active ? 'text-snax-red' : 'text-gray-500 hover:text-gray-300'
                }`}
              >
                <Icon size={20} />
                <span className="text-xs font-medium">{item.label}</span>
              </Link>
            )
          })}
        </div>
      </nav>

      {/* Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  )
}

export default Layout
