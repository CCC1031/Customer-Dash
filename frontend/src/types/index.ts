// User and Authentication Types
export interface User {
  id: number
  email: string
  first_name: string
  last_name: string
  phone: string
  created_at: string
}

export interface Customer {
  id: number
  company_name: string
  address: string
  city: string
  state: string
  zip_code: string
  created_at: string
}

export interface AuthResponse {
  access_token: string
  user: User
  message: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface SignupRequest {
  email: string
  password: string
  first_name: string
  last_name: string
  company_name: string
  phone?: string
  address?: string
  city?: string
  state?: string
  zip_code?: string
}

// Machine Types
export interface Machine {
  id: number
  machine_id: string
  location: string
  status: 'online' | 'offline' | 'maintenance'
  inventory_percentage: number
  monthly_revenue: number
  last_restock: string | null
  created_at: string
}

// Inventory Types
export interface InventoryItem {
  id: number
  product_name: string
  sku: string
  quantity: number
  low_stock_threshold: number
  status: 'in_stock' | 'low_stock' | 'out_of_stock'
  last_updated: string
}

// Revenue Types
export interface RevenueRecord {
  id: number
  date: string
  units_sold: number
  total_revenue: number
  average_transaction: number
}

export interface DailyRevenue {
  date: string
  revenue: number
  units?: number
}

// Support Ticket Types
export interface SupportTicket {
  id: number
  ticket_number: string
  subject: string
  description: string
  status: 'open' | 'in_progress' | 'resolved' | 'closed'
  priority: 'low' | 'medium' | 'high' | 'urgent'
  created_at: string
  resolved_at: string | null
}

// Activity Types
export interface Activity {
  id: number
  activity_type: string
  description: string
  created_at: string
}

// Dashboard Types
export interface DashboardOverview {
  total_machines: number
  online_machines: number
  revenue_30_days: number
  low_stock_alerts: number
  open_tickets: number
  recent_activities: Activity[]
}

export interface RevenueSummary {
  daily_revenue: DailyRevenue[]
  total_revenue: number
}

export interface MachineStatus {
  id: number
  machine_id: string
  location: string
  status: 'online' | 'offline' | 'maintenance'
  inventory_percentage: number
  monthly_revenue: number
  last_restock: string | null
}

// API Response Types
export interface ApiResponse<T> {
  data: T
  message?: string
  error?: string
}

export interface ApiError {
  error: string
  status: number
}
