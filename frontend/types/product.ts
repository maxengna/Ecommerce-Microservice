export interface Product {
  id: number;
  name: string;
  description: string | null;
  sku: string;
  price: number;
  stock_quantity: number;
  stock: number; // Alias for stock_quantity
  original_price?: number;
  rating?: number;
  reviews_count?: number;
  is_new?: boolean;
  is_featured?: boolean;
  is_active: boolean;
  weight: number | null;
  dimensions: string | null;
  created_at: string;
}

export interface ProductCreate {
  name: string;
  description?: string;
  sku: string;
  price: number;
  stock_quantity: number;
  is_active?: boolean;
  weight?: number;
  dimensions?: string;
  category_ids?: number[];
}

export interface ProductUpdate {
  name?: string;
  description?: string;
  price?: number;
  stock_quantity?: number;
  is_active?: boolean;
  weight?: number;
  dimensions?: string;
}

export interface Category {
  id: number;
  name: string;
  description: string | null;
  parent_id: number | null;
  is_active: boolean;
  created_at: string;
}

export interface ProductSearchParams {
  skip?: number;
  limit?: number;
  category_id?: number;
  search?: string;
  min_price?: number;
  max_price?: number;
  in_stock?: boolean;
}
