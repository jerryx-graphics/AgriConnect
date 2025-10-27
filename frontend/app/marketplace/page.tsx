"use client"

import { useState } from "react"
import Navbar from "@/components/navbar"
import { Search, MapPin, Star } from "lucide-react"
import Link from "next/link"

interface Product {
  id: string
  name: string
  farmer: string
  price: number
  image: string
  rating: number
  reviews: number
  location: string
  quantity: string
  verified: boolean
  category: string
}

const products: Product[] = [
  {
    id: "1",
    name: "Fresh Bananas",
    farmer: "Jane Moraa",
    price: 2500,
    image: "/fresh-bananas.jpg",
    rating: 4.8,
    reviews: 124,
    location: "Kisii",
    quantity: "50kg",
    verified: true,
    category: "Fruits",
  },
  {
    id: "2",
    name: "Organic Avocados",
    farmer: "David Kipchoge",
    price: 4200,
    image: "/organic-avocados.png",
    rating: 4.9,
    reviews: 89,
    location: "Kisii",
    quantity: "30kg",
    verified: true,
    category: "Fruits",
  },
  {
    id: "3",
    name: "Tea Leaves (Premium)",
    farmer: "Esther Nyaboke",
    price: 8500,
    image: "/premium-tea-leaves.jpg",
    rating: 4.7,
    reviews: 156,
    location: "Gucha",
    quantity: "20kg",
    verified: true,
    category: "Beverages",
  },
  {
    id: "4",
    name: "Fresh Tomatoes",
    farmer: "Peter Omondi",
    price: 1800,
    image: "/fresh-tomatoes.png",
    rating: 4.6,
    reviews: 92,
    location: "Kisii",
    quantity: "40kg",
    verified: true,
    category: "Vegetables",
  },
  {
    id: "5",
    name: "Maize (Dried)",
    farmer: "Grace Wanjiru",
    price: 3200,
    image: "/dried-maize.jpg",
    rating: 4.5,
    reviews: 67,
    location: "Nyamira",
    quantity: "100kg",
    verified: true,
    category: "Grains",
  },
  {
    id: "6",
    name: "Cabbage (Fresh)",
    farmer: "Samuel Kiplagat",
    price: 1200,
    image: "/fresh-cabbage.jpg",
    rating: 4.4,
    reviews: 45,
    location: "Kisii",
    quantity: "60kg",
    verified: false,
    category: "Vegetables",
  },
]

const categories = ["All", "Fruits", "Vegetables", "Grains", "Beverages"]

export default function MarketplacePage() {
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedCategory, setSelectedCategory] = useState("All")
  const [sortBy, setSortBy] = useState("trending")

  const filteredProducts = products.filter((product) => {
    const matchesSearch = product.name.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCategory = selectedCategory === "All" || product.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  const sortedProducts = [...filteredProducts].sort((a, b) => {
    if (sortBy === "price-low") return a.price - b.price
    if (sortBy === "price-high") return b.price - a.price
    if (sortBy === "rating") return b.rating - a.rating
    return 0
  })

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
              {categories.map((cat) => (
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
          {sortedProducts.length > 0 ? (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {sortedProducts.map((product) => (
                <Link key={product.id} href={`/product/${product.id}`}>
                  <div className="bg-white rounded-xl overflow-hidden shadow-sm hover:shadow-lg transition-smooth cursor-pointer h-full flex flex-col">
                    {/* Image */}
                    <div className="relative h-48 bg-background-secondary overflow-hidden">
                      <img
                        src={product.image || "/placeholder.svg"}
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
                      <p className="text-sm text-foreground-secondary mb-3">{product.farmer}</p>

                      {/* Location */}
                      <div className="flex items-center gap-1 text-sm text-foreground-secondary mb-3">
                        <MapPin size={16} />
                        {product.location}
                      </div>

                      {/* Rating */}
                      <div className="flex items-center gap-2 mb-4">
                        <div className="flex items-center gap-1">
                          <Star size={16} className="fill-accent text-accent" />
                          <span className="font-semibold text-foreground">{product.rating}</span>
                        </div>
                        <span className="text-sm text-foreground-secondary">({product.reviews})</span>
                      </div>

                      {/* Quantity and Price */}
                      <div className="flex justify-between items-end mt-auto">
                        <div>
                          <p className="text-xs text-foreground-secondary">Available</p>
                          <p className="font-semibold text-foreground">{product.quantity}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-xs text-foreground-secondary">Price</p>
                          <p className="text-2xl font-bold text-primary">KES {product.price}</p>
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
