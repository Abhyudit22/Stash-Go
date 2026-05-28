export const Base_URL = "https://abhyudit-stash-go.hf.space";
import type { Product } from "./types";

export async function pingServer() {
    try {
        const response = await fetch(`${Base_URL}/`);
        if (!response.ok) {
            throw new Error("The server rejects the request");
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error("Could not reach the StashGO:", error);
        return { status: "offline" };
    }
}

export async function getProduct() {
    try {
        const token = localStorage.getItem("token"); 

        const response = await fetch(`${Base_URL}/products/getall`, {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            }
        }); 
        
        if (!response.ok) {
            throw new Error("The server rejects the request");
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error("Could not reach the StashGO:", error);
        return []; 
 }
}
export async function createProduct(productData: { sku: string; name: string; cost_price: number; selling_price: number; quantity_left: number }) {
    try {
        const token = localStorage.getItem("token");
        const response = await fetch(`${Base_URL}/products/create`, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify(productData)
        });
        return response.ok;
    } catch (error) {
        console.error("Error creating product:", error);
        return false;
    }
}
export async function adjustStock(productId: string, action: "increase-stock" | "decrease-stock") {
    try {
        const token = localStorage.getItem("token");
        const response = await fetch(`${Base_URL}/products/${productId}/${action}`, {
            method: "PATCH",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });
        return response.ok;
    } catch (error) {
        console.error(`Error executing ${action}:`, error);
        return false;
    }
}

export async function deleteProduct(productId: string) {
    try {
        const token = localStorage.getItem("token");
        const response = await fetch(`${Base_URL}/products/${productId}`, {
            method: "DELETE",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });
        return response.ok;
    } catch (error) {
        console.error("Error deleting product:", error);
        return false;
    }
}

export async function getAllSales() {
    try {
        const token = localStorage.getItem("token");
        const response = await fetch(`${Base_URL}/sales/`, { 
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            }
        });
        if (!response.ok) return [];
        return await response.json();
    } catch (error) {
        console.error("Error fetching historical sales ledger:", error);
        return [];
    }
}

export async function createDraftBill(customerData: { customer_name: string; customer_phone: string; customer_email: string }) {
    try {
        const token = localStorage.getItem("token");
        const response = await fetch(`${Base_URL}/bills/`, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify(customerData)
        });
        if (!response.ok) return null;
        return await response.json(); 
    } catch (error) {
        console.error("Error creating draft bill:", error);
        return null;
    }
}

export async function addItemToBill(billId: number, itemData: { product_id: string; quantity: number }) {
    try {
        const token = localStorage.getItem("token");
        const response = await fetch(`${Base_URL}/bills/${billId}/items`, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify(itemData)
        });
        if (!response.ok) {
            const err = await response.json();
            alert(`Error: ${err.detail}`);
            return null;
        }
        return await response.json(); 
    } catch (error) {
        console.error("Error appending item:", error);
        return null;
    }
}

export async function updateBillDetails(billId: number, updateData: { discount: number; tax: number; payment_method: string }) {
    try {
        const token = localStorage.getItem("token");
        const response = await fetch(`${Base_URL}/bills/${billId}`, {
            method: "PUT",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify(updateData)
        });
        if (!response.ok) return null;
        return await response.json();
    } catch (error) {
        console.error("Error patching invoice configurations:", error);
        return null;
    }
}

export async function finalizeBill(billId: number) {
    try {
        const token = localStorage.getItem("token");
        const response = await fetch(`${Base_URL}/bills/${billId}/finalize`, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });
        if (!response.ok) {
            const err = await response.json();
            alert(`Finalize Error: ${err.detail}`);
            return null;
        }
        return await response.json(); 
    } catch (error) {
        console.error("Error finalizing transaction:", error);
        return null;
    }
}
export async function getDashboardAnalytics() {
    try {
        const token = localStorage.getItem("token");
        const response = await fetch(`${Base_URL}/analytics/dashboard`, {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            }
        });
        if (!response.ok) return null;
        return await response.json(); // Returns the exact DashboardResponse schema object
    } catch (error) {
        console.error("Error fetching dashboard analytics:", error);
        return null;
    }
}
// 1. Process a new product return request container
export async function initiateProductReturn(returnData: { sale_id: number; product_id: string; quantity: number; reason: string }) {
    try {
        const token = localStorage.getItem("token");
        const response = await fetch(`${Base_URL}/returns/create/`, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify(returnData)
        });
        if (!response.ok) {
            const err = await response.json();
            alert(`Return Refused: ${err.detail}`);
            return null;
        }
        return await response.json(); 
    } catch (error) {
        console.error("Error processing return execution:", error);
        return null;
    }
}
export async function getAllReturns() {
    try {
        const token = localStorage.getItem("token");
        const response = await fetch(`${Base_URL}/returns/all_returns/`, {
            method: "GET",
            headers: { "Authorization": `Bearer ${token}` }
        });
        if (!response.ok) return [];
        return await response.json();
    } catch (error) {
        console.error("Error gathering historical returns log:", error);
        return [];
    }
}
export async function removeItemFromBill(billId: number, itemId: number) {
  try {
    const token = localStorage.getItem("token");
    const res = await fetch(`http://localhost:8000/bills/${billId}/items/${itemId}`, {
      method: "DELETE",
      headers: { 
        "Authorization": `Bearer ${token}` 
      }
    });
    
    if (!res.ok) {
        console.error("Failed to remove item. Status:", res.status);
        return null;
    }
    
    return await res.json();
  } catch (error) {
    console.error("Error calling remove item API:", error);
    return null;
  }
}
export async function deleteSaleBill(billId: number) {
  try {
    const token = localStorage.getItem("token");
    const res = await fetch(`http://localhost:8000/bills/${billId}`, {
      method: "DELETE",
      headers: { "Authorization": `Bearer ${token}` }
    });
    if (!res.ok) throw new Error("Failed to delete bill");
    return true;
  } catch (error) {
    console.error("Error deleting bill:", error);
    return false;
  }
}