"use client"

import { useState, useEffect } from "react"
import { ProtectedRoute } from "@/components/protected-route"
import { DashboardLayout } from "@/components/dashboard-layout"
import { useAuth } from "@/lib/auth-context"
import {
  Plus,
  Edit,
  Trash2,
  Eye,
  Star,
  MapPin,
  Package,
  DollarSign,
  TrendingUp,
  Search,
  Filter,
  MoreVertical
} from "lucide-react"
import Link from "next/link"
import { apiClient } from "@/lib/api"

interface Product {
  id: string
  name: string
  description: string
  price?: string // legacy field
  price_per_unit?: string // backend field
  quantity_available: string
  category?: {
    name: string
  }
  images?: Array<{ image: string }>
  primary_image?: string
  location?: string
  county?: string // backend field
  created_at: string
  view_count?: number
  average_rating?: number
  reviews_count?: number
  is_active?: boolean
  is_available?: boolean // backend field
}

function MyProductsContent() {
  const { user } = useAuth()
  const [products, setProducts] = useState<Product[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState("")
  const [searchTerm, setSearchTerm] = useState("")
  const [filterStatus, setFilterStatus] = useState("all")

  useEffect(() => {
    fetchMyProducts()
  }, [])

  const fetchMyProducts = async () => {
    try {
      const response = await apiClient.getMyProducts()

      if (response.data) {
        const productData = response.data.results || response.data
        setProducts(Array.isArray(productData) ? productData : [])
        setError("") // Clear any previous errors
      } else {
        setError(response.error || "No products found")
      }
    } catch (error) {
      console.error("Failed to fetch products:", error)
      setError("Failed to connect to backend. Please make sure the backend server is running.")
    } finally {
      setIsLoading(false)
    }
  }

  const filteredProducts = products.filter(product => {
    const matchesSearch = (product.name || "").toLowerCase().includes(searchTerm.toLowerCase())
    const isActive = product.is_active ?? product.is_available ?? true
    const matchesFilter = filterStatus === "all" ||
      (filterStatus === "active" && isActive) ||
      (filterStatus === "inactive" && !isActive)
    return matchesSearch && matchesFilter
  })

  const totalRevenue = products.reduce((sum, product) => {
    const price = parseFloat(product.price_per_unit || product.price || "0")
    const quantity = parseInt(product.quantity_available || "0")
    return sum + (price * quantity)
  }, 0)

  const activeProducts = products.filter(p => p.is_active).length
  const totalViews = products.reduce((sum, product) => sum + (product.view_count || 0), 0)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-green-900 mb-2">My Products</h1>
          <p className="text-green-600">Manage your product listings and track performance</p>
        </div>
        <div className="flex gap-3 mt-4 lg:mt-0">
          <button
            onClick={fetchMyProducts}
            disabled={isLoading}
            className="inline-flex items-center gap-2 border-2 border-green-600 text-green-600 hover:bg-green-50 disabled:opacity-50 font-semibold px-4 py-2 rounded-xl transition-colors"
          >
            {isLoading ? "Loading..." : "Refresh"}
          </button>
          <Link
            href="/dashboard/create-listing"
            className="inline-flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white font-semibold px-6 py-3 rounded-xl transition-colors"
          >
            <Plus size={20} />
            Add New Product
          </Link>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl p-6 shadow-sm border border-green-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-green-600 mb-1">Total Products</p>
              <p className="text-3xl font-bold text-green-900">{products.length}</p>
            </div>
            <Package className="text-green-600" size={24} />
          </div>
          <p className="text-xs text-gray-600 mt-2">{activeProducts} active</p>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm border border-green-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-green-600 mb-1">Potential Revenue</p>
              <p className="text-2xl font-bold text-green-900">KES {totalRevenue.toLocaleString()}</p>
            </div>
            <DollarSign className="text-green-600" size={24} />
          </div>
          <p className="text-xs text-gray-600 mt-2">From current inventory</p>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm border border-green-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-green-600 mb-1">Total Views</p>
              <p className="text-3xl font-bold text-green-900">{totalViews.toLocaleString()}</p>
            </div>
            <Eye className="text-green-600" size={24} />
          </div>
          <p className="text-xs text-gray-600 mt-2">Across all products</p>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm border border-green-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-green-600 mb-1">Performance</p>
              <p className="text-lg font-bold text-green-600">Good</p>
            </div>
            <TrendingUp className="text-green-600" size={24} />
          </div>
          <p className="text-xs text-gray-600 mt-2">Above average</p>
        </div>
      </div>

      {/* Search and Filter */}
      <div className="bg-white rounded-xl p-6 shadow-sm border border-green-100">
        <div className="flex flex-col lg:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Search your products..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-12 pr-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
            />
          </div>
          <div className="flex items-center gap-3">
            <Filter size={16} className="text-gray-600" />
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 bg-white"
            >
              <option value="all">All Products</option>
              <option value="active">Active Only</option>
              <option value="inactive">Inactive Only</option>
            </select>
          </div>
        </div>
      </div>

      {/* Products List */}
      <div className="bg-white rounded-xl shadow-sm border border-green-100">
        {error && (
          <div className="p-6 border-b border-green-100">
            <div className="bg-red-50 border-l-4 border-red-500 text-red-700 px-4 py-3 rounded">
              <div className="flex justify-between items-start">
                <div>
                  <h4 className="font-semibold mb-1">Unable to load products</h4>
                  <p className="text-sm">{error}</p>
                  <p className="text-sm mt-2">Try clicking the Refresh button or check if the backend server is running on port 8000.</p>
                </div>
                <button
                  onClick={fetchMyProducts}
                  className="text-red-600 hover:text-red-800 text-sm underline"
                >
                  Retry
                </button>
              </div>
            </div>
          </div>
        )}

        <div className="p-6">
          {isLoading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Loading your products...</p>
            </div>
          ) : filteredProducts.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredProducts.map((product) => (
                <div key={product.id} className="border border-gray-200 rounded-xl overflow-hidden hover:shadow-md transition-shadow">
                  {/* Product Image */}
                  <div className="relative h-48 bg-gray-100 overflow-hidden">
                    <img
                      src={product.primary_image || "/placeholder.svg"}
                      alt={product.name}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        e.currentTarget.src = "/placeholder.svg"
                      }}
                    />
                    <div className="absolute top-3 right-3">
                      <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                        (product.is_active ?? product.is_available ?? true)
                          ? "bg-green-100 text-green-800"
                          : "bg-gray-100 text-gray-800"
                      }`}>
                        {(product.is_active ?? product.is_available ?? true) ? "Active" : "Inactive"}
                      </span>
                    </div>
                  </div>

                  {/* Product Info */}
                  <div className="p-4">
                    <div className="flex justify-between items-start mb-2">
                      <h3 className="font-bold text-gray-900 truncate flex-1">{product.name}</h3>
                      <div className="relative">
                        <button className="p-1 hover:bg-gray-100 rounded">
                          <MoreVertical size={16} className="text-gray-600" />
                        </button>
                      </div>
                    </div>

                    <p className="text-sm text-gray-600 mb-3 line-clamp-2">{product.description}</p>

                    {/* Category & Location */}
                    <div className="flex items-center gap-4 text-sm text-gray-500 mb-3">
                      {product.category && (
                        <span className="bg-gray-100 px-2 py-1 rounded text-xs">
                          {product.category.name}
                        </span>
                      )}
                      {product.location && (
                        <div className="flex items-center gap-1">
                          <MapPin size={12} />
                          <span className="truncate">{product.location}</span>
                        </div>
                      )}
                    </div>

                    {/* Rating & Views */}
                    {(product.average_rating || product.view_count) && (
                      <div className="flex items-center gap-4 text-sm text-gray-500 mb-3">
                        {product.average_rating && (
                          <div className="flex items-center gap-1">
                            <Star size={12} className="fill-yellow-400 text-yellow-400" />
                            <span>{product.average_rating.toFixed(1)}</span>
                            <span>({product.reviews_count || 0})</span>
                          </div>
                        )}
                        {product.view_count && (
                          <div className="flex items-center gap-1">
                            <Eye size={12} />
                            <span>{product.view_count} views</span>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Price & Quantity */}
                    <div className="flex justify-between items-center mb-4">
                      <div>
                        <p className="text-xs text-gray-500">Price</p>
                        <p className="font-bold text-green-600">KES {parseFloat(product.price_per_unit || product.price || "0").toLocaleString()}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-xs text-gray-500">Available</p>
                        <p className="font-bold text-gray-900">{product.quantity_available}</p>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex gap-2">
                      <Link
                        href={`/product/${product.id}`}
                        className="flex-1 flex items-center justify-center gap-2 bg-gray-100 hover:bg-gray-200 text-gray-700 py-2 px-3 rounded-lg text-sm font-medium transition-colors"
                      >
                        <Eye size={16} />
                        View
                      </Link>
                      <Link
                        href={`/dashboard/products/${product.id}/edit`}
                        className="flex-1 flex items-center justify-center gap-2 bg-green-600 hover:bg-green-700 text-white py-2 px-3 rounded-lg text-sm font-medium transition-colors"
                      >
                        <Edit size={16} />
                        Edit
                      </Link>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <Package size={48} className="text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No products found</h3>
              <p className="text-gray-600 mb-6">
                {searchTerm || filterStatus !== "all"
                  ? "Try adjusting your search or filter criteria."
                  : "Start by adding your first product to the marketplace."
                }
              </p>
              {!searchTerm && filterStatus === "all" && (
                <Link
                  href="/dashboard/create-listing"
                  className="inline-flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white font-medium px-6 py-3 rounded-lg transition-colors"
                >
                  <Plus size={20} />
                  Add Your First Product
                </Link>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default function MyProductsPage() {
  return (
    <ProtectedRoute>
      <DashboardLayout>
        <MyProductsContent />
      </DashboardLayout>
    </ProtectedRoute>
  )
}