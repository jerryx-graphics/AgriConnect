"use client"

import { ProtectedRoute } from "@/components/protected-route"
import { DashboardLayout } from "@/components/dashboard-layout"
import { useAuth } from "@/lib/auth-context"
import { useState, useEffect } from "react"
import { apiClient } from "@/lib/api"
import {
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area
} from "recharts"
import {
  TrendingUp,
  Package,
  DollarSign,
  Plus,
  ShoppingCart,
  Users,
  Eye,
  Star,
  Calendar,
  ArrowUpRight,
  Activity,
  Target,
  Clock,
  User
} from "lucide-react"
import Link from "next/link"


function DashboardContent() {
  const { user } = useAuth()
  const [orders, setOrders] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [dashboardStats, setDashboardStats] = useState({
    totalRevenue: 0,
    activeListings: 0,
    completedOrders: 0,
    rating: 4.8,
    totalViews: 0,
    pendingOrders: 0,
    monthlyGrowth: 12.5
  })

  const isFarmer = user?.role === "farmer"
  const isBuyer = user?.role === "buyer"

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [ordersResponse, productsResponse] = await Promise.all([
          apiClient.getOrders().catch(() => ({ data: { results: [] } })),
          isFarmer ? apiClient.getMyProducts().catch(() => ({ data: { results: [] } })) : Promise.resolve({ data: { results: [] } })
        ])

        const ordersData = ordersResponse.data?.results || ordersResponse.data || []
        const productsData = productsResponse.data?.results || productsResponse.data || []

        setOrders(ordersData)

        // Calculate stats from real data
        const completedOrders = ordersData.filter((order: any) =>
          order.status === 'COMPLETED' || order.status === 'DELIVERED'
        )
        const pendingOrders = ordersData.filter((order: any) =>
          order.status === 'PENDING' || order.status === 'PROCESSING'
        )

        const totalRevenue = completedOrders.reduce((sum: number, order: any) =>
          sum + (order.total_amount || 0), 0
        )

        const totalViews = productsData.reduce((sum: number, product: any) =>
          sum + (product.view_count || 0), 0
        )

        setDashboardStats({
          totalRevenue,
          activeListings: productsData.length,
          completedOrders: completedOrders.length,
          pendingOrders: pendingOrders.length,
          rating: 4.8,
          totalViews,
          monthlyGrowth: 12.5
        })
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error)
        // Set mock data on error
        setDashboardStats({
          totalRevenue: isFarmer ? 125000 : 45000,
          activeListings: isFarmer ? 8 : 12,
          completedOrders: 24,
          pendingOrders: 3,
          rating: 4.8,
          totalViews: 1250,
          monthlyGrowth: 12.5
        })
      } finally {
        setIsLoading(false)
      }
    }

    if (user) {
      fetchDashboardData()
    }
  }, [user, isFarmer])

  const salesData = [
    { month: "Jan", sales: 4000, revenue: 24000, orders: 12 },
    { month: "Feb", sales: 3000, revenue: 18000, orders: 8 },
    { month: "Mar", sales: 5000, revenue: 32000, orders: 15 },
    { month: "Apr", sales: 2780, revenue: 28000, orders: 10 },
    { month: "May", sales: 4890, revenue: 35000, orders: 18 },
    { month: "Jun", sales: 6390, revenue: 42000, orders: 22 },
  ]

  const categoryData = [
    { name: 'Vegetables', value: 35, color: '#22c55e' },
    { name: 'Fruits', value: 28, color: '#eab308' },
    { name: 'Grains', value: 20, color: '#f97316' },
    { name: 'Dairy', value: 17, color: '#3b82f6' }
  ]


  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between mb-8">
        <div className="mb-4 lg:mb-0">
          <h1 className="text-3xl lg:text-4xl font-bold text-green-900 mb-2">
            {isFarmer ? "Farmer Dashboard" : isBuyer ? "Buyer Dashboard" : "Dashboard"}
          </h1>
          <p className="text-green-600 text-lg">Welcome back, {user?.first_name} {user?.last_name}</p>
        </div>
        <div className="flex items-center space-x-3">
          <div className="text-sm text-green-600 bg-green-50 px-4 py-2 rounded-lg">
            <Calendar size={16} className="inline mr-2" />
            {new Date().toLocaleDateString('en-US', {
              weekday: 'long',
              year: 'numeric',
              month: 'long',
              day: 'numeric'
            })}
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6 mb-8">
        <div className="bg-white rounded-xl p-6 shadow-sm border border-green-100 hover:shadow-md transition-shadow">
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              <p className="text-sm font-medium text-green-600 mb-2">{isFarmer ? "Total Revenue" : "Total Spent"}</p>
              <p className="text-2xl lg:text-3xl font-bold text-green-900">
                {isLoading ? "..." : `KES ${dashboardStats.totalRevenue.toLocaleString()}`}
              </p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center flex-shrink-0">
              <DollarSign className="text-green-600" size={20} />
            </div>
          </div>
          <div className="flex items-center text-sm">
            <ArrowUpRight size={16} className="text-green-500 mr-1" />
            <span className="text-green-500 font-medium">+{dashboardStats.monthlyGrowth}%</span>
            <span className="text-green-600 ml-1">this month</span>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm border border-green-100 hover:shadow-md transition-shadow">
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              <p className="text-sm font-medium text-green-600 mb-2">
                {isFarmer ? "Active Products" : "Saved Items"}
              </p>
              <p className="text-2xl lg:text-3xl font-bold text-green-900">
                {isLoading ? "..." : dashboardStats.activeListings}
              </p>
            </div>
            <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center flex-shrink-0">
              <Package className="text-orange-600" size={20} />
            </div>
          </div>
          <div className="flex items-center text-sm">
            <Activity size={16} className="text-orange-500 mr-1" />
            <span className="text-green-600">{dashboardStats.pendingOrders} pending orders</span>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm border border-green-100 hover:shadow-md transition-shadow">
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              <p className="text-sm font-medium text-green-600 mb-2">
                {isFarmer ? "Total Orders" : "Orders Placed"}
              </p>
              <p className="text-2xl lg:text-3xl font-bold text-green-900">
                {isLoading ? "..." : dashboardStats.completedOrders}
              </p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
              <ShoppingCart className="text-blue-600" size={20} />
            </div>
          </div>
          <div className="flex items-center text-sm">
            <Target size={16} className="text-blue-500 mr-1" />
            <span className="text-green-600">98% success rate</span>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm border border-green-100 hover:shadow-md transition-shadow">
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              <p className="text-sm font-medium text-green-600 mb-2">{isFarmer ? "Avg Rating" : "Total Views"}</p>
              <p className="text-2xl lg:text-3xl font-bold text-green-900">
                {isLoading ? "..." : isFarmer ? `${dashboardStats.rating}/5` : dashboardStats.totalViews.toLocaleString()}
              </p>
            </div>
            <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center flex-shrink-0">
              {isFarmer ? (
                <Star className="text-yellow-600" size={20} />
              ) : (
                <Eye className="text-yellow-600" size={20} />
              )}
            </div>
          </div>
          <div className="flex items-center text-sm">
            <Users size={16} className="text-yellow-500 mr-1" />
            <span className="text-green-600">{isFarmer ? "Based on 156 reviews" : "This month"}</span>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Performance Chart */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-green-100">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-green-900">
              {isFarmer ? "Sales Performance" : "Purchase Activity"}
            </h3>
            <div className="text-sm text-green-600">Last 6 months</div>
          </div>
          <ResponsiveContainer width="100%" height={280}>
            <AreaChart data={salesData}>
              <defs>
                <linearGradient id="salesGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#22c55e" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="revenueGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#f97316" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#f97316" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="month" stroke="#6b7280" />
              <YAxis stroke="#6b7280" />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                }}
              />
              <Legend />
              <Area
                type="monotone"
                dataKey="revenue"
                stroke="#f97316"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#revenueGradient)"
                name="Revenue (KES)"
              />
              <Area
                type="monotone"
                dataKey="sales"
                stroke="#22c55e"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#salesGradient)"
                name="Sales Volume"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Category/Performance Distribution */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-green-100">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-green-900">
              {isFarmer ? "Product Categories" : "Purchase Categories"}
            </h3>
          </div>
          <div className="flex flex-col lg:flex-row items-center">
            <div className="w-full lg:w-1/2">
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie
                    data={categoryData}
                    cx="50%"
                    cy="50%"
                    innerRadius={40}
                    outerRadius={80}
                    dataKey="value"
                  >
                    {categoryData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(value) => [`${value}%`, 'Percentage']}
                    contentStyle={{
                      backgroundColor: 'white',
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px'
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="w-full lg:w-1/2 mt-4 lg:mt-0">
              <div className="space-y-3">
                {categoryData.map((item, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <div
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: item.color }}
                      ></div>
                      <span className="text-sm text-green-800">{item.name}</span>
                    </div>
                    <span className="text-sm font-medium text-green-900">{item.value}%</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-xl p-6 shadow-sm border border-green-100">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6">
          <h3 className="text-lg font-bold text-green-900">
            {isFarmer ? "Recent Orders" : "Recent Activity"}
          </h3>
          <Link
            href="/dashboard/orders"
            className="text-green-600 hover:text-green-700 font-medium flex items-center mt-2 sm:mt-0"
          >
            View All
            <ArrowUpRight size={16} className="ml-1" />
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-green-100">
                <th className="text-left py-3 px-4 font-semibold text-green-900">Order ID</th>
                <th className="text-left py-3 px-4 font-semibold text-green-900">
                  {isFarmer ? "Customer" : "Seller"}
                </th>
                <th className="text-left py-3 px-4 font-semibold text-green-900">Product</th>
                <th className="text-left py-3 px-4 font-semibold text-green-900">Amount</th>
                <th className="text-left py-3 px-4 font-semibold text-green-900">Status</th>
                <th className="text-left py-3 px-4 font-semibold text-green-900">Date</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-green-600">
                    <div className="flex items-center justify-center space-x-2">
                      <Clock size={16} className="animate-spin" />
                      <span>Loading orders...</span>
                    </div>
                  </td>
                </tr>
              ) : orders.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-green-600">
                    <div className="flex flex-col items-center space-y-2">
                      <ShoppingCart size={32} className="text-green-400" />
                      <span>No orders found</span>
                      <Link
                        href="/dashboard/marketplace"
                        className="text-green-600 hover:text-green-700 font-medium"
                      >
                        Browse Products
                      </Link>
                    </div>
                  </td>
                </tr>
              ) : (
                orders.slice(0, 5).map((order: any, index: number) => (
                  <tr
                    key={order.id || index}
                    className="border-b border-green-50 hover:bg-green-50 transition-colors"
                  >
                    <td className="py-4 px-4 font-medium text-green-900">
                      #{(order.id || `ORD${index + 1000}`).toString().slice(-8)}
                    </td>
                    <td className="py-4 px-4 text-green-700">
                      {isFarmer
                        ? order.buyer?.first_name || order.buyer_name || "John Doe"
                        : order.seller?.first_name || order.seller_name || "AgriStore"
                      }
                    </td>
                    <td className="py-4 px-4 text-green-800">
                      {order.items?.map((item: any) => item.product?.name).join(", ")
                       || order.product_name
                       || ["Fresh Tomatoes", "Maize", "Cabbage", "Carrots", "Potatoes"][index] || "Product"}
                    </td>
                    <td className="py-4 px-4 font-semibold text-green-900">
                      KES {(order.total_amount || (Math.random() * 5000 + 1000)).toLocaleString()}
                    </td>
                    <td className="py-4 px-4">
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-semibold ${
                          (order.status === "COMPLETED" || order.status === "DELIVERED")
                            ? "bg-green-100 text-green-800"
                            : (order.status === "IN_TRANSIT" || order.status === "SHIPPED")
                              ? "bg-orange-100 text-orange-800"
                              : "bg-yellow-100 text-yellow-800"
                        }`}
                      >
                        {(order.status?.replace('_', ' ') || ['PENDING', 'IN_TRANSIT', 'COMPLETED'][index % 3]).toUpperCase()}
                      </span>
                    </td>
                    <td className="py-4 px-4 text-green-600">
                      {new Date(order.created_at || Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toLocaleDateString()}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {isFarmer ? (
          <>
            <Link
              href="/dashboard/create-listing"
              className="flex items-center justify-center gap-3 bg-green-600 text-white p-4 rounded-xl hover:bg-green-700 transition-colors shadow-sm group"
            >
              <Plus size={20} className="group-hover:scale-110 transition-transform" />
              <span className="font-semibold">Add New Product</span>
            </Link>
            <Link
              href="/dashboard/analytics"
              className="flex items-center justify-center gap-3 bg-orange-600 text-white p-4 rounded-xl hover:bg-orange-700 transition-colors shadow-sm group"
            >
              <TrendingUp size={20} className="group-hover:scale-110 transition-transform" />
              <span className="font-semibold">View Analytics</span>
            </Link>
            <Link
              href="/dashboard/marketplace"
              className="flex items-center justify-center gap-3 bg-blue-600 text-white p-4 rounded-xl hover:bg-blue-700 transition-colors shadow-sm group"
            >
              <ShoppingCart size={20} className="group-hover:scale-110 transition-transform" />
              <span className="font-semibold">Browse Market</span>
            </Link>
          </>
        ) : (
          <>
            <Link
              href="/dashboard/marketplace"
              className="flex items-center justify-center gap-3 bg-green-600 text-white p-4 rounded-xl hover:bg-green-700 transition-colors shadow-sm group"
            >
              <ShoppingCart size={20} className="group-hover:scale-110 transition-transform" />
              <span className="font-semibold">Browse Products</span>
            </Link>
            <Link
              href="/dashboard/orders"
              className="flex items-center justify-center gap-3 bg-orange-600 text-white p-4 rounded-xl hover:bg-orange-700 transition-colors shadow-sm group"
            >
              <Package size={20} className="group-hover:scale-110 transition-transform" />
              <span className="font-semibold">My Orders</span>
            </Link>
            <Link
              href="/dashboard/profile"
              className="flex items-center justify-center gap-3 bg-blue-600 text-white p-4 rounded-xl hover:bg-blue-700 transition-colors shadow-sm group"
            >
              <User size={20} className="group-hover:scale-110 transition-transform" />
              <span className="font-semibold">Edit Profile</span>
            </Link>
          </>
        )}
      </div>
    </div>
  )
}

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <DashboardLayout>
        <DashboardContent />
      </DashboardLayout>
    </ProtectedRoute>
  )
}
