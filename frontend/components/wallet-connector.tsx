"use client"

import { useState } from "react"
import { Wallet, LogOut } from "lucide-react"

export default function WalletConnector() {
  const [isConnected, setIsConnected] = useState(false)
  const [walletAddress, setWalletAddress] = useState("")

  const connectWallet = async () => {
    // Mock wallet connection
    const mockAddress = "0x" + Math.random().toString(16).slice(2, 10).toUpperCase()
    setWalletAddress(mockAddress)
    setIsConnected(true)
  }

  const disconnectWallet = () => {
    setIsConnected(false)
    setWalletAddress("")
  }

  if (isConnected) {
    return (
      <div className="flex items-center gap-3">
        <div className="bg-primary/10 text-primary px-4 py-2 rounded-full text-sm font-semibold">
          {walletAddress.slice(0, 6)}...{walletAddress.slice(-4)}
        </div>
        <button
          onClick={disconnectWallet}
          className="text-foreground-secondary hover:text-foreground transition-smooth"
        >
          <LogOut size={18} />
        </button>
      </div>
    )
  }

  return (
    <button
      onClick={connectWallet}
      className="flex items-center gap-2 bg-primary hover:bg-primary-dark text-white font-semibold px-5 py-2 rounded-full shadow-md transition-smooth"
    >
      <Wallet size={18} />
      <span>Connect Wallet</span>
    </button>
  )
}
