"use client"

import { useState, useEffect } from "react"
import Navbar from "@/components/navbar"
import { Search, MapPin, Star, Loader2 } from "lucide-react"
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

export default function MarketplacePage() {
  console.log("DEBUG: Marketplace component loaded")

  const [searchTerm, setSearchTerm] = useState("")
  const [selectedCategory, setSelectedCategory] = useState("All")
  const [sortBy, setSortBy] = useState("trending")
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
        console.log("DEBUG: Full API response:", response)
        if (response.data) {
          const productData = response.data.results || response.data
          console.log("DEBUG: Product data:", productData)
          console.log("DEBUG: First product:", productData[0])
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

    console.log("DEBUG: useEffect triggered, calling fetchProducts")
    fetchProducts()
  }, [searchTerm, selectedCategory, categories])

  const sortedProducts = Array.isArray(products) ? [...products].sort((a, b) => {
    if (sortBy === "price-low") return parseFloat(a.price_per_unit || a.price || "0") - parseFloat(b.price_per_unit || b.price || "0")
    if (sortBy === "price-high") return parseFloat(b.price_per_unit || b.price || "0") - parseFloat(a.price_per_unit || a.price || "0")
    if (sortBy === "rating") return (b.average_rating || 0) - (a.average_rating || 0)
    return 0
  }) : []

  const categoryOptions = ["All", ...(Array.isArray(categories) ? categories.map(c => c.name) : [])]

  return (
    <main className="min-h-screen bg-gray-50">
      <Navbar />

      {/* Header */}
      <div className="pt-32 pb-12 px-6 bg-white border-b border-gray-200">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">Marketplace</h1>
          <p className="text-lg text-gray-600 mb-6">Discover fresh, verified products from local farmers</p>
          <div className="flex flex-wrap gap-6 text-sm text-gray-500">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <span>500+ Active Farmers</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <span>Fresh Daily Harvests</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <span>Verified Quality</span>
            </div>
          </div>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="sticky top-24 bg-white shadow-lg border-b border-gray-100 z-40 py-8 px-6">
        <div className="max-w-6xl mx-auto">
          {/* Search Bar */}
          <div className="relative mb-8">
            <Search
              className="absolute left-5 top-1/2 transform -translate-y-1/2 text-gray-400"
              size={22}
            />
            <input
              type="text"
              placeholder="Search for fresh produce, grains, vegetables..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-14 pr-6 py-4 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 text-lg placeholder-gray-400 shadow-sm"
            />
          </div>

          {/* Category and Sort */}
          <div className="flex flex-col lg:flex-row gap-6 items-start lg:items-center justify-between">
            {/* Categories */}
            <div className="flex flex-wrap gap-3 overflow-x-auto pb-2">
              {categoryOptions.map((cat) => (
                <button
                  key={cat}
                  onClick={() => setSelectedCategory(cat)}
                  className={`px-6 py-3 rounded-xl font-semibold whitespace-nowrap transition-smooth ${
                    selectedCategory === cat
                      ? "bg-green-600 text-white shadow-md"
                      : "bg-gray-100 text-gray-700 hover:bg-gray-200 hover:shadow-sm"
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>

            {/* Sort */}
            <div className="flex items-center gap-3">
              <label className="text-gray-700 font-medium">Sort by:</label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 bg-white font-medium text-gray-700"
              >
                <option value="trending">Trending</option>
                <option value="price-low">Price: Low to High</option>
                <option value="price-high">Price: High to Low</option>
                <option value="rating">Highest Rated</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Products Grid */}
      <div className="px-6 py-12">
        <div className="max-w-6xl mx-auto">
          {error && (
            <div className="bg-red-50 border-l-4 border-red-500 text-red-700 px-6 py-4 rounded-lg mb-8 shadow-sm">
              <div className="flex items-center">
                <div className="w-6 h-6 bg-red-500 rounded-full flex items-center justify-center mr-3">
                  <span className="text-white text-sm font-bold">!</span>
                </div>
                {error}
              </div>
            </div>
          )}

          {isLoading ? (
            <div className="flex flex-col justify-center items-center py-20">
              <Loader2 className="h-12 w-12 animate-spin text-green-500 mb-4" />
              <span className="text-lg text-gray-600 font-medium">Loading fresh products...</span>
              <span className="text-sm text-gray-500 mt-1">Finding the best deals for you</span>
            </div>
          ) : sortedProducts.length > 0 ? (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {sortedProducts.map((product) => (
                <Link key={product.id} href={`/product/${product.id}`}>
                  <div className="bg-white rounded-2xl overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 cursor-pointer h-full flex flex-col group border border-gray-100">
                    {/* Image */}
                    <div className="relative h-52 bg-gray-50 overflow-hidden">
                      <img
                        src={product.primary_image || "/placeholder.svg"}
                        alt={product.name}
                        className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                        onError={(e) => {
                          e.currentTarget.src = "/placeholder.svg"
                        }}
                      />
                      {product.verified && (
                        <div className="absolute top-3 right-3 bg-green-600 text-white px-3 py-1.5 rounded-full text-xs font-bold flex items-center gap-1 shadow-md">
                          ✓ Verified
                        </div>
                      )}
                      <div className="absolute bottom-3 left-3 bg-white/90 backdrop-blur-sm px-3 py-1 rounded-full text-xs font-semibold text-gray-700">
                        {product.category?.name || 'Fresh Produce'}
                      </div>
                    </div>

                    {/* Content */}
                    <div className="p-5 flex-1 flex flex-col">
                      <h3 className="text-lg font-bold text-gray-900 mb-2 group-hover:text-green-600 transition-colors">{product.name}</h3>
                      <p className="text-sm text-gray-600 mb-3 font-medium">
                        by {product.farmer_name || 'Unknown Farmer'}
                      </p>

                      {/* Location */}
                      {product.location && (
                        <div className="flex items-center gap-2 text-sm text-gray-500 mb-4">
                          <MapPin size={16} className="text-green-500" />
                          {product.location}
                        </div>
                      )}

                      {/* Rating */}
                      {product.average_rating && (
                        <div className="flex items-center gap-2 mb-4">
                          <div className="flex items-center gap-1">
                            <Star size={16} className="fill-yellow-400 text-yellow-400" />
                            <span className="font-bold text-gray-900">{product.average_rating.toFixed(1)}</span>
                          </div>
                          <span className="text-sm text-gray-500">({product.reviews_count || 0} reviews)</span>
                        </div>
                      )}

                      {/* Quantity and Price */}
                      <div className="flex justify-between items-end mt-auto pt-4 border-t border-gray-100">
                        <div>
                          <p className="text-xs text-gray-500 uppercase tracking-wide">Available</p>
                          <p className="font-bold text-gray-900">{product.quantity_available || 'Contact seller'}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-xs text-gray-500 uppercase tracking-wide">Price</p>
                          <p className="text-xl font-bold text-green-600">KES {parseFloat(product.price_per_unit || product.price || "0").toLocaleString()}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          ) : (
            <div className="text-center py-20">
              <div className="max-w-md mx-auto">
                <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
                  <Search className="h-12 w-12 text-gray-400" />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">No products found</h3>
                <p className="text-gray-600 mb-6">We couldn't find any products matching your search criteria. Try adjusting your filters or search terms.</p>
                <button
                  onClick={() => {
                    setSearchTerm("")
                    setSelectedCategory("All")
                  }}
                  className="bg-green-600 hover:bg-green-700 text-white font-semibold px-6 py-3 rounded-xl transition-colors"
                >
                  Clear Filters
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </main>
  )
}
