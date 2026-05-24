import axios, { AxiosInstance, AxiosError } from 'axios'
import type { AuthResponse, LoginRequest, SignupRequest } from '@/types'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

class ApiClient {
  private client: AxiosInstance
  private token: string | null = null

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Load token from localStorage
    this.token = localStorage.getItem('access_token')

    // Add token to requests
    this.client.interceptors.request.use((config) => {
      if (this.token) {
        config.headers.Authorization = `Bearer ${this.token}`
      }
      return config
    })

    // Handle response errors
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          this.clearToken()
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }
    )
  }

  setToken(token: string) {
    this.token = token
    localStorage.setItem('access_token', token)
  }

  clearToken() {
    this.token = null
    localStorage.removeItem('access_token')
  }

  getToken() {
    return this.token
  }

  // Auth endpoints
  async signup(data: SignupRequest): Promise<AuthResponse> {
    const response = await this.client.post('/auth/signup', data)
    return response.data
  }

  async login(data: LoginRequest): Promise<AuthResponse> {
    const response = await this.client.post('/auth/login', data)
    return response.data
  }

  async getProfile() {
    const response = await this.client.get('/auth/profile')
    return response.data
  }

  async updateProfile(data: any) {
    const response = await this.client.put('/auth/profile', data)
    return response.data
  }

  async logout() {
    const response = await this.client.post('/auth/logout')
    this.clearToken()
    return response.data
  }

  // Dashboard endpoints
  async getDashboardOverview() {
    const response = await this.client.get('/dashboard/overview')
    return response.data
  }

  async getRevenueSummary() {
    const response = await this.client.get('/dashboard/revenue-summary')
    return response.data
  }

  async getMachineStatus() {
    const response = await this.client.get('/dashboard/machine-status')
    return response.data
  }

  // Machine endpoints
  async getMachines() {
    const response = await this.client.get('/machines')
    return response.data
  }

  async getHahaMachines() {
    const response = await this.client.get('/haha/machines')
    return response.data
  }

  async getMachine(id: number) {
    const response = await this.client.get(`/machines/${id}`)
    return response.data
  }

  async createMachine(data: any) {
    const response = await this.client.post('/machines', data)
    return response.data
  }

  async updateMachine(id: number, data: any) {
    const response = await this.client.put(`/machines/${id}`, data)
    return response.data
  }

  async deleteMachine(id: number) {
    const response = await this.client.delete(`/machines/${id}`)
    return response.data
  }

  // Inventory endpoints
  async getInventory() {
    const response = await this.client.get('/inventory')
    return response.data
  }

  async getMachineInventory(machineId: number) {
    const response = await this.client.get(`/inventory/machine/${machineId}`)
    return response.data
  }

  async getInventoryItem(id: number) {
    const response = await this.client.get(`/inventory/${id}`)
    return response.data
  }

  async createInventoryItem(data: any) {
    const response = await this.client.post('/inventory', data)
    return response.data
  }

  async updateInventoryItem(id: number, data: any) {
    const response = await this.client.put(`/inventory/${id}`, data)
    return response.data
  }

  async deleteInventoryItem(id: number) {
    const response = await this.client.delete(`/inventory/${id}`)
    return response.data
  }

  async getLowStockItems() {
    const response = await this.client.get('/inventory/low-stock')
    return response.data
  }

  // Revenue endpoints
  async getRevenue() {
    const response = await this.client.get('/revenue')
    return response.data
  }

  async getMachineRevenue(machineId: number) {
    const response = await this.client.get(`/revenue/machine/${machineId}`)
    return response.data
  }

  async createRevenueRecord(data: any) {
    const response = await this.client.post('/revenue', data)
    return response.data
  }

  async getRevenueSummaryByMachine() {
    const response = await this.client.get('/revenue/summary')
    return response.data
  }

  // Support endpoints
  async getSupportTickets() {
    const response = await this.client.get('/support')
    return response.data
  }

  async getSupportTicket(id: number) {
    const response = await this.client.get(`/support/${id}`)
    return response.data
  }

  async createSupportTicket(data: any) {
    const response = await this.client.post('/support', data)
    return response.data
  }

  async updateSupportTicket(id: number, data: any) {
    const response = await this.client.put(`/support/${id}`, data)
    return response.data
  }

  async deleteSupportTicket(id: number) {
    const response = await this.client.delete(`/support/${id}`)
    return response.data
  }

  async getTicketsByStatus(status: string) {
    const response = await this.client.get(`/support/status/${status}`)
    return response.data
  }

  async getTicketsByPriority(priority: string) {
    const response = await this.client.get(`/support/priority/${priority}`)
    return response.data
  }
}

export const apiClient = new ApiClient()
