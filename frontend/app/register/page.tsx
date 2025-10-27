"use client"

import type React from "react"

import { useState } from "react"
import Navbar from "@/components/navbar"
import { ArrowRight, CheckCircle } from "lucide-react"
import Link from "next/link"

export default function RegisterPage() {
  const [role, setRole] = useState<"farmer" | "buyer" | null>(null)
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: "",
    location: "",
    farmSize: "",
    crops: "",
  })

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    console.log("Registration data:", { role, ...formData })
    // Handle registration logic here
  }

  return (
    <main className="min-h-screen bg-background-secondary">
      <Navbar />

      <div className="pt-32 pb-12 px-6">
        <div className="max-w-2xl mx-auto">
          {/* Role Selection */}
          {!role ? (
            <div>
              <h1 className="text-4xl font-bold text-foreground text-center mb-4">Join AgriConnect</h1>
              <p className="text-lg text-foreground-secondary text-center mb-12">Choose your role to get started</p>

              <div className="grid md:grid-cols-2 gap-6">
                {[
                  {
                    role: "farmer" as const,
                    title: "I'm a Farmer",
                    desc: "Sell your produce directly to buyers",
                    benefits: ["60% more revenue", "Instant payments", "Build credit history"],
                  },
                  {
                    role: "buyer" as const,
                    title: "I'm a Buyer",
                    desc: "Source fresh products directly from farmers",
                    benefits: ["Verified quality", "Better prices", "Direct relationships"],
                  },
                ].map((option) => (
                  <button
                    key={option.role}
                    onClick={() => setRole(option.role)}
                    className="bg-white rounded-xl p-8 shadow-sm border-2 border-border hover:border-primary transition-smooth text-left"
                  >
                    <h3 className="text-2xl font-bold text-foreground mb-2">{option.title}</h3>
                    <p className="text-foreground-secondary mb-6">{option.desc}</p>
                    <ul className="space-y-2">
                      {option.benefits.map((benefit, idx) => (
                        <li key={idx} className="flex items-center gap-2 text-sm text-foreground">
                          <CheckCircle size={16} className="text-primary" />
                          {benefit}
                        </li>
                      ))}
                    </ul>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div>
              <button
                onClick={() => setRole(null)}
                className="text-primary hover:text-primary-dark font-semibold mb-6 flex items-center gap-2"
              >
                ← Back
              </button>

              <h1 className="text-4xl font-bold text-foreground mb-2">
                {role === "farmer" ? "Farmer Registration" : "Buyer Registration"}
              </h1>
              <p className="text-foreground-secondary mb-8">
                {role === "farmer"
                  ? "Create your account and start selling today"
                  : "Create your account and start buying"}
              </p>

              <form onSubmit={handleSubmit} className="bg-white rounded-xl p-8 shadow-sm border border-border">
                {/* Name */}
                <div className="mb-6">
                  <label className="block text-sm font-semibold text-foreground mb-2">Full Name</label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    placeholder="Your full name"
                    className="w-full px-4 py-3 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                    required
                  />
                </div>

                {/* Email */}
                <div className="mb-6">
                  <label className="block text-sm font-semibold text-foreground mb-2">Email</label>
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    placeholder="your@email.com"
                    className="w-full px-4 py-3 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                    required
                  />
                </div>

                {/* Phone */}
                <div className="mb-6">
                  <label className="block text-sm font-semibold text-foreground mb-2">Phone Number</label>
                  <input
                    type="tel"
                    name="phone"
                    value={formData.phone}
                    onChange={handleInputChange}
                    placeholder="+254 7XX XXX XXX"
                    className="w-full px-4 py-3 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                    required
                  />
                </div>

                {/* Location */}
                <div className="mb-6">
                  <label className="block text-sm font-semibold text-foreground mb-2">Location</label>
                  <input
                    type="text"
                    name="location"
                    value={formData.location}
                    onChange={handleInputChange}
                    placeholder="Your city/county"
                    className="w-full px-4 py-3 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                    required
                  />
                </div>

                {/* Farmer-specific fields */}
                {role === "farmer" && (
                  <>
                    <div className="mb-6">
                      <label className="block text-sm font-semibold text-foreground mb-2">Farm Size (acres)</label>
                      <input
                        type="text"
                        name="farmSize"
                        value={formData.farmSize}
                        onChange={handleInputChange}
                        placeholder="e.g., 2.5"
                        className="w-full px-4 py-3 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      />
                    </div>

                    <div className="mb-6">
                      <label className="block text-sm font-semibold text-foreground mb-2">Crops You Grow</label>
                      <textarea
                        name="crops"
                        value={formData.crops}
                        onChange={handleInputChange}
                        placeholder="e.g., Bananas, Avocados, Tea"
                        className="w-full px-4 py-3 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                        rows={3}
                      />
                    </div>
                  </>
                )}

                {/* Submit Button */}
                <button
                  type="submit"
                  className="w-full bg-primary hover:bg-primary-dark text-white font-bold py-3 rounded-lg transition-smooth flex items-center justify-center gap-2"
                >
                  Create Account
                  <ArrowRight size={20} />
                </button>

                {/* Login Link */}
                <p className="text-center text-foreground-secondary mt-6">
                  Already have an account?{" "}
                  <Link href="/login" className="text-primary hover:text-primary-dark font-semibold">
                    Sign in
                  </Link>
                </p>
              </form>
            </div>
          )}
        </div>
      </div>
    </main>
  )
}
