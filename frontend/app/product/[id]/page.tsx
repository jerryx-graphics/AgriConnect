"use client"

import { useState } from "react"
import Navbar from "@/components/navbar"
import { Star, MapPin, Shield, Truck, MessageCircle, ShoppingCart } from "lucide-react"
import Link from "next/link"

export default function ProductPage({ params }: { params: { id: string } }) {
  const [quantity, setQuantity] = useState(1)

  // Mock product data
  const product = {
    id: params.id,
    name: "Fresh Bananas",
    farmer: "Jane Moraa",
    farmerImage: "/farmer-portrait.jpg",
    price: 2500,
    image: "/fresh-bananas.jpg",
    rating: 4.8,
    reviews: 124,
    location: "Kisii",
    quantity: "50kg available",
    verified: true,
    description:
      "Premium quality bananas harvested fresh from our farm in Kisii. Grown using sustainable farming practices without harmful pesticides. Perfect for retailers, restaurants, and wholesalers.",
    specifications: [
      { label: "Grade", value: "Grade A" },
      { label: "Harvest Date", value: "2024-01-15" },
      { label: "Shelf Life", value: "7-10 days" },
      { label: "Packaging", value: "Wooden crates" },
    ],
    images: ["/fresh-bananas.jpg", "/bananas-close-up.jpg", "/bananas-farm.jpg"],
  }

  const reviews = [
    {
      id: 1,
      author: "David Kimani",
      rating: 5,
      text: "Excellent quality! The bananas arrived fresh and in perfect condition. Will order again.",
      date: "2024-01-10",
    },
    {
      id: 2,
      author: "Sarah Mwangi",
      rating: 4,
      text: "Good product, fast delivery. Slightly smaller than expected but still satisfied.",
      date: "2024-01-08",
    },
  ]

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
                  src={product.image || "/placeholder.svg"}
                  alt={product.name}
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="grid grid-cols-3 gap-4">
                {product.images.map((img, idx) => (
                  <div
                    key={idx}
                    className="bg-white rounded-lg overflow-hidden cursor-pointer hover:ring-2 hover:ring-primary"
                  >
                    <img src={img || "/placeholder.svg"} alt={`View ${idx + 1}`} className="w-full h-24 object-cover" />
                  </div>
                ))}
              </div>
            </div>

            {/* Product Info */}
            <div>
              {/* Header */}
              <div className="mb-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h1 className="text-4xl font-bold text-foreground mb-2">{product.name}</h1>
                    <div className="flex items-center gap-2 mb-4">
                      <div className="flex items-center gap-1">
                        <Star size={20} className="fill-accent text-accent" />
                        <span className="font-bold text-foreground">{product.rating}</span>
                      </div>
                      <span className="text-foreground-secondary">({product.reviews} reviews)</span>
                    </div>
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
                  <p className="text-5xl font-bold text-primary">KES {product.price}</p>
                </div>

                {/* Location */}
                <div className="flex items-center gap-2 text-foreground-secondary mb-6">
                  <MapPin size={18} />
                  {product.location}
                </div>
              </div>

              {/* Description */}
              <p className="text-foreground-secondary mb-6 leading-relaxed">{product.description}</p>

              {/* Specifications */}
              <div className="bg-white rounded-lg p-4 mb-6">
                <h3 className="font-bold text-foreground mb-4">Specifications</h3>
                <div className="grid grid-cols-2 gap-4">
                  {product.specifications.map((spec, idx) => (
                    <div key={idx}>
                      <p className="text-sm text-foreground-secondary">{spec.label}</p>
                      <p className="font-semibold text-foreground">{spec.value}</p>
                    </div>
                  ))}
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
                <button className="flex-1 bg-primary hover:bg-primary-dark text-white font-bold py-3 rounded-lg transition-smooth flex items-center justify-center gap-2">
                  <ShoppingCart size={20} />
                  Add to Cart
                </button>
              </div>

              {/* Contact Farmer */}
              <button className="w-full border-2 border-primary text-primary hover:bg-primary/5 font-bold py-3 rounded-lg transition-smooth flex items-center justify-center gap-2">
                <MessageCircle size={20} />
                Contact Farmer
              </button>

              {/* Farmer Card */}
              <div className="bg-white rounded-lg p-4 mt-6 border border-border">
                <p className="text-sm text-foreground-secondary mb-3">Sold by</p>
                <div className="flex items-center gap-4">
                  <img
                    src={product.farmerImage || "/placeholder.svg"}
                    alt={product.farmer}
                    className="w-12 h-12 rounded-full"
                  />
                  <div className="flex-1">
                    <p className="font-bold text-foreground">{product.farmer}</p>
                    <p className="text-sm text-foreground-secondary">Kisii, Kenya</p>
                  </div>
                  <Link
                    href={`/farmer/${product.farmer}`}
                    className="text-primary hover:text-primary-dark font-semibold"
                  >
                    View Profile
                  </Link>
                </div>
              </div>

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
            <div className="space-y-6">
              {reviews.map((review) => (
                <div key={review.id} className="border-b border-border pb-6 last:border-b-0">
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <p className="font-bold text-foreground">{review.author}</p>
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
                        <span className="text-sm text-foreground-secondary">{review.date}</span>
                      </div>
                    </div>
                  </div>
                  <p className="text-foreground-secondary">{review.text}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}
