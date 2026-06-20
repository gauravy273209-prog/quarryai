import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

const isPublicRoute = createRouteMatcher([
  '/sign-in(.*)',
  '/sign-up(.*)',
])

const isLandingPage = createRouteMatcher(['/'])

export default clerkMiddleware(async (auth, request) => {
  const { userId } = await auth()

  // Redirect already-logged-in users away from landing page to dashboard
  if (userId && isLandingPage(request)) {
    return NextResponse.redirect(new URL('/dashboard', request.url))
  }

  // Protect all non-public, non-landing routes
  if (!isPublicRoute(request) && !isLandingPage(request)) {
    await auth.protect()
  }
})

export const config = {
  matcher: [
    '/((?!_next|[^?]*\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    '/(api|trpc)(.*)',
  ],
}
