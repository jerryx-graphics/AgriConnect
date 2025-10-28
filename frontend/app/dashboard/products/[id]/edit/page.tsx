"use client"

import { useState, useEffect } from "react"
import { ProtectedRoute } from "@/components/protected-route"
import { DashboardLayout } from "@/components/dashboard-layout"
import { useAuth } from "@/lib/auth-context"
import { useRouter, useParams } from "next/navigation"
import {
  Upload,
  MapPin,
  Package,
  DollarSign,
  Camera,
  X,
  Save,
  Loader2,
  ArrowLeft
} from "lucide-react"
import Link from "next/link"
import { apiClient } from "@/lib/api"

interface ProductForm {
  name: string
  description: string
  price_per_unit: string
  quantity_available: string
  category: string
  county: string
  images: File[]
}

function EditProductContent() {
  const { user } = useAuth()
  const router = useRouter()
  const params = useParams()
  const productId = params.id as string

  const [isLoading, setIsLoading] = useState(false)
  const [isLoadingProduct, setIsLoadingProduct] = useState(true)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")

  const [form, setForm] = useState<ProductForm>({
    name: "",
    description: "",
    price_per_unit: "",
    quantity_available: "",
    category: "",
    county: "",
    images: []
  })

  const [existingImages, setExistingImages] = useState<Array<{id: string, image: string}>>([])

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

  useEffect(() => {
    if (productId) {
      fetchProduct()
    }
  }, [productId])

  const fetchProduct = async () => {
    try {
      const response = await apiClient.getProduct(productId)
      if (response.data) {
        const product = response.data
        setForm({
          name: product.name || "",
          description: product.description || "",
          price_per_unit: product.price_per_unit || "",
          quantity_available: product.quantity_available || "",
          category: product.category?.name || "",
          county: product.county || "",
          images: []
        })
        setExistingImages(product.images || [])
      } else {
        setError("Product not found")
      }
    } catch (error) {
      console.error("Failed to fetch product:", error)
      setError("Failed to load product")
    } finally {
      setIsLoadingProduct(false)
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setForm(prev => ({ ...prev, [name]: value }))
    if (error) setError("")
  }

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    if (files.length + form.images.length + existingImages.length > 5) {
      setError("Maximum 5 images allowed")
      return
    }
    setForm(prev => ({ ...prev, images: [...prev.images, ...files] }))
  }

  const removeNewImage = (index: number) => {
    setForm(prev => ({
      ...prev,
      images: prev.images.filter((_, i) => i !== index)
    }))
  }

  const removeExistingImage = (index: number) => {
    setExistingImages(prev => prev.filter((_, i) => i !== index))
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
    if (!form.price_per_unit || parseFloat(form.price_per_unit) <= 0) {
      setError("Valid price is required")
      return false
    }
    if (!form.quantity_available || parseInt(form.quantity_available) <= 0) {
      setError("Valid quantity is required")
      return false
    }
    return true
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) return

    setIsLoading(true)
    setError("")

    try {
      // Map category names to IDs
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
      formData.append('price_per_unit', form.price_per_unit)
      formData.append('quantity_available', form.quantity_available)
      formData.append('category', categoryId)
      formData.append('county', form.county)
      formData.append('unit', 'kg')
      formData.append('condition', 'fresh')
      formData.append('quality_grade', 'standard')
      formData.append('is_organic', 'false')
      formData.append('is_available', 'true')

      form.images.forEach((image) => {
        formData.append(`uploaded_images`, image)
      })

      const response = await apiClient.updateProduct(productId, formData)

      if (response.data) {
        setSuccess("Product updated successfully!")
        setTimeout(() => {
          router.push("/dashboard/products")
        }, 2000)
      } else {
        setError(response.error || "Failed to update product")
      }
    } catch (err) {
      console.error("Error updating product:", err)
      setError("Failed to update product. Please try again.")
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoadingProduct) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
      </div>
    )
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
          <h1 className="text-3xl font-bold text-green-900 mb-2">Edit Product</h1>
          <p className="text-green-600">Update your product information</p>
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
              {/* Existing Images */}
              {existingImages.map((image, index) => (
                <div key={`existing-${index}`} className="relative">
                  <img
                    src={image.image?.startsWith('http') ? image.image : `http://localhost:8000${image.image}`}
                    alt={`Existing ${index + 1}`}
                    className="w-full h-24 object-cover rounded-lg border border-green-200"
                  />
                  <button
                    type="button"
                    onClick={() => removeExistingImage(index)}
                    className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600 transition-colors"
                  >
                    <X size={12} />
                  </button>
                </div>
              ))}

              {/* New Images */}
              {form.images.map((image, index) => (
                <div key={`new-${index}`} className="relative">
                  <img
                    src={URL.createObjectURL(image)}
                    alt={`New ${index + 1}`}
                    className="w-full h-24 object-cover rounded-lg border border-green-200"
                  />
                  <button
                    type="button"
                    onClick={() => removeNewImage(index)}
                    className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600 transition-colors"
                  >
                    <X size={12} />
                  </button>
                </div>
              ))}

              {form.images.length + existingImages.length < 5 && (
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
                  name="price_per_unit"
                  value={form.price_per_unit}
                  onChange={handleInputChange}
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
                name="county"
                value={form.county}
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
                  Updating Product...
                </>
              ) : (
                <>
                  <Save size={20} />
                  Update Product
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
    </div>
  )
}

export default function EditProductPage() {
  return (
    <ProtectedRoute>
      <DashboardLayout>
        <EditProductContent />
      </DashboardLayout>
    </ProtectedRoute>
  )
}