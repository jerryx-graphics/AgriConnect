"use client"

import { ProtectedRoute } from "@/components/protected-route"
import { useAuth } from "@/lib/auth-context"
import Navbar from "@/components/navbar"
import { ArrowLeft, Bell, Lock, Eye } from "lucide-react"
import Link from "next/link"
import { useState } from "react"

function SettingsContent() {
  const { user } = useAuth()
  const [settings, setSettings] = useState({
    emailNotifications: true,
    smsNotifications: true,
    orderUpdates: true,
    marketingEmails: false,
  })

  const handleToggle = (key: string) => {
    setSettings((prev) => ({ ...prev, [key]: !prev[key] }))
  }

  return (
    <main className="min-h-screen bg-background-secondary">
      <Navbar />

      <div className="pt-32 pb-12 px-6">
        <div className="max-w-2xl mx-auto">
          <Link href="/dashboard" className="flex items-center gap-2 text-primary hover:text-primary-dark mb-6">
            <ArrowLeft size={20} />
            Back to Dashboard
          </Link>

          <h1 className="text-4xl font-bold text-foreground mb-2">Settings</h1>
          <p className="text-foreground-secondary mb-8">Manage your account preferences</p>

          {/* Notifications */}
          <div className="bg-white rounded-xl p-6 shadow-sm border border-border mb-6">
            <div className="flex items-center gap-3 mb-6">
              <Bell className="text-primary" size={24} />
              <h2 className="text-2xl font-bold text-foreground">Notifications</h2>
            </div>

            <div className="space-y-4">
              {[
                { key: "emailNotifications", label: "Email Notifications", desc: "Receive updates via email" },
                { key: "smsNotifications", label: "SMS Notifications", desc: "Receive updates via SMS" },
                { key: "orderUpdates", label: "Order Updates", desc: "Get notified about order status changes" },
                { key: "marketingEmails", label: "Marketing Emails", desc: "Receive promotional offers" },
              ].map((item) => (
                <div key={item.key} className="flex items-center justify-between p-4 border border-border rounded-lg">
                  <div>
                    <p className="font-semibold text-foreground">{item.label}</p>
                    <p className="text-sm text-foreground-secondary">{item.desc}</p>
                  </div>
                  <button
                    onClick={() => handleToggle(item.key)}
                    className={`relative inline-flex h-8 w-14 items-center rounded-full transition-colors ${
                      settings[item.key as keyof typeof settings] ? "bg-primary" : "bg-gray-300"
                    }`}
                  >
                    <span
                      className={`inline-block h-6 w-6 transform rounded-full bg-white transition-transform ${
                        settings[item.key as keyof typeof settings] ? "translate-x-7" : "translate-x-1"
                      }`}
                    />
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Security */}
          <div className="bg-white rounded-xl p-6 shadow-sm border border-border">
            <div className="flex items-center gap-3 mb-6">
              <Lock className="text-primary" size={24} />
              <h2 className="text-2xl font-bold text-foreground">Security</h2>
            </div>

            <div className="space-y-4">
              <button className="w-full flex items-center justify-between p-4 border border-border rounded-lg hover:bg-background-secondary transition-smooth">
                <div className="text-left">
                  <p className="font-semibold text-foreground">Change Password</p>
                  <p className="text-sm text-foreground-secondary">Update your password regularly</p>
                </div>
                <Eye size={20} className="text-foreground-secondary" />
              </button>

              <button className="w-full flex items-center justify-between p-4 border border-border rounded-lg hover:bg-background-secondary transition-smooth">
                <div className="text-left">
                  <p className="font-semibold text-foreground">Two-Factor Authentication</p>
                  <p className="text-sm text-foreground-secondary">Add an extra layer of security</p>
                </div>
                <span className="text-xs bg-yellow-100 text-yellow-700 px-3 py-1 rounded-full">Disabled</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}

export default function SettingsPage() {
  return (
    <ProtectedRoute>
      <SettingsContent />
    </ProtectedRoute>
  )
}
