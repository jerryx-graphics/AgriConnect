"use client"

import { useState, useEffect } from "react"
import Navbar from "@/components/navbar"
import { Search, MapPin, Star, Loader2 } from "lucide-react"
import Link from "next/link"
import { apiClient } from "@/lib/api"

interface Product {
  id: string
  name: string
  farmer?: {
    first_name: string
    last_name: string
  }
  price: string
  images?: Array<{ image: string }>
  average_rating?: number
  reviews_count?: number
  location?: string
  quantity_available?: string
  verified?: boolean
  category?: {
    name: string
  }
  description?: string
}

interface Category {
  id: string
  name: string
}

export default function MarketplacePage() {
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
        if (response.data) {
          setCategories(response.data)
        }
      } catch (error) {
        console.error("Failed to fetch categories:", error)
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
        if (selectedCategory !== "All") {
          const category = categories.find(c => c.name === selectedCategory)
          if (category) params.category = category.id
        }

        const response = await apiClient.getProducts(params)
        if (response.data) {
          setProducts(response.data.results || response.data)
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

  const sortedProducts = [...products].sort((a, b) => {
    if (sortBy === "price-low") return parseFloat(a.price) - parseFloat(b.price)
    if (sortBy === "price-high") return parseFloat(b.price) - parseFloat(a.price)
    if (sortBy === "rating") return (b.average_rating || 0) - (a.average_rating || 0)
    return 0
  })

  const categoryOptions = ["All", ...categories.map(c => c.name)]

  return (
    <main className="min-h-screen bg-background-secondary">
      <Navbar />

      {/* Header */}
      <div className="pt-32 pb-12 px-6 bg-gradient-to-b from-primary/5 to-transparent">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-4">Marketplace</h1>
          <p className="text-lg text-foreground-secondary">Discover fresh, verified products from local farmers</p>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="sticky top-24 bg-white shadow-sm z-40 py-6 px-6">
        <div className="max-w-6xl mx-auto">
          {/* Search Bar */}
          <div className="relative mb-6">
            <Search
              className="absolute left-4 top-1/2 transform -translate-y-1/2 text-foreground-secondary"
              size={20}
            />
            <input
              type="text"
              placeholder="Search products..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-12 pr-4 py-3 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>

          {/* Category and Sort */}
          <div className="flex flex-col md:flex-row gap-4 items-start md:items-center justify-between">
            {/* Categories */}
            <div className="flex gap-2 overflow-x-auto pb-2">
              {categoryOptions.map((cat) => (
                <button
                  key={cat}
                  onClick={() => setSelectedCategory(cat)}
                  className={`px-4 py-2 rounded-full font-medium whitespace-nowrap transition-smooth ${
                    selectedCategory === cat
                      ? "bg-primary text-white"
                      : "bg-background-secondary text-foreground hover:bg-border"
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>

            {/* Sort */}
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-4 py-2 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="trending">Trending</option>
              <option value="price-low">Price: Low to High</option>
              <option value="price-high">Price: High to Low</option>
              <option value="rating">Highest Rated</option>
            </select>
          </div>
        </div>
      </div>

      {/* Products Grid */}
      <div className="px-6 py-12">
        <div className="max-w-6xl mx-auto">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
              {error}
            </div>
          )}

          {isLoading ? (
            <div className="flex justify-center items-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
              <span className="ml-2 text-foreground-secondary">Loading products...</span>
            </div>
          ) : sortedProducts.length > 0 ? (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {sortedProducts.map((product) => (
                <Link key={product.id} href={`/product/${product.id}`}>
                  <div className="bg-white rounded-xl overflow-hidden shadow-sm hover:shadow-lg transition-smooth cursor-pointer h-full flex flex-col">
                    {/* Image */}
                    <div className="relative h-48 bg-background-secondary overflow-hidden">
                      <img
                        src={product.images?.[0]?.image || "/placeholder.svg"}
                        alt={product.name}
                        className="w-full h-full object-cover hover:scale-105 transition-smooth"
                      />
                      {product.verified && (
                        <div className="absolute top-3 right-3 bg-primary text-white px-3 py-1 rounded-full text-xs font-semibold flex items-center gap-1">
                          ✓ Verified
                        </div>
                      )}
                    </div>

                    {/* Content */}
                    <div className="p-4 flex-1 flex flex-col">
                      <h3 className="text-lg font-bold text-foreground mb-1">{product.name}</h3>
                      <p className="text-sm text-foreground-secondary mb-3">
                        {product.farmer ?
                          `${product.farmer.first_name} ${product.farmer.last_name}` :
                          'Unknown Farmer'
                        }
                      </p>

                      {/* Location */}
                      {product.location && (
                        <div className="flex items-center gap-1 text-sm text-foreground-secondary mb-3">
                          <MapPin size={16} />
                          {product.location}
                        </div>
                      )}

                      {/* Rating */}
                      {product.average_rating && (
                        <div className="flex items-center gap-2 mb-4">
                          <div className="flex items-center gap-1">
                            <Star size={16} className="fill-accent text-accent" />
                            <span className="font-semibold text-foreground">{product.average_rating.toFixed(1)}</span>
                          </div>
                          <span className="text-sm text-foreground-secondary">({product.reviews_count || 0})</span>
                        </div>
                      )}

                      {/* Quantity and Price */}
                      <div className="flex justify-between items-end mt-auto">
                        <div>
                          <p className="text-xs text-foreground-secondary">Available</p>
                          <p className="font-semibold text-foreground">{product.quantity_available || 'Contact seller'}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-xs text-foreground-secondary">Price</p>
                          <p className="text-2xl font-bold text-primary">KES {parseFloat(product.price).toLocaleString()}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-lg text-foreground-secondary">No products found. Try adjusting your filters.</p>
            </div>
          )}
        </div>
      </div>
    </main>
  )
}
