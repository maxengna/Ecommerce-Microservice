import axios from 'axios'
import { Product, ProductSearchParams, Category } from '@/types/product'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add request interceptor to include auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Add response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Product API
export const productService = {
  getProducts: async (params?: ProductSearchParams): Promise<Product[]> => {
    const response = await api.get('/products', { params })
    return response.data
  },

  getProduct: async (id: number): Promise<Product> => {
    const response = await api.get(`/products/${id}`)
    return response.data
  },

  createProduct: async (product: Partial<Product>): Promise<Product> => {
    const response = await api.post('/products', product)
    return response.data
  },

  updateProduct: async (id: number, product: Partial<Product>): Promise<Product> => {
    const response = await api.put(`/products/${id}`, product)
    return response.data
  },

  deleteProduct: async (id: number): Promise<void> => {
    await api.delete(`/products/${id}`)
  },
}

// Category API
export const categoryService = {
  getCategories: async (): Promise<Category[]> => {
    const response = await api.get('/categories')
    return response.data
  },

  getCategory: async (id: number): Promise<Category> => {
    const response = await api.get(`/categories/${id}`)
    return response.data
  },

  createCategory: async (category: Partial<Category>): Promise<Category> => {
    const response = await api.post('/categories', category)
    return response.data
  },
}

// User API
export const userService = {
  login: async (email: string, password: string) => {
    const response = await api.post('/login', { email, password })
    return response.data
  },

  register: async (userData: any) => {
    const response = await api.post('/register', userData)
    return response.data
  },

  getCurrentUser: async () => {
    const response = await api.get('/me')
    return response.data
  },

  updateProfile: async (profileData: any) => {
    const response = await api.put('/me', profileData)
    return response.data
  },

  logout: async () => {
    await api.post('/logout')
  },
}

// Order API
export const orderService = {
  getOrders: async (userId?: number) => {
    const url = userId ? `/users/${userId}/orders` : '/orders'
    const response = await api.get(url)
    return response.data
  },

  getOrder: async (id: number) => {
    const response = await api.get(`/orders/${id}`)
    return response.data
  },

  createOrder: async (orderData: any) => {
    const response = await api.post('/orders', orderData)
    return response.data
  },

  createPayment: async (orderId: number, paymentMethod: string, paymentToken?: string) => {
    const response = await api.post(`/orders/${orderId}/payments`, {
      payment_method: paymentMethod,
      payment_token: paymentToken,
    })
    return response.data
  },
}

// Cart API
export const cartService = {
  getCart: async (userId: number) => {
    const response = await api.get(`/cart/${userId}`)
    return response.data
  },

  addToCart: async (userId: number, productId: number, quantity: number) => {
    const response = await api.post(`/cart/${userId}/items`, {
      product_id: productId,
      quantity,
    })
    return response.data
  },

  updateCartItem: async (userId: number, itemId: number, quantity: number) => {
    const response = await api.put(`/cart/${userId}/items/${itemId}`, {
      quantity,
    })
    return response.data
  },

  removeFromCart: async (userId: number, itemId: number) => {
    await api.delete(`/cart/${userId}/items/${itemId}`)
  },

  clearCart: async (userId: number) => {
    await api.delete(`/cart/${userId}`)
  },
}

export default api
