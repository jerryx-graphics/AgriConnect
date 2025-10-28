"use client"

import type React from "react"
import { createContext, useContext, useState, useEffect } from "react"
import { apiClient } from "./api"

interface User {
  id: string
  email: string
  first_name: string
  last_name: string
  role: "farmer" | "buyer" | "transporter" | "cooperative" | "admin"
  phone?: string
  location?: string
  is_verified?: boolean
  profile?: any
}

interface AuthContextType {
  user: User | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  signup: (email: string, password: string, firstName: string, lastName: string, role: string, phone?: string) => Promise<void>
  logout: () => void
  isAuthenticated: boolean
  refreshProfile: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Check if user is logged in on mount and fetch profile
  useEffect(() => {
    const initializeAuth = async () => {
      if (apiClient.isAuthenticated()) {
        try {
          const response = await apiClient.getProfile()
          if (response.data) {
            setUser(response.data)
            localStorage.setItem("agriconnect_user", JSON.stringify(response.data))
          } else {
            // Token might be invalid, clear it
            apiClient.logout()
          }
        } catch (error) {
          console.error("Failed to fetch user profile:", error)
          apiClient.logout()
        }
      }
      setIsLoading(false)
    }

    initializeAuth()
  }, [])

  const login = async (email: string, password: string) => {
    setIsLoading(true)
    try {
      const response = await apiClient.login(email, password)

      if (response.data && (response.data as any).user) {
        setUser((response.data as any).user)
        localStorage.setItem("agriconnect_user", JSON.stringify((response.data as any).user))
      } else {
        throw new Error(response.error || "Login failed")
      }
    } catch (error) {
      console.error("Login failed:", error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const signup = async (
    email: string,
    password: string,
    firstName: string,
    lastName: string,
    role: string,
    phone?: string
  ) => {
    setIsLoading(true)
    try {
      const response = await apiClient.register({
        email,
        password,
        first_name: firstName,
        last_name: lastName,
        role: role.toLowerCase(),
        phone
      })

      if (response.data) {
        // After successful registration, log the user in
        await login(email, password)
      } else {
        throw new Error(response.error || "Registration failed")
      }
    } catch (error) {
      console.error("Signup failed:", error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const refreshProfile = async () => {
    try {
      const response = await apiClient.getProfile()
      if (response.data) {
        setUser(response.data)
        localStorage.setItem("agriconnect_user", JSON.stringify(response.data))
      }
    } catch (error) {
      console.error("Failed to refresh profile:", error)
    }
  }

  const logout = () => {
    setUser(null)
    apiClient.logout()
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        login,
        signup,
        logout,
        isAuthenticated: !!user,
        refreshProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
