'use client'

import { Product } from '@/types/product'
import { useCartStore } from '@/store/cartStore'
import { ShoppingCart, Star } from 'lucide-react'
import Link from 'next/link'

interface ProductGridProps {
  products: Product[]
  loading?: boolean
}

export function ProductGrid({ products, loading }: ProductGridProps) {
  const addItem = useCartStore((state) => state.addItem)

  const handleAddToCart = (product: Product) => {
    addItem(product, 1)
  }

  if (loading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {[...Array(8)].map((_, index) => (
          <div key={index} className="animate-pulse">
            <div className="bg-gray-200 rounded-lg h-48 mb-4"></div>
            <div className="h-4 bg-gray-200 rounded mb-2"></div>
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
            <div className="h-6 bg-gray-200 rounded w-1/2"></div>
          </div>
        ))}
      </div>
    )
  }

  if (products.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-500 text-lg mb-4">No products found</div>
        <p className="text-gray-400">
          Try adjusting your search or browse our categories
        </p>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
      {products.map((product) => (
        <div
          key={product.id}
          className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow duration-200"
        >
          {/* Product Image */}
          <div className="relative">
            <div className="aspect-square bg-gray-100 flex items-center justify-center">
              <div className="text-gray-400 text-4xl">
                📦
              </div>
            </div>
            
            {/* Stock Badge */}
            {product.stock_quantity <= 5 && product.stock_quantity > 0 && (
              <div className="absolute top-2 left-2 bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded">
                Only {product.stock_quantity} left
              </div>
            )}
            
            {product.stock_quantity === 0 && (
              <div className="absolute top-2 left-2 bg-red-100 text-red-800 text-xs px-2 py-1 rounded">
                Out of Stock
              </div>
            )}
          </div>

          {/* Product Info */}
          <div className="p-4">
            <div className="mb-2">
              <h3 className="text-lg font-medium text-gray-900 line-clamp-2">
                {product.name}
              </h3>
              <p className="text-sm text-gray-500 line-clamp-2 mt-1">
                {product.description}
              </p>
            </div>

            {/* Rating */}
            <div className="flex items-center mb-3">
              <div className="flex items-center">
                {[...Array(5)].map((_, i) => (
                  <Star
                    key={i}
                    className={`h-4 w-4 ${
                      i < 4 ? 'text-yellow-400 fill-current' : 'text-gray-300'
                    }`}
                  />
                ))}
              </div>
              <span className="text-sm text-gray-500 ml-2">(4.5)</span>
            </div>

            {/* Price and Actions */}
            <div className="flex items-center justify-between">
              <div>
                <span className="text-2xl font-bold text-gray-900">
                  ${product.price.toFixed(2)}
                </span>
              </div>
              
              <div className="flex space-x-2">
                <Link
                  href={`/products/${product.id}`}
                  className="p-2 text-gray-600 hover:text-primary-600 transition-colors"
                >
                  <svg
                    className="h-5 w-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                    />
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                    />
                  </svg>
                </Link>
                
                <button
                  onClick={() => handleAddToCart(product)}
                  disabled={product.stock_quantity === 0}
                  className={`p-2 rounded-lg transition-colors ${
                    product.stock_quantity === 0
                      ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                      : 'bg-primary-600 text-white hover:bg-primary-700'
                  }`}
                >
                  <ShoppingCart className="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
