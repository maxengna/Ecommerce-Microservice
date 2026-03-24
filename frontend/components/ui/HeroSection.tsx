'use client'

import { useState } from 'react'
import Link from 'next/link'
import { ArrowRight, Play, Sparkles, ShoppingBag, Shield, Truck } from 'lucide-react'

export function HeroSection() {
  const [isVideoPlaying, setIsVideoPlaying] = useState(false)

  return (
    <div className="relative bg-gradient-to-r from-orange-500 via-red-500 to-pink-500 text-white overflow-hidden">
      {/* Banner Carousel */}
      <div className="absolute inset-0">
        <div className="absolute inset-0 bg-black/10"></div>
        {/* Banner decoration */}
        <div className="absolute top-4 right-4 bg-yellow-400 text-red-600 rounded-lg px-4 py-2 font-bold text-lg animate-pulse">
          🔥 FLASH SALE 80% OFF
        </div>
        <div className="absolute bottom-4 left-4 bg-white text-red-600 rounded-lg px-4 py-2 font-bold">
          ⏰ Limited Time
        </div>
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16 lg:py-20">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
          {/* Left Content - Deals */}
          <div className="space-y-6">
            <div className="space-y-4">
              {/* Flash Sale Badge */}
              <div className="inline-flex items-center gap-2 bg-yellow-400 text-red-600 rounded-full px-4 py-2 text-sm font-bold">
                <span className="animate-pulse">⚡</span>
                FLASH SALE ENDS SOON
              </div>

              <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold leading-tight">
                Big Sale Today!
                <span className="block text-yellow-300">Up to 80% OFF</span>
                <span className="block text-xl sm:text-2xl lg:text-3xl text-white/90 mt-2">
                  Thousands of Deals
                </span>
              </h1>
              
              <p className="text-lg sm:text-xl text-white/90 max-w-2xl leading-relaxed">
                Don't miss out on the biggest sale of the year! Electronics, fashion, home & more at unbeatable prices.
              </p>
            </div>

            {/* Countdown Timer */}
            <div className="bg-white/20 backdrop-blur-sm rounded-xl p-4">
              <div className="text-center mb-2">
                <span className="text-sm font-semibold">FLASH SALE ENDS IN</span>
              </div>
              <div className="flex justify-center gap-2">
                <div className="bg-white text-red-600 rounded-lg px-3 py-2 text-center">
                  <div className="text-2xl font-bold">02</div>
                  <div className="text-xs">HOURS</div>
                </div>
                <div className="flex items-center text-2xl font-bold">:</div>
                <div className="bg-white text-red-600 rounded-lg px-3 py-2 text-center">
                  <div className="text-2xl font-bold">45</div>
                  <div className="text-xs">MINS</div>
                </div>
                <div className="flex items-center text-2xl font-bold">:</div>
                <div className="bg-white text-red-600 rounded-lg px-3 py-2 text-center">
                  <div className="text-2xl font-bold">30</div>
                  <div className="text-xs">SECS</div>
                </div>
              </div>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4">
              <button className="inline-flex items-center justify-center px-8 py-4 bg-yellow-400 text-red-600 font-bold rounded-xl hover:bg-yellow-300 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-1">
                <span className="mr-2">🛍️</span>
                Shop Now
                <span className="ml-2">→</span>
              </button>
              
              <button className="inline-flex items-center justify-center px-8 py-4 bg-transparent border-2 border-white text-white font-semibold rounded-xl hover:bg-white hover:text-red-600 transition-all duration-300">
                <span className="mr-2">📱</span>
                Get App
              </button>
            </div>

            {/* Deal Categories */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="bg-white/20 backdrop-blur-sm rounded-lg p-3 text-center hover:bg-white/30 transition-colors cursor-pointer">
                <div className="text-2xl mb-1">📱</div>
                <div className="text-xs font-semibold">Electronics</div>
                <div className="text-xs">70% OFF</div>
              </div>
              <div className="bg-white/20 backdrop-blur-sm rounded-lg p-3 text-center hover:bg-white/30 transition-colors cursor-pointer">
                <div className="text-2xl mb-1">👕</div>
                <div className="text-xs font-semibold">Fashion</div>
                <div className="text-xs">60% OFF</div>
              </div>
              <div className="bg-white/20 backdrop-blur-sm rounded-lg p-3 text-center hover:bg-white/30 transition-colors cursor-pointer">
                <div className="text-2xl mb-1">🏠</div>
                <div className="text-xs font-semibold">Home</div>
                <div className="text-xs">50% OFF</div>
              </div>
              <div className="bg-white/20 backdrop-blur-sm rounded-lg p-3 text-center hover:bg-white/30 transition-colors cursor-pointer">
                <div className="text-2xl mb-1">💄</div>
                <div className="text-xs font-semibold">Beauty</div>
                <div className="text-xs">80% OFF</div>
              </div>
            </div>
          </div>

          {/* Right Content - Product Showcase */}
          <div className="relative">
            <div className="relative aspect-[4/3] rounded-2xl overflow-hidden shadow-2xl">
              {/* Product Grid */}
              <div className="w-full h-full bg-gradient-to-br from-yellow-400/20 to-red-500/20 backdrop-blur-sm grid grid-cols-2 gap-2 p-4">
                {/* Product Cards */}
                <div className="bg-white rounded-lg p-3 text-center transform hover:scale-105 transition-transform cursor-pointer">
                  <div className="text-3xl mb-2">�</div>
                  <div className="text-xs font-bold text-gray-900">iPhone 15</div>
                  <div className="text-xs text-red-600 font-bold">-50%</div>
                  <div className="text-xs text-gray-600 line-through">$999</div>
                  <div className="text-sm font-bold text-green-600">$499</div>
                </div>
                
                <div className="bg-white rounded-lg p-3 text-center transform hover:scale-105 transition-transform cursor-pointer">
                  <div className="text-3xl mb-2">👟</div>
                  <div className="text-xs font-bold text-gray-900">Nike Shoes</div>
                  <div className="text-xs text-red-600 font-bold">-60%</div>
                  <div className="text-xs text-gray-600 line-through">$199</div>
                  <div className="text-sm font-bold text-green-600">$79</div>
                </div>
                
                <div className="bg-white rounded-lg p-3 text-center transform hover:scale-105 transition-transform cursor-pointer">
                  <div className="text-3xl mb-2">💻</div>
                  <div className="text-xs font-bold text-gray-900">Laptop</div>
                  <div className="text-xs text-red-600 font-bold">-40%</div>
                  <div className="text-xs text-gray-600 line-through">$1299</div>
                  <div className="text-sm font-bold text-green-600">$779</div>
                </div>
                
                <div className="bg-white rounded-lg p-3 text-center transform hover:scale-105 transition-transform cursor-pointer">
                  <div className="text-3xl mb-2">⌚</div>
                  <div className="text-xs font-bold text-gray-900">Smart Watch</div>
                  <div className="text-xs text-red-600 font-bold">-70%</div>
                  <div className="text-xs text-gray-600 line-through">$399</div>
                  <div className="text-sm font-bold text-green-600">$119</div>
                </div>
              </div>
              
              {/* Hot Badge */}
              <div className="absolute top-2 right-2 bg-red-600 text-white rounded-full px-3 py-1 text-xs font-bold animate-pulse">
                🔥 HOT
              </div>
            </div>
            
            {/* Floating Stats */}
            <div className="absolute -top-4 -right-4 bg-white rounded-xl shadow-xl p-3 animate-bounce">
              <div className="flex items-center gap-2">
                <div className="text-2xl">🔥</div>
                <div>
                  <div className="font-bold text-gray-900 text-sm">10K+ Sold</div>
                  <div className="text-xs text-gray-600">Last Hour</div>
                </div>
              </div>
            </div>
            
            <div className="absolute -bottom-4 -left-4 bg-white rounded-xl shadow-xl p-3">
              <div className="flex items-center gap-2">
                <div className="text-2xl">⭐</div>
                <div>
                  <div className="font-bold text-gray-900 text-sm">4.9/5</div>
                  <div className="text-xs text-gray-600">50K+ Reviews</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
