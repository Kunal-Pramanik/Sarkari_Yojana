'use client'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { isLoggedIn } from '@/lib/auth'
import ChatWindow from "@/components/ChatWindow"

export default function Home() {
  const router = useRouter()
  const [checking, setChecking] = useState(true)

  useEffect(() => {
    if (!isLoggedIn()) {
      router.push('/login')
    } else {
      setChecking(false)
    }
  }, [])

  if (checking) {
    return (
      <div className="flex h-screen items-center justify-center" style={{ background: "var(--bg)" }}>
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-orange-500 mb-3">
            <span className="text-white text-xl font-bold">स</span>
          </div>
          <p className="text-gray-400 text-sm">Loading...</p>
        </div>
      </div>
    )
  }

  return (
    <main className="flex h-screen overflow-hidden" style={{ background: "var(--bg)" }}>
      <ChatWindow />
    </main>
  )
}