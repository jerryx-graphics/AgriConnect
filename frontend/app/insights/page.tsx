"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { ProtectedRoute } from "@/components/protected-route"
import { useAuth } from "@/lib/auth-context"
import Navbar from "@/components/navbar"
import { TrendingUp, Brain, BarChart3, Target, Lightbulb, Clock, Star, ArrowUp, ArrowDown } from "lucide-react"
import { apiClient } from "@/lib/api"
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from "recharts"

interface PricePrediction {
  product_name: string
  current_price: number
  predicted_price: number
  prediction_date: string
  confidence: number
  trend: 'up' | 'down' | 'stable'
}

interface MarketInsight {
  id: string
  title: string
  description: string
  insight_type: string
  confidence: number
  created_at: string
}

interface Recommendation {
  id: string
  product_name: string
  reason: string
  confidence: number
  action_type: string
}

const COLORS = ['#10b981', '#f97316', '#ef4444', '#3b82f6', '#8b5cf6']

function InsightsContent() {
  const { user } = useAuth()
  const [pricePredictions, setPricePredictions] = useState<PricePrediction[]>([])
  const [marketInsights, setMarketInsights] = useState<MarketInsight[]>([])
  const [recommendations, setRecommendations] = useState<Recommendation[]>([])
  const [priceHistory, setPriceHistory] = useState<any[]>([])
  const [demandForecasts, setDemandForecasts] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [activeTab, setActiveTab] = useState("overview")
  const [error, setError] = useState("")

  useEffect(() => {
    fetchInsightsData()
  }, [])

  const fetchInsightsData = async () => {
    try {
      const [
        priceHistoryResponse,
        predictionsResponse,
        insightsResponse,
        recommendationsResponse,
        forecastsResponse
      ] = await Promise.all([
        apiClient.getPriceHistory(),
        apiClient.getPricePredictions(""),
        apiClient.getMarketInsights(),
        apiClient.getProductRecommendations(),
        apiClient.getDemandForecasts()
      ])

      if (priceHistoryResponse.data) {
        setPriceHistory(priceHistoryResponse.data.results || priceHistoryResponse.data)
      }

      if (predictionsResponse.data) {
        setPricePredictions(predictionsResponse.data.results || predictionsResponse.data)
      }

      if (insightsResponse.data) {
        setMarketInsights(insightsResponse.data.results || insightsResponse.data)
      }

      if (recommendationsResponse.data) {
        setRecommendations(recommendationsResponse.data.results || recommendationsResponse.data)
      }

      if (forecastsResponse.data) {
        setDemandForecasts(forecastsResponse.data.results || forecastsResponse.data)
      }
    } catch (err) {
      setError("Failed to load insights data")
      console.error("Error fetching insights data:", err)
    } finally {
      setIsLoading(false)
    }
  }

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up':
        return <ArrowUp size={16} className="text-green-600" />
      case 'down':
        return <ArrowDown size={16} className="text-red-600" />
      default:
        return <span className="w-4 h-4 bg-gray-400 rounded-full" />
    }
  }

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'up':
        return 'text-green-600'
      case 'down':
        return 'text-red-600'
      default:
        return 'text-gray-600'
    }
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 80) return 'text-green-600'
    if (confidence >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  // Mock data for charts when no real data is available
  const mockPriceData = [
    { month: 'Jan', bananas: 120, avocados: 200, tea: 350 },
    { month: 'Feb', bananas: 135, avocados: 180, tea: 380 },
    { month: 'Mar', bananas: 125, avocados: 220, tea: 340 },
    { month: 'Apr', bananas: 140, avocados: 190, tea: 370 },
    { month: 'May', bananas: 150, avocados: 210, tea: 390 },
    { month: 'Jun', bananas: 145, avocados: 230, tea: 410 },
  ]

  const mockDemandData = [
    { name: 'Bananas', value: 35 },
    { name: 'Avocados', value: 25 },
    { name: 'Tea', value: 20 },
    { name: 'Coffee', value: 15 },
    { name: 'Others', value: 5 },
  ]

  return (
    <main className="min-h-screen bg-background-secondary">
      <Navbar />

      <div className="pt-32 pb-12 px-6">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-foreground mb-2">AI Market Insights</h1>
            <p className="text-foreground-secondary">Data-driven insights to optimize your agricultural business</p>
          </div>

          {/* AI Stats */}
          <div className="grid md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-xl p-6 shadow-sm border border-border">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-foreground-secondary mb-1">Price Predictions</p>
                  <p className="text-3xl font-bold text-foreground">{pricePredictions.length || '8'}</p>
                </div>
                <TrendingUp className="text-primary" size={32} />
              </div>
              <p className="text-xs text-green-600 mt-2">92% accuracy</p>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-sm border border-border">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-foreground-secondary mb-1">Market Insights</p>
                  <p className="text-3xl font-bold text-foreground">{marketInsights.length || '12'}</p>
                </div>
                <Brain className="text-accent" size={32} />
              </div>
              <p className="text-xs text-foreground-secondary mt-2">Updated hourly</p>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-sm border border-border">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-foreground-secondary mb-1">Recommendations</p>
                  <p className="text-3xl font-bold text-foreground">{recommendations.length || '6'}</p>
                </div>
                <Target className="text-green-600" size={32} />
              </div>
              <p className="text-xs text-primary mt-2">3 high priority</p>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-sm border border-border">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-foreground-secondary mb-1">AI Model Health</p>
                  <p className="text-lg font-bold text-green-600">Excellent</p>
                </div>
                <BarChart3 className="text-green-600" size={32} />
              </div>
              <p className="text-xs text-foreground-secondary mt-2">Last updated: 2h ago</p>
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
                {[
                  { id: "overview", label: "Overview" },
                  { id: "predictions", label: "Price Predictions" },
                  { id: "insights", label: "Market Insights" },
                  { id: "recommendations", label: "Recommendations" }
                ].map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`py-4 px-1 border-b-2 font-medium text-sm ${
                      activeTab === tab.id
                        ? "border-primary text-primary"
                        : "border-transparent text-foreground-secondary hover:text-foreground"
                    }`}
                  >
                    {tab.label}
                  </button>
                ))}
              </nav>
            </div>

            <div className="p-6">
              {isLoading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
                  <p className="text-foreground-secondary">Loading AI insights...</p>
                </div>
              ) : activeTab === "overview" ? (
                <div className="space-y-8">
                  {/* Price Trends Chart */}
                  <div>
                    <h3 className="text-lg font-bold text-foreground mb-4">Price Trends (Last 6 Months)</h3>
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={priceHistory.length > 0 ? priceHistory : mockPriceData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="month" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey="bananas" stroke="#10b981" strokeWidth={2} />
                        <Line type="monotone" dataKey="avocados" stroke="#f97316" strokeWidth={2} />
                        <Line type="monotone" dataKey="tea" stroke="#3b82f6" strokeWidth={2} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>

                  {/* Demand Distribution */}
                  <div>
                    <h3 className="text-lg font-bold text-foreground mb-4">Market Demand Distribution</h3>
                    <ResponsiveContainer width="100%" height={300}>
                      <PieChart>
                        <Pie
                          data={demandForecasts.length > 0 ? demandForecasts : mockDemandData}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                          outerRadius={80}
                          fill="#8884d8"
                          dataKey="value"
                        >
                          {mockDemandData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              ) : activeTab === "predictions" ? (
                pricePredictions.length === 0 ? (
                  <div className="text-center py-8">
                    <TrendingUp size={48} className="text-foreground-secondary mx-auto mb-4" />
                    <p className="text-lg text-foreground-secondary mb-2">No price predictions available</p>
                    <p className="text-foreground-secondary">AI predictions will appear here based on market data</p>
                  </div>
                ) : (
                  <div className="grid gap-4">
                    {pricePredictions.map((prediction, index) => (
                      <div key={index} className="border border-border rounded-lg p-6">
                        <div className="flex justify-between items-start mb-4">
                          <div>
                            <h3 className="text-lg font-bold text-foreground">{prediction.product_name}</h3>
                            <p className="text-foreground-secondary">Prediction for {new Date(prediction.prediction_date).toLocaleDateString()}</p>
                          </div>
                          <div className="text-right">
                            <div className={`flex items-center gap-1 ${getTrendColor(prediction.trend)}`}>
                              {getTrendIcon(prediction.trend)}
                              <span className="font-semibold">
                                {prediction.trend === 'up' ? '+' : prediction.trend === 'down' ? '-' : ''}
                                {Math.abs(((prediction.predicted_price - prediction.current_price) / prediction.current_price) * 100).toFixed(1)}%
                              </span>
                            </div>
                          </div>
                        </div>

                        <div className="grid md:grid-cols-3 gap-4">
                          <div>
                            <p className="text-sm text-foreground-secondary">Current Price</p>
                            <p className="text-xl font-bold text-foreground">KES {prediction.current_price}</p>
                          </div>
                          <div>
                            <p className="text-sm text-foreground-secondary">Predicted Price</p>
                            <p className={`text-xl font-bold ${getTrendColor(prediction.trend)}`}>
                              KES {prediction.predicted_price}
                            </p>
                          </div>
                          <div>
                            <p className="text-sm text-foreground-secondary">Confidence</p>
                            <p className={`text-xl font-bold ${getConfidenceColor(prediction.confidence)}`}>
                              {prediction.confidence}%
                            </p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )
              ) : activeTab === "insights" ? (
                marketInsights.length === 0 ? (
                  <div className="text-center py-8">
                    <Lightbulb size={48} className="text-foreground-secondary mx-auto mb-4" />
                    <p className="text-lg text-foreground-secondary mb-2">No market insights available</p>
                    <p className="text-foreground-secondary">AI-generated insights will appear here</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {marketInsights.map((insight) => (
                      <div key={insight.id} className="border border-border rounded-lg p-6">
                        <div className="flex justify-between items-start mb-4">
                          <div>
                            <h3 className="text-lg font-bold text-foreground mb-2">{insight.title}</h3>
                            <p className="text-foreground-secondary">{insight.description}</p>
                          </div>
                          <div className="flex items-center gap-2">
                            <Star size={16} className={getConfidenceColor(insight.confidence)} />
                            <span className={`text-sm font-semibold ${getConfidenceColor(insight.confidence)}`}>
                              {insight.confidence}%
                            </span>
                          </div>
                        </div>
                        <div className="flex items-center gap-4 text-sm text-foreground-secondary">
                          <span className="capitalize">{insight.insight_type.replace('_', ' ')}</span>
                          <span>•</span>
                          <span>{new Date(insight.created_at).toLocaleDateString()}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )
              ) : (
                recommendations.length === 0 ? (
                  <div className="text-center py-8">
                    <Target size={48} className="text-foreground-secondary mx-auto mb-4" />
                    <p className="text-lg text-foreground-secondary mb-2">No recommendations available</p>
                    <p className="text-foreground-secondary">AI recommendations will appear here based on your activity</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {recommendations.map((recommendation) => (
                      <div key={recommendation.id} className="border border-border rounded-lg p-6">
                        <div className="flex justify-between items-start mb-4">
                          <div>
                            <h3 className="text-lg font-bold text-foreground mb-2">{recommendation.product_name}</h3>
                            <p className="text-foreground-secondary">{recommendation.reason}</p>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                              recommendation.action_type === 'buy'
                                ? 'bg-green-100 text-green-800'
                                : recommendation.action_type === 'sell'
                                ? 'bg-blue-100 text-blue-800'
                                : 'bg-yellow-100 text-yellow-800'
                            }`}>
                              {recommendation.action_type.toUpperCase()}
                            </span>
                          </div>
                        </div>
                        <div className="flex items-center gap-4">
                          <span className={`text-sm font-semibold ${getConfidenceColor(recommendation.confidence)}`}>
                            {recommendation.confidence}% confidence
                          </span>
                          <button className="bg-primary text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-primary-dark transition-smooth">
                            Act on Recommendation
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )
              )}
            </div>
          </div>

          {/* AI Model Info */}
          <div className="bg-white rounded-xl p-8 shadow-sm border border-border">
            <h2 className="text-2xl font-bold text-foreground mb-6">How Our AI Works</h2>
            <div className="grid md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="bg-primary/10 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                  <Brain className="text-primary" size={24} />
                </div>
                <h3 className="text-lg font-bold text-foreground mb-2">Machine Learning</h3>
                <p className="text-foreground-secondary">
                  Advanced algorithms analyze historical market data, weather patterns, and demand trends to generate accurate predictions.
                </p>
              </div>
              <div className="text-center">
                <div className="bg-accent/10 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                  <BarChart3 className="text-accent" size={24} />
                </div>
                <h3 className="text-lg font-bold text-foreground mb-2">Real-time Analysis</h3>
                <p className="text-foreground-secondary">
                  Continuous monitoring of market conditions, price fluctuations, and supply-demand dynamics for up-to-date insights.
                </p>
              </div>
              <div className="text-center">
                <div className="bg-green-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                  <Target className="text-green-600" size={24} />
                </div>
                <h3 className="text-lg font-bold text-foreground mb-2">Actionable Recommendations</h3>
                <p className="text-foreground-secondary">
                  Personalized suggestions for optimal planting times, pricing strategies, and market opportunities.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}

export default function InsightsPage() {
  return (
    <ProtectedRoute>
      <InsightsContent />
    </ProtectedRoute>
  )
}