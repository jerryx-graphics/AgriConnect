"use client"

import { useState, useEffect } from "react"
import { ProtectedRoute } from "@/components/protected-route"
import { DashboardLayout } from "@/components/dashboard-layout"
import { useAuth } from "@/lib/auth-context"
import {
  TrendingUp,
  TrendingDown,
  Eye,
  ShoppingCart,
  DollarSign,
  Package,
  Users,
  Calendar,
  Download,
  Filter,
  BarChart3,
  PieChart,
  ArrowUp,
  ArrowDown
} from "lucide-react"
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from "recharts"

const COLORS = ['#16a34a', '#eab308', '#f97316', '#3b82f6', '#8b5cf6']

function AnalyticsContent() {
  const { user } = useAuth()
  const [timeRange, setTimeRange] = useState("30")
  const [isLoading, setIsLoading] = useState(true)
  const [selectedMetric, setSelectedMetric] = useState("revenue")

  useEffect(() => {
    // Simulate loading
    setTimeout(() => setIsLoading(false), 1000)
  }, [timeRange])

  // Mock data for charts
  const revenueData = [
    { month: 'Jan', revenue: 45000, orders: 23, views: 1200 },
    { month: 'Feb', revenue: 52000, orders: 31, views: 1450 },
    { month: 'Mar', revenue: 48000, orders: 28, views: 1380 },
    { month: 'Apr', revenue: 61000, orders: 35, views: 1620 },
    { month: 'May', revenue: 68000, orders: 42, views: 1890 },
    { month: 'Jun', revenue: 74000, orders: 48, views: 2100 },
  ]

  const productPerformance = [
    { name: 'Bananas', sales: 45, revenue: 28000, profit: 8400 },
    { name: 'Avocados', sales: 32, revenue: 42000, profit: 15400 },
    { name: 'Tea Leaves', sales: 18, revenue: 35000, profit: 21000 },
    { name: 'Coffee Beans', sales: 25, revenue: 31000, profit: 12400 },
    { name: 'Maize', sales: 38, revenue: 22000, profit: 6600 },
  ]

  const customerInsights = [
    { segment: 'Restaurants', value: 35, color: '#16a34a' },
    { segment: 'Retailers', value: 28, color: '#eab308' },
    { segment: 'Exporters', value: 20, color: '#f97316' },
    { segment: 'Direct Consumers', value: 17, color: '#3b82f6' },
  ]

  const topMetrics = [
    {
      title: "Total Revenue",
      value: "KES 308,000",
      change: "+15.3%",
      isPositive: true,
      icon: DollarSign,
      color: "text-green-600"
    },
    {
      title: "Total Orders",
      value: "207",
      change: "+8.7%",
      isPositive: true,
      icon: ShoppingCart,
      color: "text-blue-600"
    },
    {
      title: "Product Views",
      value: "9,640",
      change: "+22.1%",
      isPositive: true,
      icon: Eye,
      color: "text-purple-600"
    },
    {
      title: "Conversion Rate",
      value: "2.14%",
      change: "-0.3%",
      isPositive: false,
      icon: TrendingUp,
      color: "text-orange-600"
    }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-green-900 mb-2">Analytics Dashboard</h1>
          <p className="text-green-600">Track your farm's performance and growth</p>
        </div>
        <div className="flex items-center gap-3 mt-4 lg:mt-0">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="px-4 py-2 border-2 border-green-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 bg-white"
          >
            <option value="7">Last 7 days</option>
            <option value="30">Last 30 days</option>
            <option value="90">Last 3 months</option>
            <option value="365">Last year</option>
          </select>
          <button className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-colors">
            <Download size={16} />
            Export
          </button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {topMetrics.map((metric, index) => (
          <div key={index} className="bg-white rounded-xl p-6 shadow-sm border border-green-100">
            <div className="flex items-center justify-between mb-4">
              <div className={`w-12 h-12 ${metric.color === 'text-green-600' ? 'bg-green-100' :
                metric.color === 'text-blue-600' ? 'bg-blue-100' :
                metric.color === 'text-purple-600' ? 'bg-purple-100' : 'bg-orange-100'}
                rounded-lg flex items-center justify-center`}>
                <metric.icon className={metric.color} size={24} />
              </div>
              <div className={`flex items-center gap-1 ${metric.isPositive ? 'text-green-600' : 'text-red-600'}`}>
                {metric.isPositive ? <ArrowUp size={16} /> : <ArrowDown size={16} />}
                <span className="text-sm font-medium">{metric.change}</span>
              </div>
            </div>
            <h3 className="text-sm font-medium text-gray-600 mb-1">{metric.title}</h3>
            <p className="text-2xl font-bold text-gray-900">{metric.value}</p>
          </div>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Revenue Trend */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-green-100">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-bold text-green-900">Revenue Trend</h3>
            <div className="flex items-center gap-2">
              <select
                value={selectedMetric}
                onChange={(e) => setSelectedMetric(e.target.value)}
                className="text-sm border border-gray-300 rounded px-2 py-1"
              >
                <option value="revenue">Revenue</option>
                <option value="orders">Orders</option>
                <option value="views">Views</option>
              </select>
            </div>
          </div>
          {isLoading ? (
            <div className="h-64 flex items-center justify-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={280}>
              <AreaChart data={revenueData}>
                <defs>
                  <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#16a34a" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#16a34a" stopOpacity={0}/>
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
                <Area
                  type="monotone"
                  dataKey={selectedMetric}
                  stroke="#16a34a"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#colorRevenue)"
                />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Customer Segments */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-green-100">
          <h3 className="text-lg font-bold text-green-900 mb-6">Customer Segments</h3>
          {isLoading ? (
            <div className="h-64 flex items-center justify-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
            </div>
          ) : (
            <div className="flex items-center">
              <div className="w-1/2">
                <ResponsiveContainer width="100%" height={200}>
                  <RechartsPieChart>
                    <Pie
                      data={customerInsights}
                      cx="50%"
                      cy="50%"
                      innerRadius={40}
                      outerRadius={80}
                      dataKey="value"
                    >
                      {customerInsights.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => [`${value}%`, 'Share']} />
                  </RechartsPieChart>
                </ResponsiveContainer>
              </div>
              <div className="w-1/2 space-y-3">
                {customerInsights.map((item, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: item.color }}
                      />
                      <span className="text-sm text-gray-700">{item.segment}</span>
                    </div>
                    <span className="text-sm font-semibold text-gray-900">{item.value}%</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Product Performance */}
      <div className="bg-white rounded-xl p-6 shadow-sm border border-green-100">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-bold text-green-900">Product Performance</h3>
          <div className="flex items-center gap-2">
            <Filter size={16} className="text-gray-600" />
            <select className="text-sm border border-gray-300 rounded px-2 py-1">
              <option>All Products</option>
              <option>Top Performing</option>
              <option>Low Performing</option>
            </select>
          </div>
        </div>
        {isLoading ? (
          <div className="h-64 flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={productPerformance}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="name" stroke="#6b7280" />
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
              <Bar dataKey="revenue" fill="#16a34a" name="Revenue (KES)" />
              <Bar dataKey="profit" fill="#eab308" name="Profit (KES)" />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Performance Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl p-6 shadow-sm border border-green-100">
          <h3 className="text-lg font-bold text-green-900 mb-4">Performance Insights</h3>
          <div className="space-y-4">
            <div className="flex items-start gap-3 p-4 bg-green-50 rounded-lg">
              <TrendingUp className="text-green-600 mt-1" size={20} />
              <div>
                <h4 className="font-semibold text-green-900">Strong Growth</h4>
                <p className="text-sm text-green-700">Your revenue increased by 23% compared to last month. Avocados are your top performer.</p>
              </div>
            </div>
            <div className="flex items-start gap-3 p-4 bg-yellow-50 rounded-lg">
              <BarChart3 className="text-yellow-600 mt-1" size={20} />
              <div>
                <h4 className="font-semibold text-yellow-900">Optimization Opportunity</h4>
                <p className="text-sm text-yellow-700">Consider increasing your maize inventory as demand is growing by 15% weekly.</p>
              </div>
            </div>
            <div className="flex items-start gap-3 p-4 bg-blue-50 rounded-lg">
              <Users className="text-blue-600 mt-1" size={20} />
              <div>
                <h4 className="font-semibold text-blue-900">Customer Growth</h4>
                <p className="text-sm text-blue-700">You gained 12 new customers this month, mainly from the restaurant segment.</p>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm border border-green-100">
          <h3 className="text-lg font-bold text-green-900 mb-4">Quick Actions</h3>
          <div className="space-y-3">
            <button className="w-full flex items-center gap-3 p-4 border-2 border-green-200 rounded-lg hover:bg-green-50 transition-colors text-left">
              <Package className="text-green-600" size={20} />
              <div>
                <h4 className="font-semibold text-green-900">Update Inventory</h4>
                <p className="text-sm text-green-600">Manage your product quantities</p>
              </div>
            </button>
            <button className="w-full flex items-center gap-3 p-4 border-2 border-green-200 rounded-lg hover:bg-green-50 transition-colors text-left">
              <DollarSign className="text-green-600" size={20} />
              <div>
                <h4 className="font-semibold text-green-900">Adjust Pricing</h4>
                <p className="text-sm text-green-600">Optimize your product prices</p>
              </div>
            </button>
            <button className="w-full flex items-center gap-3 p-4 border-2 border-green-200 rounded-lg hover:bg-green-50 transition-colors text-left">
              <TrendingUp className="text-green-600" size={20} />
              <div>
                <h4 className="font-semibold text-green-900">View Insights</h4>
                <p className="text-sm text-green-600">Get AI-powered recommendations</p>
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function AnalyticsPage() {
  return (
    <ProtectedRoute>
      <DashboardLayout>
        <AnalyticsContent />
      </DashboardLayout>
    </ProtectedRoute>
  )
}