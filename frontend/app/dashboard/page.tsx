"use client"

import { ProtectedRoute } from "@/components/protected-route"
import { useAuth } from "@/lib/auth-context"
import { useState } from "react"
import Navbar from "@/components/navbar"
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts"
import { TrendingUp, Package, DollarSign, Plus, Settings, ShoppingCart } from "lucide-react"
import Link from "next/link"

const salesData = [
  { month: "Jan", sales: 4000, revenue: 2400 },
  { month: "Feb", sales: 3000, revenue: 1398 },
  { month: "Mar", sales: 2000, revenue: 9800 },
  { month: "Apr", sales: 2780, revenue: 3908 },
  { month: "May", sales: 1890, revenue: 4800 },
  { month: "Jun", sales: 2390, revenue: 3800 },
]

const farmerOrders = [
  {
    id: "ORD001",
    buyer: "Nairobi Restaurant",
    product: "Bananas",
    amount: 12500,
    status: "Completed",
    date: "2024-01-15",
  },
  {
    id: "ORD002",
    buyer: "Supermarket Chain",
    product: "Avocados",
    amount: 28000,
    status: "In Transit",
    date: "2024-01-14",
  },
  { id: "ORD003", buyer: "Juice Factory", product: "Oranges", amount: 8500, status: "Pending", date: "2024-01-13" },
  { id: "ORD004", buyer: "Hotel Group", product: "Tea Leaves", amount: 45000, status: "Completed", date: "2024-01-12" },
]

const buyerOrders = [
  {
    id: "BUY001",
    seller: "Jane Moraa",
    product: "Fresh Bananas",
    amount: 12500,
    status: "Delivered",
    date: "2024-01-15",
  },
  {
    id: "BUY002",
    seller: "David Kipchoge",
    product: "Organic Avocados",
    amount: 28000,
    status: "In Transit",
    date: "2024-01-14",
  },
  {
    id: "BUY003",
    seller: "Esther Nyaboke",
    product: "Premium Tea",
    amount: 8500,
    status: "Processing",
    date: "2024-01-13",
  },
]

