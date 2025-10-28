"use client"

import { useState } from "react"
import { ProtectedRoute } from "@/components/protected-route"
import { DashboardLayout } from "@/components/dashboard-layout"
import { useAuth } from "@/lib/auth-context"
import { useRouter } from "next/navigation"
import {
  Upload,
  MapPin,
  Package,
  DollarSign,
  Camera,
  X,
  Plus,
  Loader2,
  ArrowLeft
} from "lucide-react"
import Link from "next/link"
import { apiClient } from "@/lib/api"

interface ProductForm {
  name: string
  description: string
  price: string
  quantity_available: string
  category: string
  location: string
  images: File[]
}

function CreateListingContent() {
  const { user } = useAuth()
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")

  const [form, setForm] = useState<ProductForm>({
    name: "",
    description: "",
    price: "",
    quantity_available: "",
    category: "",
    location: "",
    images: []
  })

  const categories = [
    "Fruits",
    "Vegetables",
    "Grains & Cereals",
    "Legumes",
    "Herbs & Spices",
    "Dairy Products",
    "Livestock",
    "Seeds & Seedlings",
    "Farm Equipment",
    "Other"
  ]

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setForm(prev => ({ ...prev, [name]: value }))
    if (error) setError("")
  }

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    if (files.length + form.images.length > 5) {
      setError("Maximum 5 images allowed")
      return
    }
    setForm(prev => ({ ...prev, images: [...prev.images, ...files] }))
  }

  const removeImage = (index: number) => {
    setForm(prev => ({
      ...prev,
      images: prev.images.filter((_, i) => i !== index)
    }))
  }

  const validateForm = () => {
    if (!form.name.trim()) {
      setError("Product name is required")
      return false
    }
    if (!form.description.trim()) {
      setError("Product description is required")
      return false
    }
    if (!form.price || parseFloat(form.price) <= 0) {
      setError("Valid price is required")
      return false
    }
    if (!form.quantity_available || parseInt(form.quantity_available) <= 0) {
      setError("Valid quantity is required")
      return false
    }
    if (!form.category) {
      setError("Category is required")
      return false
    }
    if (!form.location.trim()) {
      setError("Location is required")
      return false
    }
    return true
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) return

    // Check authentication
    if (!apiClient.isAuthenticated()) {
      setError("You must be logged in to create products. Please log in and try again.")
      return
    }

    // Check user role
    if (user?.role !== 'farmer') {
      setError("Only farmers can create product listings. Please contact support if you believe this is an error.")
      return
    }

    setIsLoading(true)
    setError("")

    try {
      // Map category names to IDs (from backend)
      const categoryMapping: { [key: string]: string } = {
        'Fruits': '8b1805fb-9bdb-4ebc-9498-0ff0facb6bb0',
        'Vegetables': 'd9db9b95-8c9a-48c9-8cf6-cc0fdd4b75aa',
        'Grains & Cereals': 'fdd8b1b1-83b1-4c71-8991-7b0fed936671',
        'Legumes': 'e0946cd7-9f37-46e2-bb0f-240a0105b7dd',
        'Herbs & Spices': 'fb55c768-9746-40e1-b3f9-6aaaff9a69ce',
        'Dairy Products': '0c01003f-3abd-4b0a-8eea-c2dfdcb409d4',
        'Livestock': '14e661ce-a3d5-4e40-a4bb-bd0f2e9fbd5d',
        'Seeds & Seedlings': '0c68826b-72f3-4f33-a5a3-5ebf3e24d98f',
        'Farm Equipment': '524a615e-3661-47bb-8df5-8cb45b3f8982',
        'Other': '8cedb2e0-b3eb-49b6-bd9d-24f962519fd0'
      }

      const categoryId = categoryMapping[form.category] || categoryMapping['Other']

      const formData = new FormData()
      formData.append('name', form.name)
      formData.append('description', form.description)
      formData.append('price_per_unit', form.price)
      formData.append('quantity_available', form.quantity_available)
      formData.append('category', categoryId) // Send category ID
      formData.append('county', form.location) // Use county for location
      formData.append('unit', 'kg') // Default unit
      formData.append('condition', 'fresh') // Default condition
      formData.append('quality_grade', 'standard') // Default quality grade
      formData.append('is_organic', 'false') // Default organic status
      formData.append('is_available', 'true') // Available by default

      // Handle images - backend expects 'uploaded_images' as a list
      form.images.forEach((image) => {
        formData.append(`uploaded_images`, image)
      })

      console.log("Sending form data with", form.images.length, "images")

      const response = await apiClient.createProduct(formData)

      if (response.data) {
        setSuccess("Product created successfully!")
        setTimeout(() => {
          router.push("/dashboard/products")
        }, 2000)
      } else {
        if (response.error?.includes('403') || response.error?.includes('Forbidden')) {
          setError("Permission denied. Please try logging out and back in, then try again.")
        } else {
          setError(response.error || "Failed to create product")
        }
      }
    } catch (err) {
      console.error("Error creating product:", err)
      setError("Failed to create product. Please check your connection and try again.")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <Link
          href="/dashboard/products"
          className="flex items-center gap-2 text-green-600 hover:text-green-700 transition-colors"
        >
          <ArrowLeft size={20} />
          Back to Products
        </Link>
      </div>

      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-green-900 mb-2">Create New Product Listing</h1>
          <p className="text-green-600">Add your agricultural products to the marketplace</p>
        </div>
      </div>


      {/* Alert Messages */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {success && (
        <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
          {success}
        </div>
      )}

      {/* Form */}
      <div className="bg-white rounded-xl shadow-sm border border-green-100">
        <form onSubmit={handleSubmit} className="p-6 space-y-6">

          {/* Product Images */}
          <div>
            <label className="block text-sm font-semibold text-green-900 mb-3">
              Product Images (Max 5)
            </label>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-4">
              {form.images.map((image, index) => (
                <div key={index} className="relative">
                  <img
                    src={URL.createObjectURL(image)}
                    alt={`Product ${index + 1}`}
                    className="w-full h-24 object-cover rounded-lg border border-green-200"
                  />
                  <button
                    type="button"
                    onClick={() => removeImage(index)}
                    className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600 transition-colors"
                  >
                    <X size={12} />
                  </button>
                </div>
              ))}

              {form.images.length < 5 && (
                <label className="flex flex-col items-center justify-center w-full h-24 border-2 border-green-300 border-dashed rounded-lg cursor-pointer bg-green-50 hover:bg-green-100 transition-colors">
                  <Camera className="text-green-500" size={20} />
                  <span className="text-xs text-green-600 mt-1">Add Photo</span>
                  <input
                    type="file"
                    multiple
                    accept="image/*"
                    onChange={handleImageUpload}
                    className="hidden"
                  />
                </label>
              )}
            </div>
            <p className="text-sm text-green-600">
              Upload up to 5 high-quality images of your product
              {form.images.length > 0 && (
                <span className="font-semibold"> • {form.images.length} image{form.images.length !== 1 ? 's' : ''} selected</span>
              )}
            </p>
          </div>

          {/* Product Details Grid */}
          <div className="grid md:grid-cols-2 gap-6">

            {/* Product Name */}
            <div>
              <label className="block text-sm font-semibold text-green-900 mb-2">
                Product Name *
              </label>
              <input
                type="text"
                name="name"
                value={form.name}
                onChange={handleInputChange}
                placeholder="e.g., Fresh Organic Bananas"
                className="w-full px-4 py-3 border-2 border-green-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
                required
              />
            </div>

            {/* Category */}
            <div>
              <label className="block text-sm font-semibold text-green-900 mb-2">
                Category *
              </label>
              <select
                name="category"
                value={form.category}
                onChange={handleInputChange}
                className="w-full px-4 py-3 border-2 border-green-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
                required
              >
                <option value="">Select a category</option>
                {categories.map(category => (
                  <option key={category} value={category}>{category}</option>
                ))}
              </select>
            </div>

            {/* Price */}
            <div>
              <label className="block text-sm font-semibold text-green-900 mb-2">
                Price per Unit (KES) *
              </label>
              <div className="relative">
                <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 text-green-500" size={20} />
                <input
                  type="number"
                  name="price"
                  value={form.price}
                  onChange={handleInputChange}
                  placeholder="0.00"
                  min="0"
                  step="0.01"
                  className="w-full pl-12 pr-4 py-3 border-2 border-green-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
                  required
                />
              </div>
            </div>

            {/* Quantity */}
            <div>
              <label className="block text-sm font-semibold text-green-900 mb-2">
                Quantity Available *
              </label>
              <div className="relative">
                <Package className="absolute left-3 top-1/2 transform -translate-y-1/2 text-green-500" size={20} />
                <input
                  type="number"
                  name="quantity_available"
                  value={form.quantity_available}
                  onChange={handleInputChange}
                  placeholder="e.g., 100 kg, 50 pieces"
                  min="1"
                  className="w-full pl-12 pr-4 py-3 border-2 border-green-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
                  required
                />
              </div>
            </div>

          </div>

          {/* Location */}
          <div>
            <label className="block text-sm font-semibold text-green-900 mb-2">
              Location *
            </label>
            <div className="relative">
              <MapPin className="absolute left-3 top-4 text-green-500" size={20} />
              <input
                type="text"
                name="location"
                value={form.location}
                onChange={handleInputChange}
                placeholder="e.g., Kisii, Kenya"
                className="w-full pl-12 pr-4 py-3 border-2 border-green-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
                required
              />
            </div>
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-semibold text-green-900 mb-2">
              Product Description *
            </label>
            <textarea
              name="description"
              value={form.description}
              onChange={handleInputChange}
              placeholder="Describe your product in detail. Include quality, size, harvest date, organic certification, etc."
              rows={4}
              className="w-full px-4 py-3 border-2 border-green-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 resize-none"
              required
            />
          </div>

          {/* Submit Buttons */}
          <div className="flex gap-4 pt-6 border-t border-green-100">
            <button
              type="submit"
              disabled={isLoading}
              className="flex-1 flex items-center justify-center gap-2 bg-green-600 hover:bg-green-700 disabled:bg-green-400 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
            >
              {isLoading ? (
                <>
                  <Loader2 className="animate-spin" size={20} />
                  Creating Product...
                </>
              ) : (
                <>
                  <Plus size={20} />
                  Create Product Listing
                </>
              )}
            </button>

            <Link
              href="/dashboard/products"
              className="flex items-center justify-center gap-2 border-2 border-green-200 text-green-700 hover:bg-green-50 font-semibold py-3 px-6 rounded-lg transition-colors"
            >
              Cancel
            </Link>
          </div>

        </form>
      </div>

      {/* Tips */}
      <div className="bg-green-50 rounded-xl p-6 border border-green-100">
        <h3 className="text-lg font-bold text-green-900 mb-4">Tips for Better Listings</h3>
        <div className="grid md:grid-cols-2 gap-4 text-sm text-green-700">
          <div>
            <h4 className="font-semibold mb-2">Product Photos:</h4>
            <ul className="space-y-1">
              <li>• Use natural lighting</li>
              <li>• Show different angles</li>
              <li>• Include size reference</li>
              <li>• Highlight quality details</li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-2">Product Description:</h4>
            <ul className="space-y-1">
              <li>• Mention harvest date</li>
              <li>• Include size/weight details</li>
              <li>• Highlight organic certification</li>
              <li>• Specify storage conditions</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function CreateListingPage() {
  return (
    <ProtectedRoute>
      <DashboardLayout>
        <CreateListingContent />
      </DashboardLayout>
    </ProtectedRoute>
  )
}