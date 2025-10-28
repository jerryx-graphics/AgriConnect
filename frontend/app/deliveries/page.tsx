"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { ProtectedRoute } from "@/components/protected-route"
import { useAuth } from "@/lib/auth-context"
import Navbar from "@/components/navbar"
import {
  Truck,
  MapPin,
  Clock,
  CheckCircle,
  AlertCircle,
  Package,
  Route,
  Navigation,
  Star,
  Phone,
  Eye
} from "lucide-react"
import Link from "next/link"
import { apiClient } from "@/lib/api"

interface Delivery {
  id: string
  order_id: string
  transporter_name: string
  transporter_phone: string
  vehicle_info: string
  pickup_address: string
  delivery_address: string
  estimated_delivery: string
  actual_delivery?: string
  status: string
  tracking_updates: Array<{
    id: string
    location: string
    status: string
    timestamp: string
    notes?: string
  }>
  created_at: string
}

interface Vehicle {
  id: string
  license_plate: string
  vehicle_type: string
  capacity: string
  owner_name: string
  is_available: boolean
}

function DeliveriesContent() {
  const { user } = useAuth()
  const [deliveries, setDeliveries] = useState<Delivery[]>([])
  const [vehicles, setVehicles] = useState<Vehicle[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [activeTab, setActiveTab] = useState("deliveries")
  const [error, setError] = useState("")

  useEffect(() => {
    fetchDeliveriesData()
  }, [])

  const fetchDeliveriesData = async () => {
    try {
      const [deliveriesResponse, vehiclesResponse] = await Promise.all([
        apiClient.getDeliveries(),
        apiClient.getVehicles()
      ])

      if (deliveriesResponse.data) {
        setDeliveries(deliveriesResponse.data.results || deliveriesResponse.data)
      }

      if (vehiclesResponse.data) {
        setVehicles(vehiclesResponse.data.results || vehiclesResponse.data)
      }
    } catch (err) {
      setError("Failed to load delivery data")
      console.error("Error fetching delivery data:", err)
    } finally {
      setIsLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'delivered':
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'in_transit':
      case 'en_route':
        return 'bg-blue-100 text-blue-800'
      case 'picked_up':
        return 'bg-yellow-100 text-yellow-800'
      case 'delayed':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'delivered':
      case 'completed':
        return <CheckCircle size={16} className="text-green-600" />
      case 'in_transit':
      case 'en_route':
        return <Truck size={16} className="text-blue-600" />
      case 'picked_up':
        return <Package size={16} className="text-yellow-600" />
      case 'delayed':
        return <AlertCircle size={16} className="text-red-600" />
      default:
        return <Clock size={16} className="text-gray-600" />
    }
  }

  const mockDeliveries: Delivery[] = [
    {
      id: "DEL001",
      order_id: "ORD001",
      transporter_name: "John Kiprotich",
      transporter_phone: "+254712345678",
      vehicle_info: "Toyota Hiace - KBZ 123A",
      pickup_address: "Kisii Central Market, Kisii",
      delivery_address: "Westlands, Nairobi",
      estimated_delivery: "2025-10-29T14:00:00Z",
      status: "in_transit",
      tracking_updates: [
        {
          id: "1",
          location: "Kisii Central Market",
          status: "picked_up",
          timestamp: "2025-10-28T08:00:00Z",
          notes: "Products loaded and checked"
        },
        {
          id: "2",
          location: "Keroka Junction",
          status: "in_transit",
          timestamp: "2025-10-28T09:30:00Z"
        },
        {
          id: "3",
          location: "Awendo",
          status: "in_transit",
          timestamp: "2025-10-28T11:00:00Z"
        }
      ],
      created_at: "2025-10-28T07:00:00Z"
    },
    {
      id: "DEL002",
      order_id: "ORD002",
      transporter_name: "Mary Wanjiku",
      transporter_phone: "+254723456789",
      vehicle_info: "Isuzu Truck - KCA 456B",
      pickup_address: "Nyamira Tea Factory",
      delivery_address: "Mombasa Port",
      estimated_delivery: "2025-10-30T16:00:00Z",
      actual_delivery: "2025-10-28T15:30:00Z",
      status: "delivered",
      tracking_updates: [
        {
          id: "1",
          location: "Nyamira Tea Factory",
          status: "picked_up",
          timestamp: "2025-10-27T06:00:00Z"
        },
        {
          id: "2",
          location: "Nairobi",
          status: "in_transit",
          timestamp: "2025-10-27T18:00:00Z"
        },
        {
          id: "3",
          location: "Mombasa Port",
          status: "delivered",
          timestamp: "2025-10-28T15:30:00Z",
          notes: "Delivered successfully. Customer signature obtained."
        }
      ],
      created_at: "2025-10-27T05:00:00Z"
    }
  ]

  const mockVehicles: Vehicle[] = [
    {
      id: "VEH001",
      license_plate: "KBZ 123A",
      vehicle_type: "Van",
      capacity: "1.5 tons",
      owner_name: "John Kiprotich",
      is_available: false
    },
    {
      id: "VEH002",
      license_plate: "KCA 456B",
      vehicle_type: "Truck",
      capacity: "5 tons",
      owner_name: "Mary Wanjiku",
      is_available: true
    },
    {
      id: "VEH003",
      license_plate: "KDB 789C",
      vehicle_type: "Pickup",
      capacity: "1 ton",
      owner_name: "David Otieno",
      is_available: true
    }
  ]

  const displayDeliveries = deliveries.length > 0 ? deliveries : mockDeliveries
  const displayVehicles = vehicles.length > 0 ? vehicles : mockVehicles

  return (
    <main className="min-h-screen bg-background-secondary">
      <Navbar />

      <div className="pt-32 pb-12 px-6">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-foreground mb-2">Logistics & Delivery</h1>
            <p className="text-foreground-secondary">Track deliveries and manage logistics operations</p>
          </div>

          {/* Logistics Stats */}
          <div className="grid md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-xl p-6 shadow-sm border border-border">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-foreground-secondary mb-1">Active Deliveries</p>
                  <p className="text-3xl font-bold text-foreground">
                    {displayDeliveries.filter(d => d.status === 'in_transit' || d.status === 'picked_up').length}
                  </p>
                </div>
                <Truck className="text-primary" size={32} />
              </div>
              <p className="text-xs text-blue-600 mt-2">2 arriving today</p>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-sm border border-border">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-foreground-secondary mb-1">Available Vehicles</p>
                  <p className="text-3xl font-bold text-foreground">
                    {displayVehicles.filter(v => v.is_available).length}
                  </p>
                </div>
                <Package className="text-accent" size={32} />
              </div>
              <p className="text-xs text-foreground-secondary mt-2">Ready for dispatch</p>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-sm border border-border">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-foreground-secondary mb-1">Completed Today</p>
                  <p className="text-3xl font-bold text-foreground">
                    {displayDeliveries.filter(d =>
                      d.status === 'delivered' &&
                      new Date(d.actual_delivery || d.created_at).toDateString() === new Date().toDateString()
                    ).length}
                  </p>
                </div>
                <CheckCircle className="text-green-600" size={32} />
              </div>
              <p className="text-xs text-green-600 mt-2">100% on time</p>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-sm border border-border">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-foreground-secondary mb-1">Average Rating</p>
                  <p className="text-3xl font-bold text-foreground">4.8</p>
                </div>
                <Star className="text-yellow-500" size={32} />
              </div>
              <p className="text-xs text-foreground-secondary mt-2">Based on 124 reviews</p>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
              {error}
            </div>
          )}

          {/* Tabs */}
          <div className="bg-white rounded-xl shadow-sm border border-border mb-8">
            <div className="border-b border-border">
              <nav className="flex space-x-8 px-6">
                <button
                  onClick={() => setActiveTab("deliveries")}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === "deliveries"
                      ? "border-primary text-primary"
                      : "border-transparent text-foreground-secondary hover:text-foreground"
                  }`}
                >
                  Active Deliveries
                </button>
                <button
                  onClick={() => setActiveTab("vehicles")}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === "vehicles"
                      ? "border-primary text-primary"
                      : "border-transparent text-foreground-secondary hover:text-foreground"
                  }`}
                >
                  Fleet Management
                </button>
              </nav>
            </div>

            <div className="p-6">
              {isLoading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
                  <p className="text-foreground-secondary">Loading delivery data...</p>
                </div>
              ) : activeTab === "deliveries" ? (
                <div className="space-y-6">
                  {displayDeliveries.map((delivery) => (
                    <div key={delivery.id} className="border border-border rounded-lg p-6 hover:shadow-md transition-smooth">
                      {/* Delivery Header */}
                      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-6">
                        <div>
                          <h3 className="text-lg font-bold text-foreground mb-1">
                            Delivery #{delivery.id}
                          </h3>
                          <p className="text-foreground-secondary">
                            Order #{delivery.order_id} • {delivery.vehicle_info}
                          </p>
                        </div>
                        <div className="flex items-center gap-3 mt-4 lg:mt-0">
                          {getStatusIcon(delivery.status)}
                          <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(delivery.status)}`}>
                            {delivery.status.replace('_', ' ').toUpperCase()}
                          </span>
                        </div>
                      </div>

                      {/* Route Info */}
                      <div className="grid md:grid-cols-2 gap-6 mb-6">
                        <div>
                          <div className="flex items-start gap-3 mb-4">
                            <MapPin className="text-green-600 mt-1" size={16} />
                            <div>
                              <p className="text-sm text-foreground-secondary">Pickup Location</p>
                              <p className="font-semibold text-foreground">{delivery.pickup_address}</p>
                            </div>
                          </div>
                          <div className="flex items-start gap-3">
                            <MapPin className="text-red-600 mt-1" size={16} />
                            <div>
                              <p className="text-sm text-foreground-secondary">Delivery Location</p>
                              <p className="font-semibold text-foreground">{delivery.delivery_address}</p>
                            </div>
                          </div>
                        </div>

                        <div>
                          <div className="mb-4">
                            <p className="text-sm text-foreground-secondary">Transporter</p>
                            <p className="font-semibold text-foreground">{delivery.transporter_name}</p>
                            <p className="text-sm text-foreground-secondary">
                              <Phone size={12} className="inline mr-1" />
                              {delivery.transporter_phone}
                            </p>
                          </div>
                          <div>
                            <p className="text-sm text-foreground-secondary">
                              {delivery.status === 'delivered' ? 'Delivered' : 'Estimated Delivery'}
                            </p>
                            <p className="font-semibold text-foreground">
                              {new Date(delivery.actual_delivery || delivery.estimated_delivery).toLocaleDateString()} at{' '}
                              {new Date(delivery.actual_delivery || delivery.estimated_delivery).toLocaleTimeString([], {
                                hour: '2-digit',
                                minute: '2-digit'
                              })}
                            </p>
                          </div>
                        </div>
                      </div>

                      {/* Tracking Timeline */}
                      <div className="mb-6">
                        <h4 className="font-semibold text-foreground mb-4">Tracking Updates</h4>
                        <div className="space-y-3">
                          {delivery.tracking_updates.slice().reverse().map((update, index) => (
                            <div key={update.id} className="flex items-start gap-3">
                              <div className={`w-3 h-3 rounded-full mt-1 ${
                                index === 0 ? 'bg-primary' : 'bg-gray-300'
                              }`} />
                              <div className="flex-1">
                                <div className="flex justify-between items-start">
                                  <div>
                                    <p className="font-semibold text-foreground">{update.location}</p>
                                    <p className="text-sm text-foreground-secondary capitalize">
                                      {update.status.replace('_', ' ')}
                                    </p>
                                    {update.notes && (
                                      <p className="text-sm text-foreground-secondary mt-1">{update.notes}</p>
                                    )}
                                  </div>
                                  <p className="text-sm text-foreground-secondary">
                                    {new Date(update.timestamp).toLocaleString()}
                                  </p>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="flex gap-3">
                        <Link
                          href={`/deliveries/${delivery.id}`}
                          className="inline-flex items-center gap-2 bg-primary text-white px-4 py-2 rounded-lg hover:bg-primary-dark transition-smooth"
                        >
                          <Eye size={16} />
                          Track Live
                        </Link>
                        <button className="inline-flex items-center gap-2 bg-background-secondary text-foreground px-4 py-2 rounded-lg hover:bg-border transition-smooth">
                          <Navigation size={16} />
                          Get Directions
                        </button>
                        <a
                          href={`tel:${delivery.transporter_phone}`}
                          className="inline-flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-smooth"
                        >
                          <Phone size={16} />
                          Call Driver
                        </a>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="space-y-4">
                  {displayVehicles.map((vehicle) => (
                    <div key={vehicle.id} className="border border-border rounded-lg p-6 hover:shadow-md transition-smooth">
                      <div className="flex justify-between items-start">
                        <div>
                          <h3 className="text-lg font-bold text-foreground mb-2">
                            {vehicle.license_plate}
                          </h3>
                          <div className="grid md:grid-cols-3 gap-4">
                            <div>
                              <p className="text-sm text-foreground-secondary">Vehicle Type</p>
                              <p className="font-semibold text-foreground capitalize">{vehicle.vehicle_type}</p>
                            </div>
                            <div>
                              <p className="text-sm text-foreground-secondary">Capacity</p>
                              <p className="font-semibold text-foreground">{vehicle.capacity}</p>
                            </div>
                            <div>
                              <p className="text-sm text-foreground-secondary">Owner</p>
                              <p className="font-semibold text-foreground">{vehicle.owner_name}</p>
                            </div>
                          </div>
                        </div>
                        <div className="text-right">
                          <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                            vehicle.is_available
                              ? 'bg-green-100 text-green-800'
                              : 'bg-red-100 text-red-800'
                          }`}>
                            {vehicle.is_available ? 'AVAILABLE' : 'IN USE'}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Logistics Features */}
          <div className="bg-white rounded-xl p-8 shadow-sm border border-border">
            <h2 className="text-2xl font-bold text-foreground mb-6">Logistics Features</h2>
            <div className="grid md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="bg-primary/10 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                  <Route className="text-primary" size={24} />
                </div>
                <h3 className="text-lg font-bold text-foreground mb-2">Route Optimization</h3>
                <p className="text-foreground-secondary">
                  AI-powered route planning to minimize delivery time and fuel costs while maximizing efficiency.
                </p>
              </div>
              <div className="text-center">
                <div className="bg-accent/10 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                  <Navigation className="text-accent" size={24} />
                </div>
                <h3 className="text-lg font-bold text-foreground mb-2">Real-time Tracking</h3>
                <p className="text-foreground-secondary">
                  Live GPS tracking for all deliveries with automated updates and notifications for customers.
                </p>
              </div>
              <div className="text-center">
                <div className="bg-green-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                  <Truck className="text-green-600" size={24} />
                </div>
                <h3 className="text-lg font-bold text-foreground mb-2">Fleet Management</h3>
                <p className="text-foreground-secondary">
                  Comprehensive vehicle management with maintenance scheduling, driver assignments, and performance analytics.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}

export default function DeliveriesPage() {
  return (
    <ProtectedRoute>
      <DeliveriesContent />
    </ProtectedRoute>
  )
}