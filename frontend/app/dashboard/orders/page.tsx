"use client"

import { ProtectedRoute } from "@/components/protected-route"
import { DashboardLayout } from "@/components/dashboard-layout"
import { useAuth } from "@/lib/auth-context"
import { ArrowLeft } from "lucide-react"
import Link from "next/link"

const allOrders = [
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
  {
    id: "ORD004",
    buyer: "Hotel Group",
    product: "Tea Leaves",
    amount: 45000,
    status: "Completed",
    date: "2024-01-12",
  },
  {
    id: "ORD005",
    buyer: "Cafe Chain",
    product: "Coffee Beans",
    amount: 15000,
    status: "Completed",
    date: "2024-01-11",
  },
]

function OrdersContent() {
  const { user } = useAuth()

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-green-900 mb-2">All Orders</h1>
          <p className="text-green-600">Manage and track all your orders</p>
        </div>
        <Link href="/dashboard" className="flex items-center gap-2 text-green-600 hover:text-green-700 font-medium">
          <ArrowLeft size={18} />
          Back to Dashboard
        </Link>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-green-100 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-green-100 bg-green-50">
                <th className="text-left py-4 px-6 font-semibold text-green-900">Order ID</th>
                <th className="text-left py-4 px-6 font-semibold text-green-900">Buyer</th>
                <th className="text-left py-4 px-6 font-semibold text-green-900">Product</th>
                <th className="text-left py-4 px-6 font-semibold text-green-900">Amount</th>
                <th className="text-left py-4 px-6 font-semibold text-green-900">Status</th>
                <th className="text-left py-4 px-6 font-semibold text-green-900">Date</th>
                <th className="text-left py-4 px-6 font-semibold text-green-900">Action</th>
              </tr>
            </thead>
            <tbody>
              {allOrders.map((order) => (
                <tr
                  key={order.id}
                  className="border-b border-green-50 hover:bg-green-50 transition-colors"
                >
                  <td className="py-4 px-6 font-medium text-green-900">{order.id}</td>
                  <td className="py-4 px-6 text-gray-700">{order.buyer}</td>
                  <td className="py-4 px-6 text-gray-900">{order.product}</td>
                  <td className="py-4 px-6 font-semibold text-green-600">KES {order.amount.toLocaleString()}</td>
                  <td className="py-4 px-6">
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        order.status === "Completed"
                          ? "bg-green-100 text-green-800"
                          : order.status === "In Transit"
                            ? "bg-orange-100 text-orange-800"
                            : "bg-yellow-100 text-yellow-800"
                      }`}
                    >
                      {order.status}
                    </span>
                  </td>
                  <td className="py-4 px-6 text-gray-600">{order.date}</td>
                  <td className="py-4 px-6">
                    <Link
                      href={`/dashboard/orders/${order.id}`}
                      className="text-green-600 hover:text-green-700 font-medium"
                    >
                      View
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default function OrdersPage() {
  return (
    <ProtectedRoute>
      <DashboardLayout>
        <OrdersContent />
      </DashboardLayout>
    </ProtectedRoute>
  )
}
