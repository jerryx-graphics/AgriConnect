"use client"

import { useState } from "react"
import Link from "next/link"
import { Menu, X, LogOut } from "lucide-react"
import { useAuth } from "@/lib/auth-context"
import { useRouter } from "next/navigation"

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false)
  const { user, isAuthenticated, logout } = useAuth()
  const router = useRouter()

  const toggleMenu = () => setIsOpen(!isOpen)

  const handleLogout = () => {
    logout()
    router.push("/")
    setIsOpen(false)
  }

  const navLinks = [
    { label: "Home", href: "/" },
    { label: "Marketplace", href: "/marketplace" },
    ...(isAuthenticated ? [
      { label: "Dashboard", href: "/dashboard" },
      { label: "Payments", href: "/payments" },
      { label: "Blockchain", href: "/blockchain" },
      { label: "AI Insights", href: "/insights" },
      { label: "Deliveries", href: "/deliveries" },
      { label: "Notifications", href: "/notifications" }
    ] : []),
    { label: "Contact", href: "/contact" },
  ]

  return (
    <nav className="fixed top-4 left-1/2 transform -translate-x-1/2 w-[90%] md:w-[85%] z-50">
      {/* Glossy floating navbar */}
      <div className="glass rounded-2xl px-6 py-4 flex justify-between items-center shadow-lg">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2 group">
          
          <span className="text-xl font-bold text-foreground hidden sm:inline group-hover:text-green-600 transition-smooth">
            AgriConnect
          </span>
        </Link>

        {/* Desktop Navigation */}
        <ul className="hidden md:flex gap-8 items-center">
          {navLinks.map((link) => (
            <li key={link.href}>
              <Link
                href={link.href}
                className="text-gray-700 hover:text-green-600 font-medium transition-smooth"
              >
                {link.label}
              </Link>
            </li>
          ))}
        </ul>

        {/* Authentication buttons and user menu */}
        <div className="hidden md:flex items-center gap-3">
          {isAuthenticated ? (
            <>
              <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-green-100">
                <span className="text-sm font-medium text-gray-900">{user?.first_name} {user?.last_name}</span>
                <span className="text-xs bg-green-600 text-white px-2 py-1 rounded-full">{user?.role}</span>
              </div>
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 bg-red-500 hover:bg-red-600 text-white font-semibold px-4 py-2 rounded-full shadow-md transition-smooth"
              >
                <LogOut size={18} />
                <span>Logout</span>
              </button>
            </>
          ) : (
            <>
              <Link href="/login" className="text-gray-700 hover:text-green-600 font-medium transition-smooth">
                Sign In
              </Link>
              <Link
                href="/signup"
                className="bg-green-600 hover:bg-green-700 text-white font-semibold px-5 py-2 rounded-full shadow-md transition-smooth"
              >
                Sign Up
              </Link>
            </>
          )}
        </div>

        {/* Mobile Menu Button */}
        <button onClick={toggleMenu} className="md:hidden text-gray-700 hover:text-green-600 transition-smooth">
          {isOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Mobile Menu */}
      {isOpen && (
        <div className="glass rounded-2xl mt-2 px-6 py-4 md:hidden shadow-lg animate-in fade-in slide-in-from-top-2">
          <ul className="flex flex-col gap-4">
            {navLinks.map((link) => (
              <li key={link.href}>
                <Link
                  href={link.href}
                  className="text-gray-600 hover:text-green-600 font-medium transition-smooth block"
                  onClick={() => setIsOpen(false)}
                >
                  {link.label}
                </Link>
              </li>
            ))}
            {isAuthenticated ? (
              <>
                <div className="border-t border-white/20 pt-4 mt-4">
                  <p className="text-sm font-medium text-gray-900 mb-2">{user?.first_name} {user?.last_name}</p>
                  <button
                    onClick={handleLogout}
                    className="w-full flex items-center justify-center gap-2 bg-red-500 hover:bg-red-600 text-white font-semibold py-2 rounded-full transition-smooth"
                  >
                    <LogOut size={18} />
                    Logout
                  </button>
                </div>
              </>
            ) : (
              <>
                <Link
                  href="/login"
                  className="w-full text-center bg-gray-100 hover:bg-gray-200 text-gray-900 font-semibold py-2 rounded-full transition-smooth"
                  onClick={() => setIsOpen(false)}
                >
                  Sign In
                </Link>
                <Link
                  href="/signup"
                  className="w-full text-center bg-green-600 hover:bg-green-700 text-white font-semibold py-2 rounded-full transition-smooth"
                  onClick={() => setIsOpen(false)}
                >
                  Sign Up
                </Link>
              </>
            )}
          </ul>
        </div>
      )}
    </nav>
  )
}
