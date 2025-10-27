const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

interface ApiResponse<T> {
  data?: T
  error?: string
  message?: string
}

interface AuthTokens {
  access: string
  refresh: string
}

class ApiClient {
  private baseURL: string
  private accessToken: string | null = null
  private refreshToken: string | null = null

  constructor(baseURL: string) {
    this.baseURL = baseURL
    this.loadTokensFromStorage()
  }

  private loadTokensFromStorage() {
    if (typeof window !== 'undefined') {
      this.accessToken = localStorage.getItem('access_token')
      this.refreshToken = localStorage.getItem('refresh_token')
    }
  }

  private saveTokensToStorage(tokens: AuthTokens) {
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', tokens.access)
      localStorage.setItem('refresh_token', tokens.refresh)
      this.accessToken = tokens.access
      this.refreshToken = tokens.refresh
    }
  }

  private clearTokensFromStorage() {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('agriconnect_user')
      this.accessToken = null
      this.refreshToken = null
    }
  }

  private async refreshAccessToken(): Promise<boolean> {
    if (!this.refreshToken) return false

    try {
      const response = await fetch(`${this.baseURL}/auth/token/refresh/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh: this.refreshToken }),
      })

      if (response.ok) {
        const data = await response.json()
        this.accessToken = data.access
        if (typeof window !== 'undefined') {
          localStorage.setItem('access_token', data.access)
        }
        return true
      }
    } catch (error) {
      console.error('Token refresh failed:', error)
    }

    this.clearTokensFromStorage()
    return false
  }

  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseURL}${endpoint}`

    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    }

    if (this.accessToken) {
      headers.Authorization = `Bearer ${this.accessToken}`
    }

    try {
      let response = await fetch(url, {
        ...options,
        headers,
      })

      // If token expired, try to refresh
      if (response.status === 401 && this.refreshToken) {
        const refreshed = await this.refreshAccessToken()
        if (refreshed) {
          headers.Authorization = `Bearer ${this.accessToken}`
          response = await fetch(url, {
            ...options,
            headers,
          })
        }
      }

      const data = await response.json()

      if (response.ok) {
        return { data }
      } else {
        return {
          error: data.detail || data.message || 'An error occurred',
          data: data
        }
      }
    } catch (error) {
      console.error('API request failed:', error)
      return { error: 'Network error occurred' }
    }
  }

  // Authentication methods
  async login(email: string, password: string): Promise<ApiResponse<AuthTokens & { user: any }>> {
    const response = await this.makeRequest<AuthTokens & { user: any }>('/auth/login/', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    })

    if (response.data) {
      this.saveTokensToStorage({
        access: response.data.access,
        refresh: response.data.refresh,
      })
    }

    return response
  }

  async register(userData: {
    email: string
    password: string
    first_name: string
    last_name: string
    role: string
    phone?: string
  }): Promise<ApiResponse<any>> {
    return this.makeRequest('/auth/register/', {
      method: 'POST',
      body: JSON.stringify(userData),
    })
  }

  async getProfile(): Promise<ApiResponse<any>> {
    return this.makeRequest('/auth/profile/')
  }

  async updateProfile(profileData: any): Promise<ApiResponse<any>> {
    return this.makeRequest('/auth/profile/', {
      method: 'PUT',
      body: JSON.stringify(profileData),
    })
  }

  logout() {
    this.clearTokensFromStorage()
  }

  // Product methods
  async getProducts(params?: {
    search?: string
    category?: string
    location?: string
    min_price?: number
    max_price?: number
    page?: number
  }): Promise<ApiResponse<any>> {
    const searchParams = new URLSearchParams()
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          searchParams.append(key, value.toString())
        }
      })
    }

    const endpoint = `/products/${searchParams.toString() ? `?${searchParams.toString()}` : ''}`
    return this.makeRequest(endpoint)
  }

  async getProduct(id: string): Promise<ApiResponse<any>> {
    return this.makeRequest(`/products/${id}/`)
  }

  async createProduct(productData: any): Promise<ApiResponse<any>> {
    return this.makeRequest('/products/create/', {
      method: 'POST',
      body: JSON.stringify(productData),
    })
  }

  async getProductCategories(): Promise<ApiResponse<any>> {
    return this.makeRequest('/products/categories/')
  }

  async addToWishlist(productId: string): Promise<ApiResponse<any>> {
    return this.makeRequest(`/products/${productId}/wishlist/add/`, {
      method: 'POST',
    })
  }

  async removeFromWishlist(productId: string): Promise<ApiResponse<any>> {
    return this.makeRequest(`/products/${productId}/wishlist/remove/`, {
      method: 'DELETE',
    })
  }

  // Cart and Order methods
  async getCart(): Promise<ApiResponse<any>> {
    return this.makeRequest('/orders/cart/')
  }

  async addToCart(productId: string, quantity: number): Promise<ApiResponse<any>> {
    return this.makeRequest('/orders/cart/add/', {
      method: 'POST',
      body: JSON.stringify({ product: productId, quantity }),
    })
  }

  async updateCartItem(itemId: string, quantity: number): Promise<ApiResponse<any>> {
    return this.makeRequest(`/orders/cart/items/${itemId}/`, {
      method: 'PUT',
      body: JSON.stringify({ quantity }),
    })
  }

  async removeFromCart(itemId: string): Promise<ApiResponse<any>> {
    return this.makeRequest(`/orders/cart/items/${itemId}/`, {
      method: 'DELETE',
    })
  }

  async createOrder(): Promise<ApiResponse<any>> {
    return this.makeRequest('/orders/create/', {
      method: 'POST',
    })
  }

  async getOrders(): Promise<ApiResponse<any>> {
    return this.makeRequest('/orders/')
  }

  async getOrder(id: string): Promise<ApiResponse<any>> {
    return this.makeRequest(`/orders/${id}/`)
  }

  // Check if user is authenticated
  isAuthenticated(): boolean {
    return !!this.accessToken
  }
}

export const apiClient = new ApiClient(API_BASE_URL)
export type { ApiResponse }