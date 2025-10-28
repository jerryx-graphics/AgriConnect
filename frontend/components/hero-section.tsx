"use client"
import Link from "next/link"
import { ArrowRight, Leaf } from "lucide-react"

export default function HeroSection() {
  return (
    <section
      className="relative w-full h-screen bg-cover bg-center flex items-center justify-center text-center overflow-hidden"
      style={{
        backgroundImage:
          "url(/back2.jpeg)",
      }}
    >
      {/* Hero overlay */}
      <div className="hero-overlay" />

      {/* Content */}
      <div className="relative z-10 px-6 max-w-4xl mx-auto">
        {/* Headline */}
        <h1 className="text-3xl sm:text-4xl md:text-5xl font-extrabold text-white mb-6 leading-tight text-balance">
          Turn your Produce into <span className="text-yellow-400">Profit</span>. <span className="text-green-400">Join AgriConnect</span>
        </h1>

        {/* Tagline */}
        <p className="text-lg sm:text-xl md:text-2xl text-white/90 mb-8 max-w-2xl mx-auto text-balance">
          Trade smarter, faster, and fairer. Connect directly with buyers, eliminate middlemen, and build your digital
          future.
        </p>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row justify-center gap-4 sm:gap-6">
          <Link
            href="/register?role=farmer"
            className="inline-flex items-center justify-center gap-2 bg-green-600 hover:bg-green-700 text-white font-semibold px-8 py-4 rounded-full shadow-lg transition-smooth hover:shadow-xl"
          >
            Join as Farmer
            <ArrowRight size={20} />
          </Link>
          <Link
            href="/marketplace"
            className="inline-flex items-center justify-center gap-2 bg-yellow-500 hover:bg-yellow-600 text-gray-900 font-semibold px-8 py-4 rounded-full shadow-lg transition-smooth hover:shadow-xl"
          >
            Explore Marketplace
            <ArrowRight size={20} />
          </Link>
        </div>

        {/* Trust indicators */}
        <div className="mt-12 pt-8 border-t border-white/10 flex flex-col sm:flex-row justify-center gap-8 text-white/80 text-sm">
          <div>
            <p className="font-bold text-white">500+</p>
            <p>Farmers Connected</p>
          </div>
          <div>
            <p className="font-bold text-white">10,000+</p>
            <p>Monthly Transactions</p>
          </div>
          <div>
            <p className="font-bold text-white">60%</p>
            <p>More Revenue</p>
          </div>
        </div>
      </div>

      {/* Animated gradient orb (decorative) */}
      <div className="absolute top-20 right-10 w-72 h-72 bg-green-500/20 rounded-full blur-3xl opacity-20 animate-pulse" />
      <div className="absolute bottom-20 left-10 w-96 h-96 bg-yellow-400/15 rounded-full blur-3xl opacity-20 animate-pulse" />
    </section>
  )
}
