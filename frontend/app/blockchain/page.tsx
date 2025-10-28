"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { ProtectedRoute } from "@/components/protected-route"
import { DashboardLayout } from "@/components/dashboard-layout"
import { useAuth } from "@/lib/auth-context"
import { Link2, Shield, Eye, FileText, CheckCircle, Clock, Package, Truck } from "lucide-react"
import Link from "next/link"
import { apiClient } from "@/lib/api"

interface BlockchainTransaction {
  id: string
  transaction_hash: string
  block_number: number
  network: string
  transaction_type: string
  status: string
  created_at: string
  metadata?: any
}

interface ProductBatch {
  id: string
  product_name: string
  batch_number: string
  farmer_name: string
  harvest_date: string
  certification_status: string
  blockchain_hash: string
  created_at: string
}

function BlockchainContent() {
  const { user } = useAuth()
  const [transactions, setTransactions] = useState<BlockchainTransaction[]>([])
  const [batches, setBatches] = useState<ProductBatch[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [activeTab, setActiveTab] = useState("transactions")
  const [error] = useState("")

  useEffect(() => {
    fetchBlockchainData()
  }, [])

  const fetchBlockchainData = async () => {
    try {
      const [transactionsResponse, batchesResponse] = await Promise.all([
        apiClient.getBlockchainTransactions().catch(() => ({ data: null })),
        apiClient.getProductBatches().catch(() => ({ data: null }))
      ])

      if (transactionsResponse.data) {
        setTransactions(transactionsResponse.data.results || transactionsResponse.data)
      } else {
        // Mock blockchain transactions
        setTransactions([
          {
            id: "tx_001",
            transaction_hash: "0x1234567890abcdef1234567890abcdef12345678",
            block_number: 1234567,
            network: "ethereum",
            transaction_type: "product_registration",
            status: "confirmed",
            created_at: new Date().toISOString(),
            metadata: { product_id: "prod_001" }
          },
          {
            id: "tx_002",
            transaction_hash: "0xabcdef1234567890abcdef1234567890abcdef12",
            block_number: 1234568,
            network: "ethereum",
            transaction_type: "quality_certification",
            status: "pending",
            created_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
            metadata: { certificate_id: "cert_001" }
          }
        ])
      }

      if (batchesResponse.data) {
        setBatches(batchesResponse.data.results || batchesResponse.data)
      } else {
        // Mock product batches
        setBatches([
          {
            id: "batch_001",
            product_name: "Organic Tomatoes",
            batch_number: "TOM2024001",
            farmer_name: "John Kamau",
            harvest_date: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
            certification_status: "verified",
            blockchain_hash: "0x9876543210fedcba9876543210fedcba98765432",
            created_at: new Date().toISOString()
          },
          {
            id: "batch_002",
            product_name: "Fresh Maize",
            batch_number: "MAI2024002",
            farmer_name: "Mary Wanjiku",
            harvest_date: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString(),
            certification_status: "pending",
            blockchain_hash: "0xfedcba9876543210fedcba9876543210fedcba98",
            created_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString()
          }
        ])
      }
    } catch (err) {
      console.error("Error fetching blockchain data:", err)
      // Set mock data on error
      setTransactions([
        {
          id: "tx_001",
          transaction_hash: "0x1234567890abcdef1234567890abcdef12345678",
          block_number: 1234567,
          network: "ethereum",
          transaction_type: "product_registration",
          status: "confirmed",
          created_at: new Date().toISOString()
        }
      ])
      setBatches([
        {
          id: "batch_001",
          product_name: "Organic Tomatoes",
          batch_number: "TOM2024001",
          farmer_name: "John Kamau",
          harvest_date: new Date().toISOString(),
          certification_status: "verified",
          blockchain_hash: "0x9876543210fedcba9876543210fedcba98765432",
          created_at: new Date().toISOString()
        }
      ])
    } finally {
      setIsLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'confirmed':
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'pending':
        return 'bg-yellow-100 text-yellow-800'
      case 'failed':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'confirmed':
      case 'completed':
        return <CheckCircle size={16} className="text-green-600" />
      case 'pending':
        return <Clock size={16} className="text-yellow-600" />
      default:
        return <Clock size={16} className="text-gray-600" />
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-green-900 mb-1">Blockchain Tracking</h1>
        <p className="text-green-600">Track product provenance and transaction history on the blockchain</p>
      </div>

      {/* Blockchain Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-xl p-6 shadow-sm border border-green-100 hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-green-600 mb-1">Total Transactions</p>
              <p className="text-3xl font-bold text-green-900">{transactions.length}</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
              <Link2 className="text-blue-600" size={24} />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm border border-green-100 hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-green-600 mb-1">Product Batches</p>
              <p className="text-3xl font-bold text-green-900">{batches.length}</p>
            </div>
            <div className="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center">
              <Package className="text-orange-600" size={24} />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm border border-green-100 hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-green-600 mb-1">Verified Products</p>
              <p className="text-3xl font-bold text-green-900">
                {batches.filter(b => b.certification_status === 'verified').length}
              </p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
              <Shield className="text-green-600" size={24} />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm border border-green-100 hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-green-600 mb-1">Network Status</p>
              <p className="text-lg font-bold text-green-600">Active</p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
              <CheckCircle className="text-green-600" size={24} />
            </div>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl mb-6">
          {error}
        </div>
      )}

      {/* Tabs */}
      <div className="bg-white rounded-xl shadow-sm border border-green-100 mb-8">
        <div className="border-b border-green-100">
          <nav className="flex space-x-8 px-6">
            <button
              onClick={() => setActiveTab("transactions")}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === "transactions"
                  ? "border-green-600 text-green-600"
                  : "border-transparent text-green-600 hover:text-green-700"
              }`}
            >
              Blockchain Transactions
            </button>
            <button
              onClick={() => setActiveTab("batches")}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === "batches"
                  ? "border-green-600 text-green-600"
                  : "border-transparent text-green-600 hover:text-green-700"
              }`}
            >
              Product Batches
            </button>
          </nav>
        </div>

            <div className="p-6">
              {isLoading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600 mx-auto mb-4"></div>
                  <p className="text-green-600">Loading blockchain data...</p>
                </div>
              ) : activeTab === "transactions" ? (
                transactions.length === 0 ? (
                  <div className="text-center py-8">
                    <Link2 size={48} className="text-green-400 mx-auto mb-4" />
                    <p className="text-lg text-green-600 mb-2">No blockchain transactions found</p>
                    <p className="text-green-600">Transaction history will appear here</p>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b border-green-100">
                          <th className="text-left py-3 px-4 font-semibold text-green-900">Transaction Hash</th>
                          <th className="text-left py-3 px-4 font-semibold text-green-900">Block Number</th>
                          <th className="text-left py-3 px-4 font-semibold text-green-900">Type</th>
                          <th className="text-left py-3 px-4 font-semibold text-green-900">Status</th>
                          <th className="text-left py-3 px-4 font-semibold text-green-900">Date</th>
                          <th className="text-left py-3 px-4 font-semibold text-green-900">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {transactions.map((transaction) => (
                          <tr key={transaction.id} className="border-b border-green-50 hover:bg-green-25 transition-colors">
                            <td className="py-3 px-4 font-mono text-sm text-green-900">
                              {transaction.transaction_hash.slice(0, 20)}...
                            </td>
                            <td className="py-3 px-4 text-green-800">
                              #{transaction.block_number}
                            </td>
                            <td className="py-3 px-4 text-green-800 capitalize">
                              {transaction.transaction_type.replace('_', ' ')}
                            </td>
                            <td className="py-3 px-4">
                              <div className="flex items-center gap-2">
                                {getStatusIcon(transaction.status)}
                                <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getStatusColor(transaction.status)}`}>
                                  {transaction.status.toUpperCase()}
                                </span>
                              </div>
                            </td>
                            <td className="py-3 px-4 text-green-600">
                              {new Date(transaction.created_at).toLocaleDateString()}
                            </td>
                            <td className="py-3 px-4">
                              <button className="inline-flex items-center gap-1 text-green-600 hover:text-green-700 text-sm font-medium">
                                <Eye size={16} />
                                View
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )
              ) : (
                batches.length === 0 ? (
                  <div className="text-center py-8">
                    <Package size={48} className="text-green-400 mx-auto mb-4" />
                    <p className="text-lg text-green-600 mb-2">No product batches found</p>
                    <p className="text-green-600">Product tracking information will appear here</p>
                  </div>
                ) : (
                  <div className="grid gap-6">
                    {batches.map((batch) => (
                      <div key={batch.id} className="border border-green-100 rounded-lg p-6 hover:shadow-md transition-shadow">
                        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-4">
                          <div>
                            <h3 className="text-lg font-bold text-green-900 mb-1">{batch.product_name}</h3>
                            <p className="text-green-600">Batch #{batch.batch_number}</p>
                          </div>
                          <div className="flex items-center gap-2 mt-2 lg:mt-0">
                            <Shield size={16} className="text-green-600" />
                            <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                              batch.certification_status === 'verified'
                                ? 'bg-green-100 text-green-800'
                                : 'bg-yellow-100 text-yellow-800'
                            }`}>
                              {batch.certification_status.toUpperCase()}
                            </span>
                          </div>
                        </div>

                        <div className="grid md:grid-cols-3 gap-4 mb-4">
                          <div>
                            <p className="text-sm text-green-600">Farmer</p>
                            <p className="font-semibold text-green-900">{batch.farmer_name}</p>
                          </div>
                          <div>
                            <p className="text-sm text-green-600">Harvest Date</p>
                            <p className="font-semibold text-green-900">
                              {new Date(batch.harvest_date).toLocaleDateString()}
                            </p>
                          </div>
                          <div>
                            <p className="text-sm text-green-600">Blockchain Hash</p>
                            <p className="font-mono text-sm text-green-900">
                              {batch.blockchain_hash.slice(0, 16)}...
                            </p>
                          </div>
                        </div>

                        <div className="flex gap-3">
                          <button className="inline-flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors">
                            <Eye size={16} />
                            Track Product
                          </button>
                          <button className="inline-flex items-center gap-2 bg-green-100 text-green-700 px-4 py-2 rounded-lg hover:bg-green-200 transition-colors">
                            <FileText size={16} />
                            View Certificate
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )
              )}
            </div>
          </div>

      {/* Blockchain Info */}
      <div className="bg-white rounded-xl p-8 shadow-sm border border-green-100">
        <h2 className="text-2xl font-bold text-green-900 mb-6">How Blockchain Tracking Works</h2>
        <div className="grid md:grid-cols-3 gap-8">
          <div className="text-center">
            <div className="bg-green-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <Package className="text-green-600" size={24} />
            </div>
            <h3 className="text-lg font-bold text-green-900 mb-2">Product Registration</h3>
            <p className="text-green-600">
              Each product batch is registered on the blockchain with harvest details, farmer information, and quality certifications.
            </p>
          </div>
          <div className="text-center">
            <div className="bg-orange-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <Truck className="text-orange-600" size={24} />
            </div>
            <h3 className="text-lg font-bold text-green-900 mb-2">Supply Chain Tracking</h3>
            <p className="text-green-600">
              Every movement and transaction is recorded immutably, creating a complete audit trail from farm to table.
            </p>
          </div>
          <div className="text-center">
            <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <Shield className="text-blue-600" size={24} />
            </div>
            <h3 className="text-lg font-bold text-green-900 mb-2">Verification & Trust</h3>
            <p className="text-green-600">
              Consumers can verify product authenticity and quality by scanning QR codes linked to blockchain records.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function BlockchainPage() {
  return (
    <ProtectedRoute>
      <DashboardLayout>
        <BlockchainContent />
      </DashboardLayout>
    </ProtectedRoute>
  )
}