'use client'

import Link from 'next/link'
import { Category } from '@/types/product'

const mockCategories: Category[] = [
  { id: 1, name: 'Electronics', description: 'Latest gadgets and tech', parent_id: null, is_active: true, created_at: '2024-01-01' },
  { id: 2, name: 'Clothing', description: 'Fashion and apparel', parent_id: null, is_active: true, created_at: '2024-01-01' },
  { id: 3, name: 'Home & Garden', description: 'Home improvement and decor', parent_id: null, is_active: true, created_at: '2024-01-01' },
  { id: 4, name: 'Sports', description: 'Sports equipment and gear', parent_id: null, is_active: true, created_at: '2024-01-01' },
  { id: 5, name: 'Books', description: 'Books and educational materials', parent_id: null, is_active: true, created_at: '2024-01-01' },
  { id: 6, name: 'Toys', description: 'Toys and games for all ages', parent_id: null, is_active: true, created_at: '2024-01-01' },
]

const categoryIcons = {
  'Electronics': '📱',
  'Clothing': '👕',
  'Home & Garden': '🏠',
  'Sports': '⚽',
  'Books': '📚',
  'Toys': '🎮',
}

export function CategorySection() {
  return (
    <section className="py-16 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Shop by Category
          </h2>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Browse our wide range of categories to find exactly what you're looking for
          </p>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6">
          {mockCategories.map((category) => (
            <Link
              key={category.id}
              href={`/categories/${category.id}`}
              className="group"
            >
              <div className="bg-gray-50 rounded-lg p-6 text-center hover:bg-primary-50 hover:shadow-lg transition-all duration-200 border border-gray-200 hover:border-primary-200">
                <div className="text-4xl mb-3 group-hover:scale-110 transition-transform duration-200">
                  {categoryIcons[category.name] || '📦'}
                </div>
                <h3 className="font-semibold text-gray-900 group-hover:text-primary-600 transition-colors">
                  {category.name}
                </h3>
                <p className="text-sm text-gray-500 mt-1 line-clamp-2">
                  {category.description}
                </p>
              </div>
            </Link>
          ))}
        </div>

        <div className="text-center mt-12">
          <Link
            href="/categories"
            className="inline-flex items-center px-6 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors duration-200"
          >
            View All Categories
            <svg
              className="ml-2 h-5 w-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 5l7 7-7 7"
              />
            </svg>
          </Link>
        </div>
      </div>
    </section>
  )
}
