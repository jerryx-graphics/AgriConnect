"use client"

import { useState } from "react"
import Link from "next/link"
import { useAuth } from "@/lib/auth-context"
import { useRouter, usePathname } from "next/navigation"
import {
  Home,
  Package,
  ShoppingCart,
  CreditCard,
  Settings,
  User,
  LogOut,
  Menu,
  X,
  Store,
  TrendingUp,
  Bell,
  Search,
  Plus,
  BarChart3,
  Truck,
  Shield,
  Phone,
  Mail,
  MapPin,
  ChevronRight
} from "lucide-react"

interface DashboardLayoutProps {
  children: React.ReactNode
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const { user, logout } = useAuth()
  const router = useRouter()
  const pathname = usePathname()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const isFarmer = user?.role === "farmer"
  const isBuyer = user?.role === "buyer"
  const isTransporter = user?.role === "transporter"

  const handleLogout = () => {
    logout()
    router.push("/")
  }

  const navigationItems = [
    {
      name: "Dashboard",
      href: "/dashboard",
      icon: Home,
      show: true
    },
    {
      name: "Marketplace",
      href: "/dashboard/marketplace",
      icon: Store,
      show: true
    },
    {
      name: "My Products",
      href: "/dashboard/products",
      icon: Package,
      show: isFarmer
    },
    {
      name: "Analytics",
      href: "/dashboard/analytics",
      icon: TrendingUp,
      show: isFarmer
    },
    {
      name: "Orders",
      href: "/dashboard/orders",
      icon: ShoppingCart,
      show: true
    },
    {
      name: "Payments",
      href: "/payments",
      icon: CreditCard,
      show: true
    },
    {
      name: "Blockchain",
      href: "/blockchain",
      icon: Shield,
      show: isFarmer
    },
    {
      name: "Deliveries",
      href: "/deliveries",
      icon: Truck,
      show: isTransporter || isBuyer
    },
    {
      name: "Insights",
      href: "/insights",
      icon: BarChart3,
      show: isFarmer
    },
    {
      name: "Notifications",
      href: "/notifications",
      icon: Bell,
      show: true
    }
  ]

  const isActiveRoute = (href: string) => {
    if (href === "/dashboard") {
      return pathname === "/dashboard"
    }
    return pathname.startsWith(href)
  }

  return (
    <div className="h-screen bg-green-50 flex overflow-hidden">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-xl transform transition-transform duration-300 ease-in-out lg:relative lg:translate-x-0 flex-shrink-0
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="flex flex-col h-full">
          {/* Logo section - Fixed */}
          <div className="flex items-center justify-between h-16 px-6 border-b border-green-100 flex-shrink-0">
            <Link href="/dashboard" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-green-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">A</span>
              </div>
              <span className="text-xl font-bold text-green-800">AgriConnect</span>
            </Link>
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden p-1 rounded-md hover:bg-green-100"
            >
              <X size={20} className="text-green-600" />
            </button>
          </div>

          {/* User info - Fixed */}
          <div className="p-6 border-b border-green-100 flex-shrink-0">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                <User size={20} className="text-green-600" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-green-900 truncate">
                  {user?.first_name} {user?.last_name}
                </p>
                <p className="text-xs text-green-600 capitalize">{user?.role}</p>
              </div>
            </div>
          </div>

          {/* Scrollable content area */}
          <div className="flex-1 overflow-y-auto">
            {/* Navigation */}
            <nav className="px-4 py-6 space-y-1">
              {navigationItems
                .filter(item => item.show)
                .map((item) => {
                  const isActive = isActiveRoute(item.href)
                  return (
                    <Link
                      key={item.name}
                      href={item.href}
                      className={`
                        flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-all duration-200
                        ${isActive
                          ? 'bg-green-100 text-green-800 shadow-sm'
                          : 'text-green-700 hover:bg-green-50 hover:text-green-800'
                        }
                      `}
                      onClick={() => setSidebarOpen(false)}
                    >
                      <item.icon
                        size={20}
                        className={`mr-3 ${isActive ? 'text-green-600' : 'text-green-500'}`}
                      />
                      {item.name}
                      {isActive && (
                        <ChevronRight size={16} className="ml-auto text-green-600" />
                      )}
                    </Link>
                  )
                })}
            </nav>

            {/* Quick actions */}
            <div className="p-4 border-t border-green-100">
              {isFarmer && (
                <Link
                  href="/dashboard/create-listing"
                  className="flex items-center justify-center w-full px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700 transition-colors"
                >
                  <Plus size={16} className="mr-2" />
                  Add Product
                </Link>
              )}
              {isBuyer && (
                <Link
                  href="/dashboard/marketplace"
                  className="flex items-center justify-center w-full px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700 transition-colors"
                >
                  <Search size={16} className="mr-2" />
                  Browse Products
                </Link>
              )}
            </div>

            {/* Bottom section */}
            <div className="p-4 border-t border-green-100 space-y-1">
              <Link
                href="/dashboard/profile"
                className="flex items-center px-4 py-3 text-sm font-medium text-green-700 rounded-lg hover:bg-green-50 hover:text-green-800 transition-all duration-200"
              >
                <Settings size={20} className="mr-3 text-green-500" />
                Settings
              </Link>
              <button
                onClick={handleLogout}
                className="flex items-center w-full px-4 py-3 text-sm font-medium text-red-600 rounded-lg hover:bg-red-50 transition-all duration-200"
              >
                <LogOut size={20} className="mr-3" />
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0 h-full">
        {/* Top header - Fixed */}
        <header className="bg-white shadow-sm border-b border-green-100 flex-shrink-0">
          <div className="flex items-center justify-between h-16 px-6">
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden p-2 rounded-md hover:bg-green-100"
            >
              <Menu size={20} className="text-green-600" />
            </button>

            <div className="flex items-center space-x-4 ml-auto">
              {/* Contact info for farmers */}
              {isFarmer && (
                <div className="hidden md:flex items-center space-x-4 text-sm text-green-600">
                  <div className="flex items-center space-x-1">
                    <Phone size={14} />
                    <span>+254-700-000-000</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Mail size={14} />
                    <span>support@agriconnect.co.ke</span>
                  </div>
                </div>
              )}

              {/* Notifications */}
              <button className="relative p-2 rounded-lg hover:bg-green-50 transition-colors">
                <Bell size={20} className="text-green-600" />
                <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full"></span>
              </button>
            </div>
          </div>
        </header>

        {/* Page content - Scrollable */}
        <main className="flex-1 overflow-y-auto">
          <div className="p-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}