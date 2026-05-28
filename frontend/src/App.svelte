<script lang="ts">
  import { onMount } from "svelte";
  import { 
    pingServer, getProduct, createProduct, adjustStock, deleteProduct, 
    createDraftBill, addItemToBill, updateBillDetails, finalizeBill, 
    removeItemFromBill, // Controls deleting items from active draft
    getAllSales, getDashboardAnalytics, initiateProductReturn, getAllReturns,
    deleteSaleBill // Controls deleting finalized bills from the ledger
  } from "./lib/api";
  import type { Product, Bill } from "./lib/types"; 

  import Login from "./lib/Login.svelte";
  import Dashboard from "./lib/Dashboard.svelte";
  import Inventory from "./lib/Inventory.svelte";
  import Bills from "./lib/Bills.svelte";
  import Sales from "./lib/Sales.svelte";
  import Returns from "./lib/Returns.svelte";

  let websiteName = "Stash GO";
  
  let activePage = $state("dashboard"); 
  let backendStatus = $state("Connecting...");
  let products = $state<Product[]>([]);
  let salesHistory = $state<any[]>([]);
  let returnsHistory = $state<any[]>([]); 
  let salesAnalytics = $state<any>(null); 
  let isAuthenticated = $state(false);

  let newProduct = $state({
    sku: "",
    name: "",
    cost_price: 0,
    selling_price: 0,
    quantity_left: 0
  });

  let activeBill: Bill | null = $state(null);
  let customerName = $state(""), customerPhone = $state(""), customerEmail = $state("");
  let saleSku = $state(""); // Bound securely as a string
  let saleQty = $state(1), billingDiscount = $state(0), billingTax = $state(0), paymentMethod = $state("Cash");

  onMount(async () => {
    const data = await pingServer();
    backendStatus = data.status;
    if (localStorage.getItem("token")) {
        isAuthenticated = true;
        await refreshAllData();
    }
  });

  async function refreshAllData() {
    products = await getProduct();
    salesHistory = await getAllSales();
    salesAnalytics = await getDashboardAnalytics(); 
    returnsHistory = await getAllReturns(); 
  }

  // --- INVENTORY MANAGEMENT ---
  async function handleAddProduct() {
    const success = await createProduct({ 
      sku: newProduct.sku, 
      name: newProduct.name, 
      cost_price: Number(newProduct.cost_price),
      selling_price: Number(newProduct.selling_price), 
      quantity_left: Number(newProduct.quantity_left) 
    });
    if (success) { 
      await refreshAllData(); 
      newProduct.sku = ""; newProduct.name = ""; newProduct.cost_price = 0; newProduct.selling_price = 0; newProduct.quantity_left = 0;
    } else {
      alert("Validation failed. Check constraints.");
    }
  }

  async function handleStockChange(sku: string, action: "increase-stock" | "decrease-stock") {
    if (await adjustStock(sku, action)) await refreshAllData();
  }

  async function handleRemove(id: number) {
    if (confirm("Permanently remove product from inventory?") && await deleteProduct(String(id))) {
      await refreshAllData();
    }
  }

  // --- RETURNS MANAGEMENT ---
  async function handleProcessReturn(returnData: any) {
    if (await initiateProductReturn(returnData)) {
      alert(`Return recorded successfully for Sale #${returnData.sale_id}!`);
      await refreshAllData();
    }
  }

  // --- BILLING COUNTER (DRAFTS) ---
  async function handleCreateBill() {
    const bill = await createDraftBill({ customer_name: customerName, customer_phone: customerPhone, customer_email: customerEmail });
    if (bill) activeBill = bill;
  }

  async function handleAddItemToBill() {
    if (!activeBill) return;
    
    const updatedBill = await addItemToBill(activeBill.id, { 
      product_id: String(Number(saleSku)), 
      quantity: Number(saleQty) 
    });
    
    if (updatedBill) { 
      activeBill = updatedBill; 
      saleSku = ""; 
      saleQty = 1; 
    } else {
      alert("Failed to append item.");
    }
  }

  async function handleRemoveItem(itemId: number) {
    if (!activeBill) return;
    const updatedBill = await removeItemFromBill(activeBill.id, itemId);
    if (updatedBill) {
      activeBill = updatedBill;
    } else {
      alert("Failed to remove item.");
    }
  }

  async function handleCheckoutAndFinalize() {
    if (!activeBill) return;
    
    // Convert the UI % inputs into flat Rupee amounts for the backend
    const flatDiscountAmount = activeBill.subtotal * (billingDiscount / 100);
    const flatTaxAmount = activeBill.subtotal * (billingTax / 100);

    const detailsUpdated = await updateBillDetails(activeBill.id, { 
      discount: flatDiscountAmount, 
      tax: flatTaxAmount, 
      payment_method: paymentMethod 
    });
    
    if (!detailsUpdated) return;
    
    const finalReceipt = await finalizeBill(activeBill.id);
    
    if (finalReceipt) {
      alert(`Invoice order ${finalReceipt.bill_number} finalized successfully!`);
      activeBill = null; 
      customerName = ""; 
      customerPhone = ""; 
      customerEmail = ""; 
      billingDiscount = 0; 
      billingTax = 0;
      await refreshAllData(); 
    }
  }

  // --- SALES LEDGER ACTIONS ---
  async function handleDeleteSale(billId: number) {
    if (confirm(`Are you sure you want to permanently delete Invoice #${billId}?`)) {
      const success = await deleteSaleBill(billId);
      if (success) {
        await refreshAllData();
      } else {
        alert("Failed to delete the invoice.");
      }
    }
  }

  // --- AUTH ---
  function handleLogout() { 
    localStorage.removeItem("token"); 
    isAuthenticated = false; 
    location.reload(); 
  }
