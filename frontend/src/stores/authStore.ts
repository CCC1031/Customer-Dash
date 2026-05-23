import { create } from 'zustand'
import { apiClient } from '@/services/api'
import type { User, Customer } from '@/types'

interface AuthState {
  user: User | null
  customer: Customer | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  
  login: (email: string, password: string) => Promise<void>
  signup: (data: any) => Promise<void>
  logout: () => Promise<void>
  getProfile: () => Promise<void>
  updateProfile: (data: any) => Promise<void>
  clearError: () => void
  setUser: (user: User | null) => void
  setCustomer: (customer: Customer | null) => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  customer: null,
  isAuthenticated: !!localStorage.getItem('access_token'),
  isLoading: false,
  error: null,

  login: async (email: string, password: string) => {
    set({ isLoading: true, error: null })
    try {
      const response = await apiClient.login({ email, password })
      apiClient.setToken(response.access_token)
      set({
        user: response.user,
        isAuthenticated: true,
        isLoading: false,
      })
    } catch (error: any) {
      set({
        error: error.response?.data?.error || 'Login failed',
        isLoading: false,
      })
      throw error
    }
  },

  signup: async (data: any) => {
    set({ isLoading: true, error: null })
    try {
      const response = await apiClient.signup(data)
      apiClient.setToken(response.access_token)
      set({
        user: response.user,
        isAuthenticated: true,
        isLoading: false,
      })
    } catch (error: any) {
      set({
        error: error.response?.data?.error || 'Signup failed',
        isLoading: false,
      })
      throw error
    }
  },

  logout: async () => {
    set({ isLoading: true, error: null })
    try {
      await apiClient.logout()
      set({
        user: null,
        customer: null,
        isAuthenticated: false,
        isLoading: false,
      })
    } catch (error: any) {
      set({
        error: error.response?.data?.error || 'Logout failed',
        isLoading: false,
      })
    }
  },

  getProfile: async () => {
    set({ isLoading: true, error: null })
    try {
      const response = await apiClient.getProfile()
      set({
        user: response.user,
        customer: response.customer,
        isLoading: false,
      })
    } catch (error: any) {
      set({
        error: error.response?.data?.error || 'Failed to fetch profile',
        isLoading: false,
      })
    }
  },

  updateProfile: async (data: any) => {
    set({ isLoading: true, error: null })
    try {
      const response = await apiClient.updateProfile(data)
      set({
        user: response.user,
        customer: response.customer,
        isLoading: false,
      })
    } catch (error: any) {
      set({
        error: error.response?.data?.error || 'Failed to update profile',
        isLoading: false,
      })
      throw error
    }
  },

  clearError: () => set({ error: null }),

  setUser: (user: User | null) => set({ user }),

  setCustomer: (customer: Customer | null) => set({ customer }),
}))
