
export interface User {
    id: number;
    email: string;
    hashed_password: string;
    role: "admin" | "user";
    is_active: boolean;
}
export interface Product { 
  id: number; 
  name: string; 
  sku: string; 
  selling_price: number; 
  quantity_left: number; 
}

export interface BillItem { 
  id: number; 
  product_id: number; 
  product_name?: string; 
  quantity: number; 
  price?: number; 
  selling_price?: number;
  product?: { selling_price: number; name: string };
}

export interface Bill { 
  id: number; 
  bill_number: string; 
  customer_name: string; 
  customer_phone: string; 
  subtotal: number; 
  items: BillItem[]; 
}