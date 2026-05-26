export interface User {
    id: number;
    email: string;
    hashed_password: string;
    role: "admin" | "user";
    is_active: boolean;
}

export interface Product {
    id: number;
    sku: string;
    name: string;
    cost_price: number;
    selling_price: number;
    quantity_left: number;
}