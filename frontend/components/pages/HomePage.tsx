'use client'

import { useState, useEffect } from 'react'
import { Header } from '@/components/layout/Header'
import { HeroSection } from '@/components/ui/HeroSection'
import { CategorySection } from '@/components/ui/CategorySection'
import { ProductShowcase } from '@/components/ui/ProductShowcase'
import { Footer } from '@/components/layout/Footer'
import { Product } from '@/types/product'
import { productService } from '@/lib/api'
import { ProductGrid } from '@/components/ui/ProductGrid'

// Mock data
const featuredProducts: Product[] = [
  {
    id: 1,
    name: "Premium Wireless Headphones",
    description: "High-quality wireless headphones with noise cancellation",
    sku: "WH-001",
    price: 299.99,
    stock_quantity: 15,
    stock: 15,
    original_price: 399.99,
    rating: 4.5,
    reviews_count: 234,
    is_new: true,
    is_featured: true,
    is_active: true,
    weight: 0.5,
    dimensions: "20x15x10 cm",
    created_at: "2024-01-15"
  },
  {
    id: 2,
    name: "Smart Watch Pro",
    description: "Advanced fitness and health tracking smartwatch",
    sku: "SW-002",
    price: 199.99,
    stock_quantity: 8,
    stock: 8,
    original_price: 249.99,
    rating: 4.8,
    reviews_count: 189,
    is_new: false,
    is_featured: true,
    is_active: true,
    weight: 0.1,
    dimensions: "4x4x1 cm",
    created_at: "2024-01-10"
  },
  {
    id: 3,
    name: "Laptop Backpack",
    description: "Durable and stylish backpack for laptops up to 15.6 inches",
    sku: "BP-003",
    price: 79.99,
    stock_quantity: 25,
    stock: 25,
    rating: 4.2,
    reviews_count: 156,
    is_new: false,
    is_featured: false,
    is_active: true,
    weight: 1.2,
    dimensions: "45x30x15 cm",
    created_at: "2024-01-05"
  }
]
export function HomePage() {
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const data = await productService.getProducts({ limit: 8 })
        setProducts(data)
      } catch (error) {
        console.error('Failed to fetch products:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchProducts()
  }, [])

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main>
        {/* Hero Banner */}
        <HeroSection />
        
        {/* Flash Sale Banner */}
        <section className="bg-gradient-to-r from-red-500 to-orange-500 text-white py-3">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-center gap-4">
              <div className="bg-white/20 backdrop-blur-sm rounded-lg px-3 py-1">
                <span className="text-sm font-bold">⚡ FLASH SALE</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-semibold">Ends in:</span>
                <div className="flex gap-1">
                  <div className="bg-white text-red-500 rounded px-2 py-1 font-bold text-sm">02</div>
                  <span className="font-bold">:</span>
                  <div className="bg-white text-red-500 rounded px-2 py-1 font-bold text-sm">45</div>
                  <span className="font-bold">:</span>
                  <div className="bg-white text-red-500 rounded px-2 py-1 font-bold text-sm">30</div>
                </div>
              </div>
              <div className="text-sm font-semibold">Up to 80% OFF</div>
            </div>
          </div>
        </section>

        {/* Category Section */}
        <CategorySection />
        
        {/* Featured Products */}
        <section className="py-12 bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between mb-8">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                  🔥 Hot Deals
                </h2>
                <p className="text-gray-600">Limited time offers on popular items</p>
              </div>
              <button className="text-orange-500 hover:text-orange-600 font-semibold flex items-center gap-1">
                View All
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </div>
            <ProductGrid products={products} loading={loading} />
          </div>
        </section>

        {/* Special Offers Banner */}
        <section className="py-12 bg-gradient-to-r from-purple-600 to-blue-600 text-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 text-center">
                <div className="text-4xl mb-3">🚚</div>
                <h3 className="font-bold text-lg mb-2">Free Shipping</h3>
                <p className="text-white/80 text-sm">On orders over 299฿</p>
              </div>
              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 text-center">
                <div className="text-4xl mb-3">💰</div>
                <h3 className="font-bold text-lg mb-2">Cashback</h3>
                <p className="text-white/80 text-sm">Up to 20% cashback</p>
              </div>
              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 text-center">
                <div className="text-4xl mb-3">🎁</div>
                <h3 className="font-bold text-lg mb-2">Daily Deals</h3>
                <p className="text-white/80 text-sm">New deals every day</p>
              </div>
            </div>
          </div>
        </section>

        {/* Recommended Products */}
        <section className="py-12 bg-gray-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between mb-8">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                  Recommended For You
                </h2>
                <p className="text-gray-600">Based on your browsing history</p>
              </div>
              <button className="text-blue-500 hover:text-blue-600 font-semibold flex items-center gap-1">
                See More
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </div>
            <ProductGrid products={featuredProducts} loading={false} />
          </div>
        </section>

        {/* App Download Banner */}
        <section className="py-16 bg-gradient-to-r from-green-500 to-teal-500 text-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
              <div>
                <h2 className="text-3xl font-bold mb-4">Shop Anytime, Anywhere</h2>
                <p className="text-white/90 mb-6">Download our app for exclusive deals and faster checkout</p>
                <div className="flex flex-col sm:flex-row gap-4">
                  <button className="bg-black text-white px-6 py-3 rounded-lg flex items-center gap-3 hover:bg-gray-800 transition-colors">
                    <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.09l.01-.01zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z"/>
                    </svg>
                    <div className="text-left">
                      <div className="text-xs">Download on the</div>
                      <div className="text-sm font-semibold">App Store</div>
                    </div>
                  </button>
                  <button className="bg-black text-white px-6 py-3 rounded-lg flex items-center gap-3 hover:bg-gray-800 transition-colors">
                    <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M3,20.5V3.5C3,2.91 3.34,2.39 3.84,2.15L13.69,12L3.84,21.85C3.34,21.61 3,21.09 3,20.5M16.81,15.12L6.05,21.34L14.54,12.85L16.81,15.12M20.16,10.81C20.5,11.08 20.75,11.5 20.75,12C20.75,12.5 20.53,12.9 20.16,13.19L17.89,14.5L15.39,12L17.89,9.5L20.16,10.81M6.05,2.66L16.81,8.88L14.54,11.15L6.05,2.66Z"/>
                    </svg>
                    <div className="text-left">
                      <div className="text-xs">Get it on</div>
                      <div className="text-sm font-semibold">Google Play</div>
                    </div>
                  </button>
                </div>
              </div>
              <div className="flex justify-center">
                <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8">
                  <div className="text-6xl mb-4 text-center">📱</div>
                  <div className="text-center">
                    <div className="text-xl font-bold mb-2">Mobile App</div>
                    <div className="text-white/80">Better experience on mobile</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  )
}