</script>

<div class="StashGo-Layout">
  {#if !isAuthenticated}
    <Login onLoginSuccess={() => { isAuthenticated = true; refreshAllData(); }} />
  {:else}
    <header>
      <div class="header-brand">
        <h1>{websiteName}</h1>
        <span class="status-indicator {backendStatus === 'ok' ? 'online' : 'offline'}">
          Backend: {backendStatus}
        </span>
      </div>
      <nav>
        <button class:active={activePage === "dashboard"} onclick={() => activePage = "dashboard"}>Dashboard</button>
        <button class:active={activePage === "inventory"} onclick={() => activePage = "inventory"}>Inventory</button>
        <button class:active={activePage === "counter"} onclick={() => activePage = "counter"}>Billing Counter</button>
        <button class:active={activePage === "sales"} onclick={() => activePage = "sales"}>Sales Ledger</button>
        <button class:active={activePage === "returns"} onclick={() => activePage = "returns"}>Returns</button>
        <button class="btn-logout" onclick={handleLogout}>Logout</button>
      </nav>
    </header>

    <main>
      {#if activePage === "dashboard"}
        <Dashboard {backendStatus} analyticsData={salesAnalytics} />
      
      {:else if activePage === "inventory"}
        <Inventory {products} {handleAddProduct} {handleStockChange} {handleRemove} bind:newProduct />
      
      {:else if activePage === "counter"}
        <Bills 
          {products} {activeBill} {handleCreateBill} {handleAddItemToBill} {handleCheckoutAndFinalize} {handleRemoveItem}
          bind:customerName bind:customerPhone bind:customerEmail bind:saleSku bind:saleQty bind:billingDiscount bind:billingTax bind:paymentMethod
        />
      
      {:else if activePage === "sales"}
        <Sales {salesHistory} {handleDeleteSale} />
      
      {:else if activePage === "returns"}
        <Returns {returnsHistory} {handleProcessReturn} />
      {/if}
    </main>
  {/if}
</div>

<style>
  .StashGo-Layout { background-color: #121214; min-height: 100vh; min-width: max-content; color: #e1e1e6; font-family: system-ui, -apple-system, sans-serif; box-sizing: border-box; }
  header, .header-brand, nav { display: flex; align-items: center; }
  header { background: #1e1e24; padding: 15px 40px; justify-content: space-between; border-bottom: 1px solid #29292e; }
  .header-brand { gap: 15px; }
  h1 { margin: 0; font-size: 24px; color: #00bcd4; letter-spacing: 0.5px; }
  main { max-width: 1200px; margin: 40px auto; padding: 0 20px; }
  nav { gap: 10px; }
  nav button { background: transparent; border: none; color: #a8a8b3; padding: 8px 16px; cursor: pointer; font-size: 14px; font-weight: 500; border-radius: 4px; transition: all 0.2s ease; }
  nav button:hover, nav button.active { color: #121214; background: #00bcd4; }
  nav .btn-logout { border: 1px solid #ff5252; color: #ff5252; margin-left: 15px; }
  nav .btn-logout:hover { background: #ff5252; color: #ffffff; }
  .status-indicator { font-size: 11px; padding: 3px 8px; border-radius: 12px; text-transform: uppercase; font-weight: bold; border: 1px solid transparent; }
  .status-indicator.online { background: rgba(76, 175, 80, 0.15); color: #4caf50; border-color: rgba(76, 175, 80, 0.3); }
  .status-indicator.offline { background: rgba(255, 82, 82, 0.15); color: #ff5252; border-color: rgba(255, 82, 82, 0.3); }
</style>