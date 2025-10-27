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
    ...(isAuthenticated ? [{ label: "Dashboard", href: "/dashboard" }] : []),
    { label: "Contact", href: "/contact" },
  ]

  return (
    <nav className="fixed top-4 left-1/2 transform -translate-x-1/2 w-[90%] md:w-[85%] z-50">
      {/* Glossy floating navbar */}
      <div className="glass rounded-2xl px-6 py-4 flex justify-between items-center shadow-lg">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2 group">
          <div className="w-8 h-8 bg-gradient-to-br from-primary to-primary-dark rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-lg">A</span>
          </div>
          <span className="text-xl font-bold text-foreground hidden sm:inline group-hover:text-primary transition-smooth">
            AgriConnect
          </span>
        </Link>

        {/* Desktop Navigation */}
        <ul className="hidden md:flex gap-8 items-center">
          {navLinks.map((link) => (
            <li key={link.href}>
              <Link
                href={link.href}
                className="text-black hover:text-foreground-secondary font-medium transition-smooth"
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
              <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-primary/10">
                <span className="text-sm font-medium text-foreground">{user?.name}</span>
                <span className="text-xs bg-primary text-white px-2 py-1 rounded-full">{user?.role}</span>
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
              <Link href="/login" className="text-foreground hover:text-primary font-medium transition-smooth">
                Sign In
              </Link>
              <Link
                href="/signup"
                className="bg-primary hover:bg-primary-dark text-white font-semibold px-5 py-2 rounded-full shadow-md transition-smooth"
              >
                Sign Up
              </Link>
            </>
          )}
        </div>

        {/* Mobile Menu Button */}
        <button onClick={toggleMenu} className="md:hidden text-foreground hover:text-primary transition-smooth">
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
                  className="text-foreground-secondary hover:text-primary font-medium transition-smooth block"
                  onClick={() => setIsOpen(false)}
                >
                  {link.label}
                </Link>
              </li>
            ))}
            {isAuthenticated ? (
              <>
                <div className="border-t border-white/20 pt-4 mt-4">
                  <p className="text-sm font-medium text-foreground mb-2">{user?.name}</p>
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
                  className="w-full text-center bg-background-secondary hover:bg-border text-foreground font-semibold py-2 rounded-full transition-smooth"
                  onClick={() => setIsOpen(false)}
                >
                  Sign In
                </Link>
                <Link
                  href="/signup"
                  className="w-full text-center bg-primary hover:bg-primary-dark text-white font-semibold py-2 rounded-full transition-smooth"
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
