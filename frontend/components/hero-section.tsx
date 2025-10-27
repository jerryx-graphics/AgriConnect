"use client"
import Link from "next/link"
import { ArrowRight, Leaf } from "lucide-react"

export default function HeroSection() {
  return (
    <section
      className="relative w-full h-screen bg-cover bg-center flex items-center justify-center text-center overflow-hidden"
      style={{
        backgroundImage:
          "url(/placeholder.svg?height=1080&width=1920&query=lush-green-farmland-kisii-kenya-agricultural-landscape)",
      }}
    >
      {/* Hero overlay */}
      <div className="hero-overlay" />

      {/* Content */}
      <div className="relative z-10 px-6 max-w-4xl mx-auto">
        {/* Badge */}
        <div className="inline-flex items-center gap-2 bg-white/10 backdrop-blur-md border border-white/20 rounded-full px-4 py-2 mb-6">
          <Leaf size={16} className="text-accent" />
          <span className="text-white text-sm font-medium">Revolutionizing Agricultural Trade</span>
        </div>

        {/* Headline */}
        <h1 className="text-4xl sm:text-5xl md:text-7xl font-extrabold text-white mb-6 leading-tight text-balance">
          Empowering Farmers with <span className="text-accent">AI & Blockchain</span>
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
            className="inline-flex items-center justify-center gap-2 bg-primary hover:bg-primary-dark text-white font-semibold px-8 py-4 rounded-full shadow-lg transition-smooth hover:shadow-xl"
          >
            Join as Farmer
            <ArrowRight size={20} />
          </Link>
          <Link
            href="/marketplace"
            className="inline-flex items-center justify-center gap-2 bg-white hover:bg-background-secondary text-primary font-semibold px-8 py-4 rounded-full shadow-lg transition-smooth hover:shadow-xl"
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
      <div className="absolute top-20 right-10 w-72 h-72 bg-primary/20 rounded-full blur-3xl opacity-20 animate-pulse" />
      <div className="absolute bottom-20 left-10 w-96 h-96 bg-accent/10 rounded-full blur-3xl opacity-20 animate-pulse" />
    </section>
  )
}
