import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { ClerkProvider } from '@clerk/nextjs'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'QuarryAI',
  description: 'Multi-tenant AI Voice Agent Platform',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <ClerkProvider
      signInForceRedirectUrl="/dashboard"
      signUpForceRedirectUrl="/dashboard"
      signInUrl="/sign-in"
      signUpUrl="/sign-up"
    >
      <html lang="en">
        <body className={inter.className}>
          {children}
        </body>
      </html>
    </ClerkProvider>
  )
}
