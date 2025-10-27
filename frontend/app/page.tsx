"use client"

import Navbar from "@/components/navbar"
import HeroSection from "@/components/hero-section"
import FeaturesSection from "@/components/features-section"
import AgribotChatbot from "@/components/agribot-chatbot"
import { ArrowRight, CheckCircle } from "lucide-react"
import Link from "next/link"

export default function Home() {
  return (
    <main className="min-h-screen">
      <Navbar />
      <HeroSection />
      <FeaturesSection />

      {/* CTA Section */}
      <section className="py-20 px-6 bg-primary text-white">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">Ready to Transform Your Agricultural Business?</h2>
          <p className="text-lg text-white/90 mb-8 max-w-2xl mx-auto">
            Join thousands of farmers and buyers already using AgriConnect to grow their business.
          </p>
          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <Link
              href="/register?role=farmer"
              className="inline-flex items-center justify-center gap-2 bg-white hover:bg-background-secondary text-primary font-bold px-8 py-4 rounded-full transition-smooth"
            >
              Start Selling
              <ArrowRight size={20} />
            </Link>
            <Link
              href="/marketplace"
              className="inline-flex items-center justify-center gap-2 border-2 border-white hover:bg-white/10 text-white font-bold px-8 py-4 rounded-full transition-smooth"
            >
              Browse Products
              <ArrowRight size={20} />
            </Link>
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-20 px-6 bg-background-secondary">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-4xl font-bold text-foreground text-center mb-16">Why Farmers Choose AgriConnect</h2>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { title: "60% More Revenue", desc: "Eliminate middlemen and keep more of your profits" },
              { title: "Instant Payments", desc: "Get paid within 24 hours via M-Pesa or bank transfer" },
              { title: "Build Credit History", desc: "Blockchain records unlock access to loans and insurance" },
              { title: "Market Intelligence", desc: "AI-powered insights help you plant and price smarter" },
              { title: "Direct Buyers", desc: "Connect with verified restaurants, retailers, and exporters" },
              { title: "24/7 Support", desc: "AgriBot assistant available in your local language" },
            ].map((benefit, idx) => (
              <div key={idx} className="bg-white rounded-xl p-6 shadow-sm border border-border">
                <div className="flex items-start gap-3 mb-4">
                  <CheckCircle className="text-primary flex-shrink-0 mt-1" size={24} />
                  <h3 className="text-lg font-bold text-foreground">{benefit.title}</h3>
                </div>
                <p className="text-foreground-secondary">{benefit.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-foreground text-white py-12 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <h4 className="font-bold mb-4">AgriConnect</h4>
              <p className="text-white/70 text-sm">Empowering farmers with AI and blockchain technology.</p>
            </div>
            <div>
              <h4 className="font-bold mb-4">Platform</h4>
              <ul className="space-y-2 text-sm text-white/70">
                <li>
                  <Link href="/marketplace" className="hover:text-white">
                    Marketplace
                  </Link>
                </li>
                <li>
                  <Link href="/dashboard" className="hover:text-white">
                    Dashboard
                  </Link>
                </li>
                <li>
                  <Link href="/insights" className="hover:text-white">
                    Insights
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold mb-4">Company</h4>
              <ul className="space-y-2 text-sm text-white/70">
                <li>
                  <Link href="/about" className="hover:text-white">
                    About
                  </Link>
                </li>
                <li>
                  <Link href="/contact" className="hover:text-white">
                    Contact
                  </Link>
                </li>
                <li>
                  <Link href="/careers" className="hover:text-white">
                    Careers
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold mb-4">Legal</h4>
              <ul className="space-y-2 text-sm text-white/70">
                <li>
                  <Link href="/privacy" className="hover:text-white">
                    Privacy
                  </Link>
                </li>
                <li>
                  <Link href="/terms" className="hover:text-white">
                    Terms
                  </Link>
                </li>
              </ul>
            </div>
          </div>
          <div className="border-t border-white/10 pt-8 text-center text-sm text-white/70">
            <p>&copy; 2025 AgriConnect. All rights reserved. Transforming agriculture in Kisii and beyond.</p>
          </div>
        </div>
      </footer>

      {/* AgriBot Chatbot */}
      <AgribotChatbot />
    </main>
  )
}
