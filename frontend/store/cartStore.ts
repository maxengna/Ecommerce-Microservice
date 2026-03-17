import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { Product } from '@/types/product'

interface CartItem {
  id: string
  product: Product
  quantity: number
  added_at: string
}

interface CartStore {
  items: CartItem[]
  itemsCount: number
  totalAmount: number
  
  // Actions
  addItem: (product: Product, quantity?: number) => void
  removeItem: (itemId: string) => void
  updateQuantity: (itemId: string, quantity: number) => void
  clearCart: () => void
  
  // Getters
  getItem: (productId: number) => CartItem | undefined
  getSubtotal: () => number
}

export const useCartStore = create<CartStore>()(
  persist(
    (set, get) => ({
      items: [],
      itemsCount: 0,
      totalAmount: 0,

      addItem: (product: Product, quantity = 1) => {
        const currentItems = get().items
        const existingItem = currentItems.find(item => item.product.id === product.id)

        if (existingItem) {
          // Update quantity if item already exists
          const updatedItems = currentItems.map(item =>
            item.product.id === product.id
              ? { ...item, quantity: item.quantity + quantity }
              : item
          )
          
          const { itemsCount, totalAmount } = calculateTotals(updatedItems)
          
          set({
            items: updatedItems,
            itemsCount,
            totalAmount,
          })
        } else {
          // Add new item
          const newItem: CartItem = {
            id: `${product.id}-${Date.now()}`,
            product,
            quantity,
            added_at: new Date().toISOString(),
          }

          const updatedItems = [...currentItems, newItem]
          const { itemsCount, totalAmount } = calculateTotals(updatedItems)

          set({
            items: updatedItems,
            itemsCount,
            totalAmount,
          })
        }
      },

      removeItem: (itemId: string) => {
        const updatedItems = get().items.filter(item => item.id !== itemId)
        const { itemsCount, totalAmount } = calculateTotals(updatedItems)

        set({
          items: updatedItems,
          itemsCount,
          totalAmount,
        })
      },

      updateQuantity: (itemId: string, quantity: number) => {
        if (quantity <= 0) {
          get().removeItem(itemId)
          return
        }

        const updatedItems = get().items.map(item =>
          item.id === itemId ? { ...item, quantity } : item
        )

        const { itemsCount, totalAmount } = calculateTotals(updatedItems)

        set({
          items: updatedItems,
          itemsCount,
          totalAmount,
        })
      },

      clearCart: () => {
        set({
          items: [],
          itemsCount: 0,
          totalAmount: 0,
        })
      },

      getItem: (productId: number) => {
        return get().items.find(item => item.product.id === productId)
      },

      getSubtotal: () => {
        return get().items.reduce(
          (total, item) => total + item.product.price * item.quantity,
          0
        )
      },
    }),
    {
      name: 'cart-storage',
      partialize: (state) => ({
        items: state.items,
      }),
      onRehydrateStorage: () => (state) => {
        if (state) {
          const { itemsCount, totalAmount } = calculateTotals(state.items)
          state.itemsCount = itemsCount
          state.totalAmount = totalAmount
        }
      },
    }
  )
)

// Helper function to calculate totals
function calculateTotals(items: CartItem[]) {
  const itemsCount = items.reduce((total, item) => total + item.quantity, 0)
  const totalAmount = items.reduce(
    (total, item) => total + item.product.price * item.quantity,
    0
  )

  return { itemsCount, totalAmount }
}
