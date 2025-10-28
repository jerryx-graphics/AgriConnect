"use client"

import { useState, useEffect } from "react"
import { ProtectedRoute } from "@/components/protected-route"
import { DashboardLayout } from "@/components/dashboard-layout"
import { Search, MapPin, Star, Loader2, Filter, Grid, List } from "lucide-react"
import Link from "next/link"
import { apiClient } from "@/lib/api"

interface Product {
  id: string
  name: string
  farmer_name?: string // Backend field
  farmer?: {
    first_name: string
    last_name: string
  }
  price?: string // legacy
  price_per_unit?: string // backend field
  images?: Array<{ image: string }>
  primary_image?: string // backend field
  average_rating?: number
  review_count?: number // backend field
  reviews_count?: number
  location?: string
  county?: string // backend field
  quantity_available?: string
  verified?: boolean
  category?: {
    name: string
  }
  category_name?: string // backend field
  description?: string
}

interface Category {
  id: string
  name: string
}

function DashboardMarketplaceContent() {
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedCategory, setSelectedCategory] = useState("All")
  const [sortBy, setSortBy] = useState("trending")
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid")
  const [products, setProducts] = useState<Product[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState("")

  // Fetch categories
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await apiClient.getProductCategories()
        if (response.data && Array.isArray(response.data)) {
          setCategories(response.data)
        } else {
          setCategories([])
        }
      } catch (error) {
        console.error("Failed to fetch categories:", error)
        setCategories([])
      }
    }
    fetchCategories()
  }, [])

  // Fetch products
  useEffect(() => {
    const fetchProducts = async () => {
      setIsLoading(true)
      setError("")

      try {
        const params: any = {}
        if (searchTerm) params.search = searchTerm
        if (selectedCategory !== "All" && Array.isArray(categories)) {
          const category = categories.find(c => c.name === selectedCategory)
          if (category) params.category = category.id
        }

        const response = await apiClient.getProducts(params)
        if (response.data) {
          const productData = response.data.results || response.data
          setProducts(Array.isArray(productData) ? productData : [])
        } else {
          setError(response.error || "Failed to fetch products")
        }
      } catch (error) {
        console.error("Failed to fetch products:", error)
        setError("Failed to fetch products")
      } finally {
        setIsLoading(false)
      }
    }

    fetchProducts()
  }, [searchTerm, selectedCategory, categories])

  const sortedProducts = Array.isArray(products) ? [...products].sort((a, b) => {
    if (sortBy === "price-low") return parseFloat(a.price) - parseFloat(b.price)
    if (sortBy === "price-high") return parseFloat(b.price) - parseFloat(a.price)
    if (sortBy === "rating") return (b.average_rating || 0) - (a.average_rating || 0)
    return 0
  }) : []

  const categoryOptions = ["All", ...(Array.isArray(categories) ? categories.map(c => c.name) : [])]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-green-900 mb-2">Marketplace</h1>
          <p className="text-green-600">Discover fresh products from local farmers</p>
        </div>
        <div className="flex items-center gap-3 mt-4 lg:mt-0">
          <div className="flex items-center bg-green-50 rounded-lg p-1">
            <button
              onClick={() => setViewMode("grid")}
              className={`p-2 rounded-md transition-colors ${
                viewMode === "grid" ? "bg-white shadow-sm text-green-600" : "text-green-500"
              }`}
            >
              <Grid size={18} />
            </button>
            <button
              onClick={() => setViewMode("list")}
              className={`p-2 rounded-md transition-colors ${
                viewMode === "list" ? "bg-white shadow-sm text-green-600" : "text-green-500"
              }`}
            >
              <List size={18} />
            </button>
          </div>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-white rounded-xl p-6 shadow-sm border border-green-100">
        {/* Search Bar */}
        <div className="relative mb-6">
          <Search
            className="absolute left-4 top-1/2 transform -translate-y-1/2 text-green-500"
            size={20}
          />
          <input
            type="text"
            placeholder="Search for fresh produce, grains, vegetables..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-12 pr-4 py-3 border-2 border-green-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
          />
        </div>

        {/* Category and Sort */}
        <div className="flex flex-col lg:flex-row gap-4 items-start lg:items-center justify-between">
          {/* Categories */}
          <div className="flex flex-wrap gap-2 overflow-x-auto">
            {categoryOptions.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-4 py-2 rounded-lg font-medium whitespace-nowrap transition-colors ${
                  selectedCategory === cat
                    ? "bg-green-600 text-white"
                    : "bg-green-50 text-green-700 hover:bg-green-100"
                }`}
              >
                {cat}
              </button>
            ))}
          </div>

          {/* Sort */}
          <div className="flex items-center gap-3">
            <Filter size={16} className="text-green-600" />
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-3 py-2 border border-green-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 bg-white text-gray-700"
            >
              <option value="trending">Trending</option>
              <option value="price-low">Price: Low to High</option>
              <option value="price-high">Price: High to Low</option>
              <option value="rating">Highest Rated</option>
            </select>
          </div>
        </div>
      </div>

      {/* Products */}
      <div className="bg-white rounded-xl shadow-sm border border-green-100">
        {error && (
          <div className="p-6 border-b border-green-100">
            <div className="bg-red-50 border-l-4 border-red-500 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          </div>
        )}

        <div className="p-6">
          {isLoading ? (
            <div className="flex flex-col justify-center items-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-green-500 mb-4" />
              <span className="text-green-600">Loading products...</span>
            </div>
          ) : sortedProducts.length > 0 ? (
            <div className={
              viewMode === "grid"
                ? "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4"
                : "space-y-4"
            }>
              {sortedProducts.map((product) => (
                <Link key={product.id} href={`/product/${product.id}`}>
                  {viewMode === "grid" ? (
                    <div className="bg-gray-50 rounded-xl overflow-hidden hover:shadow-md transition-shadow cursor-pointer border border-gray-100">
                      {/* Image */}
                      <div className="relative h-40 bg-gray-100 overflow-hidden">
                        <img
                          src={product.primary_image || "/placeholder.svg"}
                          alt={product.name}
                          className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
                        />
                        {product.verified && (
                          <div className="absolute top-2 right-2 bg-green-600 text-white px-2 py-1 rounded-full text-xs font-bold">
                            ✓ Verified
                          </div>
                        )}
                      </div>

                      {/* Content */}
                      <div className="p-4">
                        <h3 className="font-bold text-gray-900 mb-1 truncate">{product.name}</h3>
                        <p className="text-sm text-gray-600 mb-2">
                          by {product.farmer_name || 'Unknown Farmer'}
                        </p>

                        {/* Location */}
                        {product.location && (
                          <div className="flex items-center gap-1 text-xs text-gray-500 mb-2">
                            <MapPin size={12} className="text-green-500" />
                            {product.location}
                          </div>
                        )}

                        {/* Rating */}
                        {product.average_rating && (
                          <div className="flex items-center gap-1 mb-3">
                            <Star size={14} className="fill-yellow-400 text-yellow-400" />
                            <span className="text-sm font-medium text-gray-900">{product.average_rating.toFixed(1)}</span>
                            <span className="text-xs text-gray-500">({product.reviews_count || 0})</span>
                          </div>
                        )}

                        {/* Price */}
                        <div className="flex justify-between items-center">
                          <span className="text-xs text-gray-500">{product.quantity_available || 'Available'}</span>
                          <span className="font-bold text-green-600">KES {parseFloat(product.price_per_unit || product.price || "0").toLocaleString()}</span>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="flex items-center gap-4 p-4 bg-gray-50 rounded-xl hover:shadow-md transition-shadow cursor-pointer border border-gray-100">
                      {/* Image */}
                      <div className="relative w-20 h-20 bg-gray-100 rounded-lg overflow-hidden flex-shrink-0">
                        <img
                          src={product.images?.[0]?.image || "/placeholder.svg"}
                          alt={product.name}
                          className="w-full h-full object-cover"
                        />
                        {product.verified && (
                          <div className="absolute top-1 right-1 bg-green-600 text-white rounded-full w-4 h-4 flex items-center justify-center">
                            <span className="text-xs">✓</span>
                          </div>
                        )}
                      </div>

                      {/* Content */}
                      <div className="flex-1 min-w-0">
                        <h3 className="font-bold text-gray-900 truncate">{product.name}</h3>
                        <p className="text-sm text-gray-600 mb-1">
                          by {product.farmer ? `${product.farmer.first_name} ${product.farmer.last_name}` : 'Unknown Farmer'}
                        </p>

                        <div className="flex items-center gap-4 text-sm">
                          {product.location && (
                            <div className="flex items-center gap-1 text-gray-500">
                              <MapPin size={12} className="text-green-500" />
                              {product.location}
                            </div>
                          )}
                          {product.average_rating && (
                            <div className="flex items-center gap-1">
                              <Star size={12} className="fill-yellow-400 text-yellow-400" />
                              <span className="text-gray-900">{product.average_rating.toFixed(1)}</span>
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Price */}
                      <div className="text-right flex-shrink-0">
                        <div className="font-bold text-green-600">KES {parseFloat(product.price).toLocaleString()}</div>
                        <div className="text-xs text-gray-500">{product.quantity_available || 'Available'}</div>
                      </div>
                    </div>
                  )}
                </Link>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Search className="h-8 w-8 text-gray-400" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No products found</h3>
              <p className="text-gray-600 mb-4">Try adjusting your filters or search terms.</p>
              <button
                onClick={() => {
                  setSearchTerm("")
                  setSelectedCategory("All")
                }}
                className="bg-green-600 hover:bg-green-700 text-white font-medium px-4 py-2 rounded-lg transition-colors"
              >
                Clear Filters
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default function DashboardMarketplacePage() {
  return (
    <ProtectedRoute>
      <DashboardLayout>
        <DashboardMarketplaceContent />
      </DashboardLayout>
    </ProtectedRoute>
  )
}