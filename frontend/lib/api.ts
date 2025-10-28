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
        if (data.refresh) {
          this.refreshToken = data.refresh
        }
        if (typeof window !== 'undefined') {
          localStorage.setItem('access_token', data.access)
          if (data.refresh) {
            localStorage.setItem('refresh_token', data.refresh)
          }
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

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
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
        // If the backend returns a structured response with success/data format
        if (data.success && data.data) {
          return { data: data.data, message: data.message }
        }
        // Otherwise return the data as-is
        return { data }
      } else {
        return {
          error: data.detail || data.message || data.errors || 'An error occurred',
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
    const response = await this.makeRequest<any>('/auth/login/', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    })

    if (response.data && (response.data as any).tokens) {
      this.saveTokensToStorage({
        access: (response.data as any).tokens.access,
        refresh: (response.data as any).tokens.refresh,
      })

      // Store user data in localStorage
      if ((response.data as any).user && typeof window !== 'undefined') {
        localStorage.setItem('agriconnect_user', JSON.stringify((response.data as any).user))
      }
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
    const registrationData = {
      email: userData.email,
      username: userData.email, // Use email as username
      password: userData.password,
      password_confirm: userData.password,
      first_name: userData.first_name,
      last_name: userData.last_name,
      role: userData.role.toLowerCase(), // Convert to lowercase
      phone_number: userData.phone || '', // Use empty string if not provided
    }

    const response = await this.makeRequest('/auth/register/', {
      method: 'POST',
      body: JSON.stringify(registrationData),
    })

    if (response.data && (response.data as any).tokens) {
      this.saveTokensToStorage({
        access: (response.data as any).tokens.access,
        refresh: (response.data as any).tokens.refresh,
      })

      // Store user data in localStorage
      if ((response.data as any).user && typeof window !== 'undefined') {
        localStorage.setItem('agriconnect_user', JSON.stringify((response.data as any).user))
      }
    }

    return response
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
    return this.makeRequest(`/orders/cart/items/${itemId}/update/`, {
      method: 'PUT',
      body: JSON.stringify({ quantity }),
    })
  }

  async removeFromCart(itemId: string): Promise<ApiResponse<any>> {
    return this.makeRequest(`/orders/cart/items/${itemId}/remove/`, {
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

  // Additional Authentication methods
  async refreshTokenManual(): Promise<ApiResponse<any>> {
    if (!this.refreshToken) {
      return { error: 'No refresh token available' }
    }

    const response = await this.makeRequest('/auth/token/refresh/', {
      method: 'POST',
      body: JSON.stringify({ refresh: this.refreshToken }),
    })

    if (response.data && typeof response.data === 'object' && 'access' in response.data) {
      this.accessToken = (response.data as any).access
      if (typeof window !== 'undefined') {
        localStorage.setItem('access_token', (response.data as any).access)
      }
    }

    return response
  }

  async changePassword(oldPassword: string, newPassword: string): Promise<ApiResponse<any>> {
    return this.makeRequest('/auth/password/change/', {
      method: 'POST',
      body: JSON.stringify({ old_password: oldPassword, new_password: newPassword }),
    })
  }

  async sendPhoneVerification(): Promise<ApiResponse<any>> {
    return this.makeRequest('/auth/phone/send-verification/', {
      method: 'POST',
    })
  }

  async verifyPhone(code: string): Promise<ApiResponse<any>> {
    return this.makeRequest('/auth/phone/verify/', {
      method: 'POST',
      body: JSON.stringify({ verification_code: code }),
    })
  }

  async sendEmailVerification(): Promise<ApiResponse<any>> {
    return this.makeRequest('/auth/email/send-verification/', {
      method: 'POST',
    })
  }

  async verifyEmail(code: string): Promise<ApiResponse<any>> {
    return this.makeRequest('/auth/email/verify/', {
      method: 'POST',
      body: JSON.stringify({ verification_code: code }),
    })
  }

  async getFarmerProfile(): Promise<ApiResponse<any>> {
    return this.makeRequest('/auth/profile/farmer/')
  }

  async updateFarmerProfile(profileData: any): Promise<ApiResponse<any>> {
    return this.makeRequest('/auth/profile/farmer/', {
      method: 'PUT',
      body: JSON.stringify(profileData),
    })
  }

  async getBuyerProfile(): Promise<ApiResponse<any>> {
    return this.makeRequest('/auth/profile/buyer/')
  }

  async updateBuyerProfile(profileData: any): Promise<ApiResponse<any>> {
    return this.makeRequest('/auth/profile/buyer/', {
      method: 'PUT',
      body: JSON.stringify(profileData),
    })
  }

  async getTransporterProfile(): Promise<ApiResponse<any>> {
    return this.makeRequest('/auth/profile/transporter/')
  }

  async updateTransporterProfile(profileData: any): Promise<ApiResponse<any>> {
    return this.makeRequest('/auth/profile/transporter/', {
      method: 'PUT',
      body: JSON.stringify(profileData),
    })
  }

  // Extended Product methods
  async getMyProducts(): Promise<ApiResponse<any>> {
    return this.makeRequest('/products/my-products/')
  }

  async updateProduct(id: string, productData: any): Promise<ApiResponse<any>> {
    return this.makeRequest(`/products/${id}/update/`, {
      method: 'PUT',
      body: JSON.stringify(productData),
    })
  }

  async deleteProduct(id: string): Promise<ApiResponse<any>> {
    return this.makeRequest(`/products/${id}/delete/`, {
      method: 'DELETE',
    })
  }

  async getProductReviews(productId: string): Promise<ApiResponse<any>> {
    return this.makeRequest(`/products/${productId}/reviews/`)
  }

  async createProductReview(productId: string, reviewData: any): Promise<ApiResponse<any>> {
    return this.makeRequest(`/products/${productId}/reviews/`, {
      method: 'POST',
      body: JSON.stringify(reviewData),
    })
  }

  async getWishlist(): Promise<ApiResponse<any>> {
    return this.makeRequest('/products/wishlist/')
  }

  async getProductAnalytics(productId: string): Promise<ApiResponse<any>> {
    return this.makeRequest(`/products/${productId}/analytics/`)
  }

  async getFeaturedProducts(): Promise<ApiResponse<any>> {
    return this.makeRequest('/products/featured/')
  }

  async getSearchSuggestions(query: string): Promise<ApiResponse<any>> {
    return this.makeRequest(`/products/search/suggestions/?q=${encodeURIComponent(query)}`)
  }

  // Extended Order methods

  async clearCart(): Promise<ApiResponse<any>> {
    return this.makeRequest('/orders/cart/clear/', {
      method: 'POST',
    })
  }

  async updateOrderStatus(orderId: string, status: string): Promise<ApiResponse<any>> {
    return this.makeRequest(`/orders/${orderId}/status/`, {
      method: 'PUT',
      body: JSON.stringify({ status }),
    })
  }

  async cancelOrder(orderId: string, reason?: string): Promise<ApiResponse<any>> {
    return this.makeRequest(`/orders/${orderId}/cancel/`, {
      method: 'POST',
      body: JSON.stringify({ reason }),
    })
  }

  async rateOrder(orderId: string, rating: number, comment?: string): Promise<ApiResponse<any>> {
    return this.makeRequest(`/orders/${orderId}/rate/`, {
      method: 'POST',
      body: JSON.stringify({ rating, comment }),
    })
  }

  async getDeliveryRequests(): Promise<ApiResponse<any>> {
    return this.makeRequest('/orders/delivery-requests/')
  }

  async acceptDeliveryRequest(deliveryId: string): Promise<ApiResponse<any>> {
    return this.makeRequest(`/orders/delivery-requests/${deliveryId}/accept/`, {
      method: 'POST',
    })
  }

  // Payment methods
  async getPayments(): Promise<ApiResponse<any>> {
    return this.makeRequest('/payments/')
  }

  async createPayment(paymentData: any): Promise<ApiResponse<any>> {
    return this.makeRequest('/payments/', {
      method: 'POST',
      body: JSON.stringify(paymentData),
    })
  }

  async getPayment(paymentId: string): Promise<ApiResponse<any>> {
    return this.makeRequest(`/payments/${paymentId}/`)
  }

  async updatePaymentStatus(paymentId: string, status: string): Promise<ApiResponse<any>> {
    return this.makeRequest(`/payments/${paymentId}/status/`, {
      method: 'PUT',
      body: JSON.stringify({ status }),
    })
  }

  async queryMpesaPayment(paymentId: string): Promise<ApiResponse<any>> {
    return this.makeRequest(`/payments/${paymentId}/mpesa/query/`)
  }

  async getPaymentRefunds(): Promise<ApiResponse<any>> {
    return this.makeRequest('/payments/refunds/')
  }

  async createPaymentRefund(refundData: any): Promise<ApiResponse<any>> {
    return this.makeRequest('/payments/refunds/', {
      method: 'POST',
      body: JSON.stringify(refundData),
    })
  }

  async releaseEscrowFunds(escrowId: string): Promise<ApiResponse<any>> {
    return this.makeRequest(`/payments/escrow/${escrowId}/release/`, {
      method: 'POST',
    })
  }

  async getPaymentAnalytics(): Promise<ApiResponse<any>> {
    return this.makeRequest('/payments/analytics/')
  }

  // Blockchain methods
  async getBlockchainNetworks(): Promise<ApiResponse<any>> {
    return this.makeRequest('/blockchain/networks/')
  }

  async getSmartContracts(): Promise<ApiResponse<any>> {
    return this.makeRequest('/blockchain/contracts/')
  }

  async createSmartContract(contractData: any): Promise<ApiResponse<any>> {
    return this.makeRequest('/blockchain/contracts/', {
      method: 'POST',
      body: JSON.stringify(contractData),
    })
  }

  async getBlockchainTransactions(): Promise<ApiResponse<any>> {
    return this.makeRequest('/blockchain/transactions/')
  }

  async createBlockchainTransaction(transactionData: any): Promise<ApiResponse<any>> {
    return this.makeRequest('/blockchain/transactions/', {
      method: 'POST',
      body: JSON.stringify(transactionData),
    })
  }

  async getProductBatches(): Promise<ApiResponse<any>> {
    return this.makeRequest('/blockchain/batches/')
  }

  async createProductBatch(batchData: any): Promise<ApiResponse<any>> {
    return this.makeRequest('/blockchain/batches/', {
      method: 'POST',
      body: JSON.stringify(batchData),
    })
  }

  async getSupplyChainEvents(): Promise<ApiResponse<any>> {
    return this.makeRequest('/blockchain/events/')
  }

  async getQualityCertificates(): Promise<ApiResponse<any>> {
    return this.makeRequest('/blockchain/certificates/')
  }

  async createQualityCertificate(certificateData: any): Promise<ApiResponse<any>> {
    return this.makeRequest('/blockchain/certificates/', {
      method: 'POST',
      body: JSON.stringify(certificateData),
    })
  }

  async getBlockchainWallets(): Promise<ApiResponse<any>> {
    return this.makeRequest('/blockchain/wallets/')
  }

  // AI Services methods
  async getPriceHistory(productId?: string): Promise<ApiResponse<any>> {
    const endpoint = productId ? `/ai/price-history/?product=${productId}` : '/ai/price-history/'
    return this.makeRequest(endpoint)
  }

  async getPricePredictions(productId: string): Promise<ApiResponse<any>> {
    return this.makeRequest(`/ai/price-predictions/?product=${productId}`)
  }

  async getDemandForecasts(productId?: string): Promise<ApiResponse<any>> {
    const endpoint = productId ? `/ai/demand-forecasts/?product=${productId}` : '/ai/demand-forecasts/'
    return this.makeRequest(endpoint)
  }

  async getProductRecommendations(): Promise<ApiResponse<any>> {
    return this.makeRequest('/ai/recommendations/')
  }

  async getMarketInsights(): Promise<ApiResponse<any>> {
    return this.makeRequest('/ai/insights/')
  }

  async trackUserInteraction(interactionData: any): Promise<ApiResponse<any>> {
    return this.makeRequest('/ai/interactions/', {
      method: 'POST',
      body: JSON.stringify(interactionData),
    })
  }

  async getAIModelMetrics(): Promise<ApiResponse<any>> {
    return this.makeRequest('/ai/model-metrics/')
  }

  async getAIAnalytics(): Promise<ApiResponse<any>> {
    return this.makeRequest('/ai/analytics/')
  }

  // Logistics methods
  async getVehicles(): Promise<ApiResponse<any>> {
    return this.makeRequest('/logistics/vehicles/')
  }

  async createVehicle(vehicleData: any): Promise<ApiResponse<any>> {
    return this.makeRequest('/logistics/vehicles/', {
      method: 'POST',
      body: JSON.stringify(vehicleData),
    })
  }

  async getTransportCompanies(): Promise<ApiResponse<any>> {
    return this.makeRequest('/logistics/companies/')
  }

  async getDeliveryRoutes(): Promise<ApiResponse<any>> {
    return this.makeRequest('/logistics/routes/')
  }

  async createDeliveryRoute(routeData: any): Promise<ApiResponse<any>> {
    return this.makeRequest('/logistics/routes/', {
      method: 'POST',
      body: JSON.stringify(routeData),
    })
  }

  async getDeliveries(): Promise<ApiResponse<any>> {
    return this.makeRequest('/logistics/deliveries/')
  }

  async createDelivery(deliveryData: any): Promise<ApiResponse<any>> {
    return this.makeRequest('/logistics/deliveries/', {
      method: 'POST',
      body: JSON.stringify(deliveryData),
    })
  }

  async getDeliveryTracking(deliveryId: string): Promise<ApiResponse<any>> {
    return this.makeRequest(`/logistics/tracking/?delivery=${deliveryId}`)
  }

  async getDeliveryZones(): Promise<ApiResponse<any>> {
    return this.makeRequest('/logistics/zones/')
  }

  async getRouteOptimization(routeData: any): Promise<ApiResponse<any>> {
    return this.makeRequest('/logistics/optimization/', {
      method: 'POST',
      body: JSON.stringify(routeData),
    })
  }

  async createDeliveryFeedback(feedbackData: any): Promise<ApiResponse<any>> {
    return this.makeRequest('/logistics/feedback/', {
      method: 'POST',
      body: JSON.stringify(feedbackData),
    })
  }

  // Notification methods
  async getNotifications(): Promise<ApiResponse<any>> {
    return this.makeRequest('/notifications/notifications/')
  }

  async markNotificationAsRead(notificationId: string): Promise<ApiResponse<any>> {
    return this.makeRequest(`/notifications/notifications/${notificationId}/`, {
      method: 'PATCH',
      body: JSON.stringify({ is_read: true }),
    })
  }

  async getNotificationSettings(): Promise<ApiResponse<any>> {
    return this.makeRequest('/notifications/settings/')
  }

  async updateNotificationSettings(settingsData: any): Promise<ApiResponse<any>> {
    return this.makeRequest('/notifications/settings/', {
      method: 'PUT',
      body: JSON.stringify(settingsData),
    })
  }

  async getNotificationTemplates(): Promise<ApiResponse<any>> {
    return this.makeRequest('/notifications/templates/')
  }

  async getSMSLogs(): Promise<ApiResponse<any>> {
    return this.makeRequest('/notifications/sms-logs/')
  }

  async getEmailLogs(): Promise<ApiResponse<any>> {
    return this.makeRequest('/notifications/email-logs/')
  }

  async getPushNotificationLogs(): Promise<ApiResponse<any>> {
    return this.makeRequest('/notifications/push-logs/')
  }

  // Check if user is authenticated
  isAuthenticated(): boolean {
    return !!this.accessToken
  }
}

export const apiClient = new ApiClient(API_BASE_URL)
export type { ApiResponse }