function DashboardContent() {
  const { user } = useAuth()
  const [activeTab, setActiveTab] = useState("overview")

  const isFarmer = user?.role === "farmer"
  const orders = isFarmer ? farmerOrders : buyerOrders

  return (
    <main className="min-h-screen bg-background-secondary">
      <Navbar />

      <div className="pt-32 pb-12 px-6">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="flex justify-between items-start mb-8">
            <div>
              <h1 className="text-4xl font-bold text-foreground mb-2">
                {isFarmer ? "Farmer Dashboard" : "Buyer Dashboard"}
              </h1>
              <p className="text-foreground-secondary">Welcome back, {user?.name}</p>
            </div>
            <Link
              href="/dashboard/settings"
              className="flex items-center gap-2 bg-primary text-white px-4 py-2 rounded-lg hover:bg-primary-dark transition-smooth"
            >
              <Settings size={18} />
              Settings
            </Link>
          </div>

          {/* KPI Cards */}
          <div className="grid md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-xl p-6 shadow-sm border border-border">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-foreground-secondary mb-1">{isFarmer ? "Total Revenue" : "Total Spent"}</p>
                  <p className="text-3xl font-bold text-foreground">KES 156,400</p>
                </div>
                <DollarSign className="text-primary" size={32} />
              </div>
              <p className="text-xs text-primary mt-2 flex items-center gap-1">
                <TrendingUp size={14} /> +12% this month
              </p>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-sm border border-border">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-foreground-secondary mb-1">
                    {isFarmer ? "Active Listings" : "Saved Items"}
                  </p>
                  <p className="text-3xl font-bold text-foreground">{isFarmer ? "8" : "12"}</p>
                </div>
                <Package className="text-accent" size={32} />
              </div>
              <p className="text-xs text-foreground-secondary mt-2">
                {isFarmer ? "3 pending approval" : "Ready to order"}
              </p>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-sm border border-border">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-foreground-secondary mb-1">
                    {isFarmer ? "Completed Orders" : "Orders Placed"}
                  </p>
                  <p className="text-3xl font-bold text-foreground">24</p>
                </div>
                <ShoppingCart className="text-primary" size={32} />
              </div>
              <p className="text-xs text-foreground-secondary mt-2">98% success rate</p>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-sm border border-border">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-foreground-secondary mb-1">Rating</p>
                  <p className="text-3xl font-bold text-foreground">4.8/5</p>
                </div>
                <div className="text-accent text-2xl">★</div>
              </div>
              <p className="text-xs text-foreground-secondary mt-2">Based on 156 reviews</p>
            </div>
          </div>

          {/* Charts */}
          <div className="grid lg:grid-cols-2 gap-6 mb-8">
            {/* Sales Chart */}
            <div className="bg-white rounded-xl p-6 shadow-sm border border-border">
              <h3 className="text-lg font-bold text-foreground mb-4">{isFarmer ? "Sales Trend" : "Purchase Trend"}</h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={salesData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="sales" stroke="#10b981" strokeWidth={2} />
                  <Line type="monotone" dataKey="revenue" stroke="#f97316" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Revenue Chart */}
            <div className="bg-white rounded-xl p-6 shadow-sm border border-border">
              <h3 className="text-lg font-bold text-foreground mb-4">
                {isFarmer ? "Revenue by Product" : "Spending by Category"}
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={salesData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="revenue" fill="#10b981" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Recent Orders */}
          <div className="bg-white rounded-xl p-6 shadow-sm border border-border">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-lg font-bold text-foreground">{isFarmer ? "Recent Orders" : "Recent Purchases"}</h3>
              <Link href="/dashboard/orders" className="text-primary hover:text-primary-dark font-medium">
                View All
              </Link>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border">
                    <th className="text-left py-3 px-4 font-semibold text-foreground">Order ID</th>
                    <th className="text-left py-3 px-4 font-semibold text-foreground">
                      {isFarmer ? "Buyer" : "Seller"}
                    </th>
                    <th className="text-left py-3 px-4 font-semibold text-foreground">Product</th>
                    <th className="text-left py-3 px-4 font-semibold text-foreground">Amount</th>
                    <th className="text-left py-3 px-4 font-semibold text-foreground">Status</th>
                    <th className="text-left py-3 px-4 font-semibold text-foreground">Date</th>
                  </tr>
                </thead>
                <tbody>
                  {orders.map((order) => (
                    <tr
                      key={order.id}
                      className="border-b border-border hover:bg-background-secondary transition-smooth"
                    >
                      <td className="py-3 px-4 font-medium text-foreground">{order.id}</td>
                      <td className="py-3 px-4 text-foreground-secondary">{isFarmer ? order.buyer : order.seller}</td>
                      <td className="py-3 px-4 text-foreground">{order.product}</td>
                      <td className="py-3 px-4 font-semibold text-primary">KES {order.amount}</td>
                      <td className="py-3 px-4">
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-semibold ${
                            order.status === "Completed" || order.status === "Delivered"
                              ? "bg-primary/10 text-primary"
                              : order.status === "In Transit"
                                ? "bg-accent/10 text-accent"
                                : "bg-yellow-100 text-yellow-700"
                          }`}
                        >
                          {order.status}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-foreground-secondary">{order.date}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="mt-8 flex gap-4">
            {isFarmer ? (
              <>
                <Link
                  href="/dashboard/create-listing"
                  className="flex items-center gap-2 bg-primary text-white px-6 py-3 rounded-lg hover:bg-primary-dark transition-smooth font-semibold"
                >
                  <Plus size={20} />
                  Create New Listing
                </Link>
                <Link
                  href="/dashboard/profile"
                  className="flex items-center gap-2 bg-background-secondary text-foreground px-6 py-3 rounded-lg hover:bg-border transition-smooth font-semibold"
                >
                  Edit Profile
                </Link>
              </>
            ) : (
              <>
                <Link
                  href="/marketplace"
                  className="flex items-center gap-2 bg-primary text-white px-6 py-3 rounded-lg hover:bg-primary-dark transition-smooth font-semibold"
                >
                  <Plus size={20} />
                  Browse Products
                </Link>
                <Link
                  href="/dashboard/profile"
                  className="flex items-center gap-2 bg-background-secondary text-foreground px-6 py-3 rounded-lg hover:bg-border transition-smooth font-semibold"
                >
                  Edit Profile
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </main>
  )
}

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  )
}
