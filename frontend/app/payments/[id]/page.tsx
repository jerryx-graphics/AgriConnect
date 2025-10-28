"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { ProtectedRoute } from "@/components/protected-route"
import { useAuth } from "@/lib/auth-context"
import Navbar from "@/components/navbar"
import { ArrowLeft, CreditCard, Phone, DollarSign, Clock, CheckCircle, AlertCircle, Download, RefreshCw } from "lucide-react"
import Link from "next/link"
import { apiClient } from "@/lib/api"

interface PaymentDetail {
  id: string
  order_id: string
  amount: number
  status: string
  payment_method: string
  transaction_id?: string
  created_at: string
  updated_at: string
  order?: {
    id: string
    total_amount: number
    items: Array<{
      product: {
        name: string
        price: number
      }
      quantity: number
    }>
  }
}

export default function PaymentDetailPage({ params }: { params: { id: string } }) {
  const { user } = useAuth()
  const [payment, setPayment] = useState<PaymentDetail | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState("")
  const [isRefunding, setIsRefunding] = useState(false)

  useEffect(() => {
    fetchPayment()
  }, [params.id])

  const fetchPayment = async () => {
    try {
      const response = await apiClient.getPayment(params.id)
      if (response.data) {
        setPayment(response.data)
      } else {
        setError("Payment not found")
      }
    } catch (err) {
      setError("Failed to load payment details")
      console.error("Error fetching payment:", err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleRefund = async () => {
    if (!payment) return

    setIsRefunding(true)
    try {
      const response = await apiClient.createPaymentRefund({
        payment_id: payment.id,
        amount: payment.amount,
        reason: "Customer requested refund"
      })

      if (response.data) {
        alert("Refund request submitted successfully")
        fetchPayment() // Refresh payment data
      } else {
        alert(response.error || "Failed to submit refund request")
      }
    } catch (err) {
      console.error("Error requesting refund:", err)
      alert("Failed to submit refund request")
    } finally {
      setIsRefunding(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
      case 'success':
        return 'bg-green-100 text-green-800'
      case 'pending':
        return 'bg-yellow-100 text-yellow-800'
      case 'failed':
      case 'cancelled':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
      case 'success':
        return <CheckCircle size={20} className="text-green-600" />
      case 'pending':
        return <Clock size={20} className="text-yellow-600" />
      case 'failed':
      case 'cancelled':
        return <AlertCircle size={20} className="text-red-600" />
      default:
        return <Clock size={20} className="text-gray-600" />
    }
  }

  const getPaymentMethodIcon = (method: string) => {
    switch (method.toLowerCase()) {
      case 'mpesa':
      case 'm-pesa':
        return <Phone size={24} className="text-green-600" />
      case 'card':
      case 'credit_card':
        return <CreditCard size={24} className="text-blue-600" />
      default:
        return <DollarSign size={24} className="text-gray-600" />
    }
  }

  if (isLoading) {
    return (
      <ProtectedRoute>
        <main className="min-h-screen bg-background-secondary">
          <Navbar />
          <div className="flex justify-center items-center min-h-[calc(100vh-80px)]">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            <span className="ml-2 text-foreground-secondary">Loading payment details...</span>
          </div>
        </main>
      </ProtectedRoute>
    )
  }

  if (error || !payment) {
    return (
      <ProtectedRoute>
        <main className="min-h-screen bg-background-secondary">
          <Navbar />
          <div className="flex flex-col justify-center items-center min-h-[calc(100vh-80px)] px-6">
            <div className="text-center">
              <h1 className="text-2xl font-bold text-foreground mb-4">Payment Not Found</h1>
              <p className="text-foreground-secondary mb-6">{error}</p>
              <Link
                href="/payments"
                className="inline-flex items-center gap-2 bg-primary text-white px-6 py-3 rounded-lg hover:bg-primary-dark transition-smooth"
              >
                <ArrowLeft size={20} />
                Back to Payments
              </Link>
            </div>
          </div>
        </main>
      </ProtectedRoute>
    )
  }

  return (
    <ProtectedRoute>
      <main className="min-h-screen bg-background-secondary">
        <Navbar />

        <div className="pt-32 pb-12 px-6">
          <div className="max-w-4xl mx-auto">
            {/* Breadcrumb */}
            <div className="flex gap-2 text-sm text-foreground-secondary mb-8">
              <Link href="/payments" className="hover:text-primary">
                Payments
              </Link>
              <span>/</span>
              <span className="text-foreground">Payment #{payment.id.slice(-8)}</span>
            </div>

            {/* Payment Header */}
            <div className="bg-white rounded-xl p-8 shadow-sm border border-border mb-8">
              <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-6">
                <div>
                  <h1 className="text-3xl font-bold text-foreground mb-2">
                    Payment #{payment.id.slice(-8)}
                  </h1>
                  <p className="text-foreground-secondary">
                    Created on {new Date(payment.created_at).toLocaleDateString()}
                  </p>
                </div>
                <div className="flex items-center gap-3 mt-4 lg:mt-0">
                  {getStatusIcon(payment.status)}
                  <span className={`px-4 py-2 rounded-full text-sm font-semibold ${getStatusColor(payment.status)}`}>
                    {payment.status.replace('_', ' ').toUpperCase()}
                  </span>
                </div>
              </div>

              <div className="grid md:grid-cols-3 gap-6">
                <div>
                  <p className="text-sm text-foreground-secondary mb-1">Amount</p>
                  <p className="text-2xl font-bold text-primary">KES {payment.amount.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-sm text-foreground-secondary mb-1">Payment Method</p>
                  <div className="flex items-center gap-2">
                    {getPaymentMethodIcon(payment.payment_method)}
                    <span className="font-semibold text-foreground capitalize">
                      {payment.payment_method.replace('_', ' ')}
                    </span>
                  </div>
                </div>
                <div>
                  <p className="text-sm text-foreground-secondary mb-1">Order</p>
                  <Link
                    href={`/orders/${payment.order_id}`}
                    className="text-primary hover:text-primary-dark font-semibold"
                  >
                    #{payment.order_id.slice(-8)}
                  </Link>
                </div>
              </div>

              {payment.transaction_id && (
                <div className="mt-6 pt-6 border-t border-border">
                  <p className="text-sm text-foreground-secondary mb-1">Transaction ID</p>
                  <p className="font-mono text-sm text-foreground">{payment.transaction_id}</p>
                </div>
              )}
            </div>

            {/* Order Details */}
            {payment.order && (
              <div className="bg-white rounded-xl p-8 shadow-sm border border-border mb-8">
                <h2 className="text-xl font-bold text-foreground mb-6">Order Details</h2>
                <div className="space-y-4">
                  {payment.order.items.map((item, index) => (
                    <div key={index} className="flex justify-between items-center py-3 border-b border-border last:border-b-0">
                      <div>
                        <p className="font-semibold text-foreground">{item.product.name}</p>
                        <p className="text-sm text-foreground-secondary">Quantity: {item.quantity}</p>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold text-foreground">
                          KES {(item.product.price * item.quantity).toLocaleString()}
                        </p>
                        <p className="text-sm text-foreground-secondary">
                          KES {item.product.price.toLocaleString()} each
                        </p>
                      </div>
                    </div>
                  ))}
                  <div className="flex justify-between items-center pt-4 border-t border-border">
                    <p className="text-lg font-bold text-foreground">Total</p>
                    <p className="text-xl font-bold text-primary">
                      KES {payment.order.total_amount.toLocaleString()}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Payment Actions */}
            <div className="bg-white rounded-xl p-8 shadow-sm border border-border">
              <h2 className="text-xl font-bold text-foreground mb-6">Payment Actions</h2>
              <div className="flex flex-col sm:flex-row gap-4">
                <button
                  onClick={() => window.print()}
                  className="flex items-center justify-center gap-2 bg-background-secondary hover:bg-border text-foreground font-semibold py-3 px-6 rounded-lg transition-smooth"
                >
                  <Download size={20} />
                  Download Receipt
                </button>

                {payment.status.toLowerCase() === 'completed' && (
                  <button
                    onClick={handleRefund}
                    disabled={isRefunding}
                    className="flex items-center justify-center gap-2 bg-red-600 hover:bg-red-700 text-white font-semibold py-3 px-6 rounded-lg transition-smooth disabled:opacity-50"
                  >
                    {isRefunding ? (
                      <RefreshCw size={20} className="animate-spin" />
                    ) : (
                      <RefreshCw size={20} />
                    )}
                    {isRefunding ? "Processing..." : "Request Refund"}
                  </button>
                )}

                <Link
                  href={`/orders/${payment.order_id}`}
                  className="flex items-center justify-center gap-2 bg-primary hover:bg-primary-dark text-white font-semibold py-3 px-6 rounded-lg transition-smooth"
                >
                  View Order
                </Link>
              </div>
            </div>
          </div>
        </div>
      </main>
    </ProtectedRoute>
  )
}