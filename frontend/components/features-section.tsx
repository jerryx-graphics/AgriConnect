"use client"
import { TrendingUp, Shield, Zap, Users } from "lucide-react"

const features = [
  {
    icon: TrendingUp,
    title: "Smart Pricing",
    description: "AI-powered price recommendations based on real-time market data and demand forecasting.",
  },
  {
    icon: Shield,
    title: "Blockchain Trust",
    description: "Immutable transaction records and supply chain traceability from farm to table.",
  },
  {
    icon: Zap,
    title: "Instant Payments",
    description: "Secure escrow system with automatic payment release upon delivery confirmation.",
  },
  {
    icon: Users,
    title: "Direct Connection",
    description: "Eliminate middlemen and connect directly with verified buyers and sellers.",
  },
]

export default function FeaturesSection() {
  return (
    <section className="py-20 px-6 bg-gradient-to-b from-yellow-50 to-green-50">
      <div className="max-w-6xl mx-auto">
        {/* Section header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-foreground mb-4">Why Choose AgriConnect?</h2>
          <p className="text-lg text-foreground-secondary max-w-2xl mx-auto">
            Combining cutting-edge technology with agricultural expertise to transform rural commerce.
          </p>
        </div>

        {/* Features grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => {
            const Icon = feature.icon
            return (
              <div
                key={index}
                className="bg-white rounded-xl p-6 shadow-sm hover:shadow-lg transition-smooth border border-border"
              >
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                  <Icon size={24} className="text-green-600" />
                </div>
                <h3 className="text-lg font-bold text-foreground mb-2">{feature.title}</h3>
                <p className="text-foreground-secondary text-sm leading-relaxed">{feature.description}</p>
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
