'use client'

import { useState } from 'react'
import Link from 'next/link'
import { ArrowRight, Play } from 'lucide-react'

export function HeroSection() {
  const [isVideoPlaying, setIsVideoPlaying] = useState(false)

  return (
    <div className="relative bg-gradient-to-r from-primary-600 to-primary-800 text-white">
      {/* Background Pattern */}
      <div className="absolute inset-0">
        <div className="absolute inset-0 bg-black opacity-20"></div>
        <div className="absolute inset-0">
          <div className="h-full w-full bg-gradient-to-r from-transparent via-white/10 to-transparent"></div>
        </div>
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Left Content */}
          <div className="space-y-8">
            <div className="space-y-4">
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold leading-tight">
                Discover Amazing Products at
                <span className="block text-yellow-300">Unbeatable Prices</span>
              </h1>
              <p className="text-xl text-gray-100 max-w-2xl">
                Shop our curated collection of premium products with fast shipping, 
                secure payments, and exceptional customer service.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-4">
              <Link
                href="/products"
                className="inline-flex items-center justify-center px-8 py-3 bg-white text-primary-600 font-medium rounded-lg hover:bg-gray-100 transition-colors duration-200"
              >
                Start Shopping
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
              
              <button
                onClick={() => setIsVideoPlaying(true)}
                className="inline-flex items-center justify-center px-8 py-3 bg-transparent border-2 border-white text-white font-medium rounded-lg hover:bg-white hover:text-primary-600 transition-colors duration-200"
              >
                <Play className="mr-2 h-5 w-5" />
                Watch Demo
              </button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-8 py-8">
              <div>
                <div className="text-3xl font-bold text-yellow-300">10K+</div>
                <div className="text-gray-200">Products</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-yellow-300">24/7</div>
                <div className="text-gray-200">Support</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-yellow-300">100%</div>
                <div className="text-gray-200">Satisfaction</div>
              </div>
            </div>
          </div>

          {/* Right Content - Hero Image/Video */}
          <div className="relative">
            <div className="relative aspect-square rounded-2xl overflow-hidden shadow-2xl">
              {/* Placeholder for hero image */}
              <div className="w-full h-full bg-gradient-to-br from-yellow-400 to-primary-600 flex items-center justify-center">
                <div className="text-center text-white">
                  <div className="text-6xl mb-4">🛍️</div>
                  <div className="text-2xl font-semibold">Premium Shopping Experience</div>
                </div>
              </div>
              
              {/* Floating badges */}
              <div className="absolute top-4 left-4 bg-white/90 backdrop-blur-sm rounded-lg px-3 py-2 text-gray-800 text-sm font-medium">
                ✨ New Arrivals
              </div>
              
              <div className="absolute top-4 right-4 bg-red-500 text-white rounded-lg px-3 py-2 text-sm font-medium">
                🔥 Hot Deals
              </div>
              
              <div className="absolute bottom-4 left-4 bg-green-500 text-white rounded-lg px-3 py-2 text-sm font-medium">
                ✅ Free Shipping
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Video Modal (when playing) */}
      {isVideoPlaying && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[80vh] overflow-hidden">
            <div className="flex justify-between items-center p-4 border-b">
              <h3 className="text-lg font-semibold">Product Demo</h3>
              <button
                onClick={() => setIsVideoPlaying(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="aspect-video bg-black flex items-center justify-center">
              <div className="text-white text-center">
                <div className="text-4xl mb-4">▶️</div>
                <div>Video demo would play here</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
