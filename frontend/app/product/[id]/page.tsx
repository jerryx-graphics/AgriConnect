"use client"

import { useState, useEffect } from "react"
import Navbar from "@/components/navbar"
import { Star, MapPin, Shield, Truck, MessageCircle, ShoppingCart, Loader2, ArrowLeft } from "lucide-react"
import Link from "next/link"
import { apiClient } from "@/lib/api"
import { useAuth } from "@/lib/auth-context"

interface Product {
  id: string
  name: string
  farmer?: {
    id: string
    first_name: string
    last_name: string
    profile?: any
  }
  price: string
  images?: Array<{ image: string }>
  average_rating?: number
  reviews_count?: number
  location?: string
  quantity_available?: string
  verified?: boolean
  description?: string
  category?: {
    name: string
  }
  created_at?: string
}

interface Review {
  id: string
  user: {
    first_name: string
    last_name: string
  }
  rating: number
  comment: string
  created_at: string
}

export default function ProductPage({ params }: { params: { id: string } }) {
  const [quantity, setQuantity] = useState(1)
  const [product, setProduct] = useState<Product | null>(null)
  const [reviews, setReviews] = useState<Review[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState("")
  const [addingToCart, setAddingToCart] = useState(false)
  const { isAuthenticated } = useAuth()

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        const response = await apiClient.getProduct(params.id)
        if (response.data) {
          setProduct(response.data)
          // In a real implementation, you'd fetch reviews separately
          // setReviews(response.data.reviews || [])
        } else {
          setError(response.error || "Product not found")
        }
      } catch (error) {
        console.error("Failed to fetch product:", error)
        setError("Failed to load product")
      } finally {
        setIsLoading(false)
      }
    }

    fetchProduct()
  }, [params.id])

  const handleAddToCart = async () => {
    if (!isAuthenticated) {
      // Redirect to login or show login modal
      return
    }

    setAddingToCart(true)
    try {
      const response = await apiClient.addToCart(params.id, quantity)
      if (response.data) {
        // Show success message or update cart state
        alert("Product added to cart!")
      } else {
        alert(response.error || "Failed to add to cart")
      }
    } catch (error) {
      console.error("Failed to add to cart:", error)
      alert("Failed to add to cart")
    } finally {
      setAddingToCart(false)
    }
  }

  if (isLoading) {
    return (
      <main className="min-h-screen bg-background-secondary">
        <Navbar />
        <div className="flex justify-center items-center min-h-[calc(100vh-80px)]">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2 text-foreground-secondary">Loading product...</span>
        </div>
      </main>
    )
  }

  if (error || !product) {
    return (
      <main className="min-h-screen bg-background-secondary">
        <Navbar />
        <div className="flex flex-col justify-center items-center min-h-[calc(100vh-80px)] px-6">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-foreground mb-4">Product Not Found</h1>
            <p className="text-foreground-secondary mb-6">{error}</p>
            <Link
              href="/marketplace"
              className="inline-flex items-center gap-2 bg-primary text-white px-6 py-3 rounded-lg hover:bg-primary-dark transition-smooth"
            >
              <ArrowLeft size={20} />
              Back to Marketplace
            </Link>
          </div>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-background-secondary">
      <Navbar />

      <div className="pt-32 pb-12 px-6">
        <div className="max-w-6xl mx-auto">
          {/* Breadcrumb */}
          <div className="flex gap-2 text-sm text-foreground-secondary mb-8">
            <Link href="/marketplace" className="hover:text-primary">
              Marketplace
            </Link>
            <span>/</span>
            <span className="text-foreground">{product.name}</span>
          </div>

          <div className="grid lg:grid-cols-2 gap-8 mb-12">
            {/* Images */}
            <div>
              <div className="bg-white rounded-xl overflow-hidden mb-4 h-96">
                <img
                  src={product.images?.[0]?.image || "/placeholder.svg"}
                  alt={product.name}
                  className="w-full h-full object-cover"
                />
              </div>
              {product.images && product.images.length > 1 && (
                <div className="grid grid-cols-3 gap-4">
                  {product.images.slice(0, 3).map((img, idx) => (
                    <div
                      key={idx}
                      className="bg-white rounded-lg overflow-hidden cursor-pointer hover:ring-2 hover:ring-primary"
                    >
                      <img src={img.image || "/placeholder.svg"} alt={`View ${idx + 1}`} className="w-full h-24 object-cover" />
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Product Info */}
            <div>
              {/* Header */}
              <div className="mb-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h1 className="text-4xl font-bold text-foreground mb-2">{product.name}</h1>
                    {product.average_rating && (
                      <div className="flex items-center gap-2 mb-4">
                        <div className="flex items-center gap-1">
                          <Star size={20} className="fill-accent text-accent" />
                          <span className="font-bold text-foreground">{product.average_rating.toFixed(1)}</span>
                        </div>
                        <span className="text-foreground-secondary">({product.reviews_count || 0} reviews)</span>
                      </div>
                    )}
                  </div>
                  {product.verified && (
                    <div className="bg-primary/10 text-primary px-3 py-1 rounded-full text-sm font-semibold flex items-center gap-1">
                      <Shield size={16} /> Verified
                    </div>
                  )}
                </div>

                {/* Price */}
                <div className="mb-6">
                  <p className="text-foreground-secondary text-sm mb-1">Price per unit</p>
                  <p className="text-5xl font-bold text-primary">KES {parseFloat(product.price).toLocaleString()}</p>
                </div>

                {/* Location */}
                {product.location && (
                  <div className="flex items-center gap-2 text-foreground-secondary mb-6">
                    <MapPin size={18} />
                    {product.location}
                  </div>
                )}
              </div>

              {/* Description */}
              {product.description && (
                <p className="text-foreground-secondary mb-6 leading-relaxed">{product.description}</p>
              )}

              {/* Product Details */}
              <div className="bg-white rounded-lg p-4 mb-6">
                <h3 className="font-bold text-foreground mb-4">Product Details</h3>
                <div className="grid grid-cols-2 gap-4">
                  {product.category && (
                    <div>
                      <p className="text-sm text-foreground-secondary">Category</p>
                      <p className="font-semibold text-foreground">{product.category.name}</p>
                    </div>
                  )}
                  {product.quantity_available && (
                    <div>
                      <p className="text-sm text-foreground-secondary">Available Quantity</p>
                      <p className="font-semibold text-foreground">{product.quantity_available}</p>
                    </div>
                  )}
                  {product.created_at && (
                    <div>
                      <p className="text-sm text-foreground-secondary">Listed Date</p>
                      <p className="font-semibold text-foreground">{new Date(product.created_at).toLocaleDateString()}</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Quantity and CTA */}
              <div className="flex gap-4 mb-6">
                <div className="flex items-center border border-border rounded-lg">
                  <button
                    onClick={() => setQuantity(Math.max(1, quantity - 1))}
                    className="px-4 py-2 hover:bg-background-secondary"
                  >
                    −
                  </button>
                  <input
                    type="number"
                    value={quantity}
                    onChange={(e) => setQuantity(Math.max(1, Number.parseInt(e.target.value) || 1))}
                    className="w-16 text-center border-l border-r border-border py-2 focus:outline-none"
                  />
                  <button onClick={() => setQuantity(quantity + 1)} className="px-4 py-2 hover:bg-background-secondary">
                    +
                  </button>
                </div>
                <button
                  onClick={handleAddToCart}
                  disabled={addingToCart || !isAuthenticated}
                  className="flex-1 bg-primary hover:bg-primary-dark text-white font-bold py-3 rounded-lg transition-smooth flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {addingToCart ? (
                    <Loader2 size={20} className="animate-spin" />
                  ) : (
                    <ShoppingCart size={20} />
                  )}
                  {addingToCart ? "Adding..." : isAuthenticated ? "Add to Cart" : "Login to Add to Cart"}
                </button>
              </div>

              {/* Contact Farmer */}
              <button className="w-full border-2 border-primary text-primary hover:bg-primary/5 font-bold py-3 rounded-lg transition-smooth flex items-center justify-center gap-2">
                <MessageCircle size={20} />
                Contact Farmer
              </button>

              {/* Farmer Card */}
              {product.farmer && (
                <div className="bg-white rounded-lg p-4 mt-6 border border-border">
                  <p className="text-sm text-foreground-secondary mb-3">Sold by</p>
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center text-primary font-bold">
                      {product.farmer.first_name[0]}{product.farmer.last_name[0]}
                    </div>
                    <div className="flex-1">
                      <p className="font-bold text-foreground">
                        {product.farmer.first_name} {product.farmer.last_name}
                      </p>
                      <p className="text-sm text-foreground-secondary">{product.location || "Kenya"}</p>
                    </div>
                    <Link
                      href={`/farmer/${product.farmer.id}`}
                      className="text-primary hover:text-primary-dark font-semibold"
                    >
                      View Profile
                    </Link>
                  </div>
                </div>
              )}

              {/* Shipping Info */}
              <div className="bg-primary/5 rounded-lg p-4 mt-6 flex items-start gap-3">
                <Truck className="text-primary flex-shrink-0 mt-1" size={20} />
                <div>
                  <p className="font-semibold text-foreground">Fast Delivery</p>
                  <p className="text-sm text-foreground-secondary">Delivery within 2-3 days to major cities</p>
                </div>
              </div>
            </div>
          </div>

          {/* Reviews Section */}
          <div className="bg-white rounded-xl p-8 border border-border">
            <h2 className="text-2xl font-bold text-foreground mb-6">Customer Reviews</h2>
            {reviews.length > 0 ? (
              <div className="space-y-6">
                {reviews.map((review) => (
                  <div key={review.id} className="border-b border-border pb-6 last:border-b-0">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <p className="font-bold text-foreground">
                          {review.user.first_name} {review.user.last_name}
                        </p>
                        <div className="flex items-center gap-2">
                          <div className="flex gap-1">
                            {[...Array(5)].map((_, i) => (
                              <Star
                                key={i}
                                size={16}
                                className={i < review.rating ? "fill-accent text-accent" : "text-border"}
                              />
                            ))}
                          </div>
                          <span className="text-sm text-foreground-secondary">
                            {new Date(review.created_at).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                    </div>
                    <p className="text-foreground-secondary">{review.comment}</p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-foreground-secondary">No reviews yet. Be the first to review this product!</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  )
}
