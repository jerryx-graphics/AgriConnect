"use client"

import { ProtectedRoute } from "@/components/protected-route"
import { useAuth } from "@/lib/auth-context"
import Navbar from "@/components/navbar"
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
    <main className="min-h-screen bg-background-secondary">
      <Navbar />

      <div className="pt-32 pb-12 px-6">
        <div className="max-w-6xl mx-auto">
          <Link href="/dashboard" className="flex items-center gap-2 text-primary hover:text-primary-dark mb-6">
            <ArrowLeft size={20} />
            Back to Dashboard
          </Link>

          <h1 className="text-4xl font-bold text-foreground mb-2">All Orders</h1>
          <p className="text-foreground-secondary mb-8">Manage and track all your orders</p>

          <div className="bg-white rounded-xl shadow-sm border border-border overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border bg-background-secondary">
                    <th className="text-left py-4 px-6 font-semibold text-foreground">Order ID</th>
                    <th className="text-left py-4 px-6 font-semibold text-foreground">Buyer</th>
                    <th className="text-left py-4 px-6 font-semibold text-foreground">Product</th>
                    <th className="text-left py-4 px-6 font-semibold text-foreground">Amount</th>
                    <th className="text-left py-4 px-6 font-semibold text-foreground">Status</th>
                    <th className="text-left py-4 px-6 font-semibold text-foreground">Date</th>
                    <th className="text-left py-4 px-6 font-semibold text-foreground">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {allOrders.map((order) => (
                    <tr
                      key={order.id}
                      className="border-b border-border hover:bg-background-secondary transition-smooth"
                    >
                      <td className="py-4 px-6 font-medium text-foreground">{order.id}</td>
                      <td className="py-4 px-6 text-foreground-secondary">{order.buyer}</td>
                      <td className="py-4 px-6 text-foreground">{order.product}</td>
                      <td className="py-4 px-6 font-semibold text-primary">KES {order.amount}</td>
                      <td className="py-4 px-6">
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-semibold ${
                            order.status === "Completed"
                              ? "bg-primary/10 text-primary"
                              : order.status === "In Transit"
                                ? "bg-accent/10 text-accent"
                                : "bg-yellow-100 text-yellow-700"
                          }`}
                        >
                          {order.status}
                        </span>
                      </td>
                      <td className="py-4 px-6 text-foreground-secondary">{order.date}</td>
                      <td className="py-4 px-6">
                        <Link
                          href={`/dashboard/orders/${order.id}`}
                          className="text-primary hover:text-primary-dark font-medium"
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
      </div>
    </main>
  )
}

export default function OrdersPage() {
  return (
    <ProtectedRoute>
      <OrdersContent />
    </ProtectedRoute>
  )
}
