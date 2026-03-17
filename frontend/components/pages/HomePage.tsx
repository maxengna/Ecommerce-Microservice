'use client'

import { useState, useEffect } from 'react'
import { Header } from '@/components/layout/Header'
import { ProductGrid } from '@/components/ui/ProductGrid'
import { HeroSection } from '@/components/ui/HeroSection'
import { CategorySection } from '@/components/ui/CategorySection'
import { Footer } from '@/components/layout/Footer'
import { Product } from '@/types/product'
import { productService } from '@/lib/api'

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
        <HeroSection />
        <CategorySection />
        <section className="py-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                Featured Products
              </h2>
              <p className="text-gray-600 max-w-2xl mx-auto">
                Discover our handpicked selection of premium products
              </p>
            </div>
            <ProductGrid products={products} loading={loading} />
          </div>
        </section>
      </main>
      <Footer />
    </div>
  )
}
