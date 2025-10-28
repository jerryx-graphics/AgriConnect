"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { ProtectedRoute } from "@/components/protected-route"
import { useAuth } from "@/lib/auth-context"
import Navbar from "@/components/navbar"
import {
  Bell,
  BellRing,
  CheckCircle,
  Clock,
  Mail,
  MessageSquare,
  Package,
  CreditCard,
  Truck,
  Settings,
  Check
} from "lucide-react"
import Link from "next/link"
import { apiClient } from "@/lib/api"

interface Notification {
  id: string
  title: string
  message: string
  notification_type: string
  is_read: boolean
  created_at: string
  metadata?: any
}

interface NotificationSettings {
  email_notifications: boolean
  sms_notifications: boolean
  push_notifications: boolean
  order_updates: boolean
  payment_alerts: boolean
  marketing_emails: boolean
  delivery_notifications: boolean
}

function NotificationsContent() {
  const { user } = useAuth()
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [settings, setSettings] = useState<NotificationSettings>({
    email_notifications: true,
    sms_notifications: true,
    push_notifications: true,
    order_updates: true,
    payment_alerts: true,
    marketing_emails: false,
    delivery_notifications: true
  })
  const [isLoading, setIsLoading] = useState(true)
  const [activeTab, setActiveTab] = useState("notifications")
  const [error, setError] = useState("")

  useEffect(() => {
    fetchNotificationsData()
  }, [])

  const fetchNotificationsData = async () => {
    try {
      const [notificationsResponse, settingsResponse] = await Promise.all([
        apiClient.getNotifications(),
        apiClient.getNotificationSettings()
      ])

      if (notificationsResponse.data) {
        setNotifications(notificationsResponse.data.results || notificationsResponse.data)
      }

      if (settingsResponse.data) {
        setSettings({ ...settings, ...settingsResponse.data })
      }
    } catch (err) {
      setError("Failed to load notifications")
      console.error("Error fetching notifications:", err)
    } finally {
      setIsLoading(false)
    }
  }

  const markAsRead = async (notificationId: string) => {
    try {
      await apiClient.markNotificationAsRead(notificationId)
      setNotifications(notifications.map(n =>
        n.id === notificationId ? { ...n, is_read: true } : n
      ))
    } catch (err) {
      console.error("Error marking notification as read:", err)
    }
  }

  const markAllAsRead = async () => {
    try {
      const unreadNotifications = notifications.filter(n => !n.is_read)
      await Promise.all(unreadNotifications.map(n => apiClient.markNotificationAsRead(n.id)))
      setNotifications(notifications.map(n => ({ ...n, is_read: true })))
    } catch (err) {
      console.error("Error marking all notifications as read:", err)
    }
  }

  const updateSettings = async (newSettings: Partial<NotificationSettings>) => {
    try {
      const updatedSettings = { ...settings, ...newSettings }
      await apiClient.updateNotificationSettings(updatedSettings)
      setSettings(updatedSettings)
    } catch (err) {
      console.error("Error updating settings:", err)
    }
  }

  const getNotificationIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'order':
        return <Package size={20} className="text-blue-600" />
      case 'payment':
        return <CreditCard size={20} className="text-green-600" />
      case 'delivery':
        return <Truck size={20} className="text-purple-600" />
      case 'message':
        return <MessageSquare size={20} className="text-orange-600" />
      case 'email':
        return <Mail size={20} className="text-red-600" />
      default:
        return <Bell size={20} className="text-gray-600" />
    }
  }

  // Mock notifications if none from API
  const mockNotifications: Notification[] = [
    {
      id: "not1",
      title: "Order Confirmed",
      message: "Your order #ORD001 has been confirmed and is being prepared for shipment.",
      notification_type: "order",
      is_read: false,
      created_at: "2025-10-28T10:00:00Z"
    },
    {
      id: "not2",
      title: "Payment Successful",
      message: "Payment of KES 12,500 for order #ORD001 has been processed successfully.",
      notification_type: "payment",
      is_read: false,
      created_at: "2025-10-28T09:30:00Z"
    },
    {
      id: "not3",
      title: "Delivery Update",
      message: "Your delivery is out for delivery and will arrive between 2-4 PM today.",
      notification_type: "delivery",
      is_read: true,
      created_at: "2025-10-28T08:00:00Z"
    },
    {
      id: "not4",
      title: "New Message",
      message: "You have received a new message from farmer John Kiprotich about your order.",
      notification_type: "message",
      is_read: true,
      created_at: "2025-10-27T16:00:00Z"
    },
    {
      id: "not5",
      title: "Price Alert",
      message: "The price of bananas has increased by 15% in your area. Consider adjusting your inventory.",
      notification_type: "alert",
      is_read: true,
      created_at: "2025-10-27T14:00:00Z"
    }
  ]

  const displayNotifications = notifications.length > 0 ? notifications : mockNotifications
  const unreadCount = displayNotifications.filter(n => !n.is_read).length

  return (
    <main className="min-h-screen bg-background-secondary">
      <Navbar />

      <div className="pt-32 pb-12 px-6">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="flex justify-between items-start mb-8">
            <div>
              <h1 className="text-4xl font-bold text-foreground mb-2">Notifications</h1>
              <p className="text-foreground-secondary">
                Stay updated with your orders, payments, and messages
              </p>
            </div>
            {unreadCount > 0 && (
              <button
                onClick={markAllAsRead}
                className="flex items-center gap-2 bg-primary text-white px-4 py-2 rounded-lg hover:bg-primary-dark transition-smooth"
              >
                <Check size={20} />
                Mark All Read
              </button>
            )}
          </div>

          {/* Notification Stats */}
          <div className="grid md:grid-cols-3 gap-6 mb-8">
            <div className="bg-white rounded-xl p-6 shadow-sm border border-border">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-foreground-secondary mb-1">Total Notifications</p>
                  <p className="text-3xl font-bold text-foreground">{displayNotifications.length}</p>
                </div>
                <Bell className="text-primary" size={32} />
              </div>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-sm border border-border">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-foreground-secondary mb-1">Unread</p>
                  <p className="text-3xl font-bold text-foreground">{unreadCount}</p>
                </div>
                <BellRing className="text-accent" size={32} />
              </div>
              {unreadCount > 0 && (
                <p className="text-xs text-accent mt-2">Requires attention</p>
              )}
            </div>

            <div className="bg-white rounded-xl p-6 shadow-sm border border-border">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-foreground-secondary mb-1">Today</p>
                  <p className="text-3xl font-bold text-foreground">
                    {displayNotifications.filter(n =>
                      new Date(n.created_at).toDateString() === new Date().toDateString()
                    ).length}
                  </p>
                </div>
                <Clock className="text-green-600" size={32} />
              </div>
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
                <button
                  onClick={() => setActiveTab("notifications")}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === "notifications"
                      ? "border-primary text-primary"
                      : "border-transparent text-foreground-secondary hover:text-foreground"
                  }`}
                >
                  Notifications
                  {unreadCount > 0 && (
                    <span className="ml-2 bg-red-500 text-white text-xs rounded-full px-2 py-1">
                      {unreadCount}
                    </span>
                  )}
                </button>
                <button
                  onClick={() => setActiveTab("settings")}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === "settings"
                      ? "border-primary text-primary"
                      : "border-transparent text-foreground-secondary hover:text-foreground"
                  }`}
                >
                  Settings
                </button>
              </nav>
            </div>

            <div className="p-6">
              {isLoading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
                  <p className="text-foreground-secondary">Loading notifications...</p>
                </div>
              ) : activeTab === "notifications" ? (
                displayNotifications.length === 0 ? (
                  <div className="text-center py-8">
                    <Bell size={48} className="text-foreground-secondary mx-auto mb-4" />
                    <p className="text-lg text-foreground-secondary mb-2">No notifications</p>
                    <p className="text-foreground-secondary">You're all caught up!</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {displayNotifications.map((notification) => (
                      <div
                        key={notification.id}
                        className={`border border-border rounded-lg p-4 hover:shadow-md transition-smooth cursor-pointer ${
                          !notification.is_read ? 'bg-blue-50 border-blue-200' : 'bg-white'
                        }`}
                        onClick={() => !notification.is_read && markAsRead(notification.id)}
                      >
                        <div className="flex items-start gap-4">
                          <div className="flex-shrink-0 mt-1">
                            {getNotificationIcon(notification.notification_type)}
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex justify-between items-start mb-2">
                              <h3 className={`font-semibold ${
                                !notification.is_read ? 'text-foreground' : 'text-foreground-secondary'
                              }`}>
                                {notification.title}
                              </h3>
                              <div className="flex items-center gap-2">
                                <span className="text-sm text-foreground-secondary">
                                  {new Date(notification.created_at).toLocaleDateString()}
                                </span>
                                {!notification.is_read && (
                                  <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                                )}
                              </div>
                            </div>
                            <p className="text-foreground-secondary text-sm mb-2">
                              {notification.message}
                            </p>
                            <div className="flex items-center gap-4">
                              <span className={`text-xs px-2 py-1 rounded-full ${
                                notification.notification_type === 'order'
                                  ? 'bg-blue-100 text-blue-800'
                                  : notification.notification_type === 'payment'
                                  ? 'bg-green-100 text-green-800'
                                  : notification.notification_type === 'delivery'
                                  ? 'bg-purple-100 text-purple-800'
                                  : 'bg-gray-100 text-gray-800'
                              }`}>
                                {notification.notification_type.toUpperCase()}
                              </span>
                              {!notification.is_read && (
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation()
                                    markAsRead(notification.id)
                                  }}
                                  className="text-primary hover:text-primary-dark text-xs font-medium"
                                >
                                  Mark as read
                                </button>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )
              ) : (
                <div className="space-y-6">
                  <h3 className="text-lg font-bold text-foreground">Notification Preferences</h3>

                  <div className="space-y-4">
                    <div className="flex items-center justify-between py-3 border-b border-border">
                      <div>
                        <p className="font-semibold text-foreground">Email Notifications</p>
                        <p className="text-sm text-foreground-secondary">Receive notifications via email</p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={settings.email_notifications}
                          onChange={(e) => updateSettings({ email_notifications: e.target.checked })}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                      </label>
                    </div>

                    <div className="flex items-center justify-between py-3 border-b border-border">
                      <div>
                        <p className="font-semibold text-foreground">SMS Notifications</p>
                        <p className="text-sm text-foreground-secondary">Receive notifications via SMS</p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={settings.sms_notifications}
                          onChange={(e) => updateSettings({ sms_notifications: e.target.checked })}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                      </label>
                    </div>

                    <div className="flex items-center justify-between py-3 border-b border-border">
                      <div>
                        <p className="font-semibold text-foreground">Push Notifications</p>
                        <p className="text-sm text-foreground-secondary">Receive browser push notifications</p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={settings.push_notifications}
                          onChange={(e) => updateSettings({ push_notifications: e.target.checked })}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                      </label>
                    </div>

                    <div className="flex items-center justify-between py-3 border-b border-border">
                      <div>
                        <p className="font-semibold text-foreground">Order Updates</p>
                        <p className="text-sm text-foreground-secondary">Notifications about order status changes</p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={settings.order_updates}
                          onChange={(e) => updateSettings({ order_updates: e.target.checked })}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                      </label>
                    </div>

                    <div className="flex items-center justify-between py-3 border-b border-border">
                      <div>
                        <p className="font-semibold text-foreground">Payment Alerts</p>
                        <p className="text-sm text-foreground-secondary">Notifications about payment confirmations</p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={settings.payment_alerts}
                          onChange={(e) => updateSettings({ payment_alerts: e.target.checked })}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                      </label>
                    </div>

                    <div className="flex items-center justify-between py-3 border-b border-border">
                      <div>
                        <p className="font-semibold text-foreground">Delivery Notifications</p>
                        <p className="text-sm text-foreground-secondary">Updates about delivery status and tracking</p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={settings.delivery_notifications}
                          onChange={(e) => updateSettings({ delivery_notifications: e.target.checked })}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                      </label>
                    </div>

                    <div className="flex items-center justify-between py-3">
                      <div>
                        <p className="font-semibold text-foreground">Marketing Emails</p>
                        <p className="text-sm text-foreground-secondary">Promotional emails and newsletters</p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={settings.marketing_emails}
                          onChange={(e) => updateSettings({ marketing_emails: e.target.checked })}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                      </label>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}

export default function NotificationsPage() {
  return (
    <ProtectedRoute>
      <NotificationsContent />
    </ProtectedRoute>
  )
}