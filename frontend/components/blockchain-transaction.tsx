"use client"

import { useState } from "react"
import { Copy, ExternalLink, CheckCircle } from "lucide-react"

interface BlockchainTransactionProps {
  transactionHash: string
  status: "pending" | "confirmed" | "failed"
  amount: number
  from: string
  to: string
}

export default function BlockchainTransaction({
  transactionHash,
  status,
  amount,
  from,
  to,
}: BlockchainTransactionProps) {
  const [copied, setCopied] = useState(false)

  const copyToClipboard = () => {
    navigator.clipboard.writeText(transactionHash)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const statusColors = {
    pending: "bg-yellow-100 text-yellow-700",
    confirmed: "bg-primary/10 text-primary",
    failed: "bg-red-100 text-red-700",
  }

  return (
    <div className="bg-white rounded-xl p-6 border border-border">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-bold text-foreground">Blockchain Transaction</h3>
        <span className={`px-3 py-1 rounded-full text-sm font-semibold ${statusColors[status]}`}>
          {status === "confirmed" && <CheckCircle className="inline mr-1" size={16} />}
          {status.charAt(0).toUpperCase() + status.slice(1)}
        </span>
      </div>

      <div className="space-y-4">
        {/* Transaction Hash */}
        <div>
          <p className="text-sm text-foreground-secondary mb-1">Transaction Hash</p>
          <div className="flex items-center gap-2 bg-background-secondary p-3 rounded-lg">
            <code className="text-sm font-mono text-foreground flex-1 truncate">{transactionHash}</code>
            <button
              onClick={copyToClipboard}
              className="text-foreground-secondary hover:text-foreground transition-smooth"
            >
              <Copy size={18} />
            </button>
          </div>
          {copied && <p className="text-xs text-primary mt-1">Copied to clipboard!</p>}
        </div>

        {/* Amount */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-foreground-secondary mb-1">Amount</p>
            <p className="font-bold text-foreground">KES {amount.toLocaleString()}</p>
          </div>
          <div>
            <p className="text-sm text-foreground-secondary mb-1">Network</p>
            <p className="font-bold text-foreground">Polygon</p>
          </div>
        </div>

        {/* From/To */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-foreground-secondary mb-1">From</p>
            <p className="font-mono text-sm text-foreground truncate">{from}</p>
          </div>
          <div>
            <p className="text-sm text-foreground-secondary mb-1">To</p>
            <p className="font-mono text-sm text-foreground truncate">{to}</p>
          </div>
        </div>

        {/* View on Explorer */}
        <a
          href={`https://polygonscan.com/tx/${transactionHash}`}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center justify-center gap-2 w-full bg-primary/10 hover:bg-primary/20 text-primary font-semibold py-2 rounded-lg transition-smooth"
        >
          View on Block Explorer
          <ExternalLink size={16} />
        </a>
      </div>
    </div>
  )
}
