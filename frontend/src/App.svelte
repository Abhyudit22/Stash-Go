<script lang="ts">
  import { onMount } from "svelte";
  import { 
    pingServer, getProduct, createProduct, adjustStock, deleteProduct, 
    createDraftBill, getBillById, addItemToBill, updateBillDetails, finalizeBill, 
    removeItemFromBill,
    getAllSales, getDashboardAnalytics, initiateProductReturn, getAllReturns,
    deleteSaleBill
  } from "./lib/api";
  import type { Product, Bill } from "./lib/types"; 

  import Landing from "./lib/Landing.svelte"; 
  import Login from "./lib/Login.svelte";
  import Dashboard from "./lib/Dashboard.svelte";
  import Inventory from "./lib/Inventory.svelte";
  import Bills from "./lib/Bills.svelte";
  import Sales from "./lib/Sales.svelte";
  import Returns from "./lib/Returns.svelte";
  import CommandPalette from "./lib/CommandPalette.svelte";
  import Toast from "./lib/Toast.svelte";
  import { toast } from "./lib/toastStore";

  let websiteName = "Stash GO";
  
  let showLanding = $state(true); 
  let activePage = $state("dashboard"); 
  let backendStatus = $state("Connecting...");
  let products = $state<Product[]>([]);
  let salesHistory = $state<any[]>([]);
  let returnsHistory = $state<any[]>([]); 
  let salesAnalytics = $state<any>(null); 
  let isAuthenticated = $state(false);
  let isCmdOpen = $state(false);

  let newProduct = $state({
    sku: "",
    name: "",
    cost_price: 0,
    selling_price: 0,
    quantity_left: 0
  });

  let activeBill: Bill | null = $state(null);
  let customerName = $state(""), customerPhone = $state(""), customerEmail = $state("");
  let saleSku = $state(""); 
  let saleQty = $state(1), billingDiscount = $state(0), billingTax = $state(0), paymentMethod = $state("Cash");

  // --- NATIVE ROUTING SYSTEM ---
  function navigate(page: string) {
    if (page === "landing" || page === "home") {
      showLanding = true;
      activePage = "landing";
      window.history.pushState({ page: "landing" }, "", "/");
      return;
    }

    showLanding = false;
    activePage = page;
    window.history.pushState({ page }, "", `/${page}`);
  }

  function handleLaunch() {
    showLanding = false;
    if (!isAuthenticated) {
      window.history.pushState({ page: 'login' }, "", "/login");
      activePage = "login";
    } else {
      navigate("dashboard");
    }
  }

  onMount(async () => {
    document.documentElement.setAttribute('data-theme', 'dark');

    const data = await pingServer();
    backendStatus = data.status;
    
    const currentPath = window.location.pathname;

    if (localStorage.getItem("token")) {
        isAuthenticated = true;
        if (currentPath === "/" || currentPath === "/landing" || currentPath === "") {
            showLanding = true;
            activePage = "landing";
        } else {
            showLanding = false;
            activePage = currentPath.replace("/", "") || "dashboard";
        }
        await refreshAllData();
    } else {
        showLanding = true;
        window.history.pushState({ page: "landing" }, "", "/");
    }

    window.addEventListener('popstate', (event) => {
      if (event.state && event.state.page) {
        if (event.state.page === 'login') {
            showLanding = false;
            activePage = "login";
        } else if (event.state.page === 'landing') {
            showLanding = true;
            activePage = "landing";
        } else {
            showLanding = false;
            activePage = event.state.page;
        }
      } else {
        showLanding = true;
        activePage = "landing";
      }
    });
  });

  async function refreshAllData() {
    products = await getProduct();
    salesHistory = await getAllSales();
    salesAnalytics = await getDashboardAnalytics(); 
    returnsHistory = await getAllReturns(); 

    // Check for low stock warnings
    const lowStock = products.filter(p => p.quantity_left <= 5);
    if (lowStock.length > 0) {
      toast.warning("Low Stock Alert", `${lowStock.length} items require replenishment.`, 5000);
    }
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
  async function refreshActiveBill(): Promise<void> {
    if (!activeBill) return;
    try {
      const updatedBill = await getBillById(activeBill.id);
      if (updatedBill) {
        activeBill = updatedBill as Bill; 
      }
    } catch (err) {
      console.error("Failed to refresh bill", err);
    }
  }

  async function handleCreateBill() {
    const bill = await createDraftBill({ customer_name: customerName, customer_phone: customerPhone, customer_email: customerEmail });
    if (bill) activeBill = bill;
  }

  async function handleAddItemToBill() {
    if (!activeBill) return;
    if (!saleSku) {
      toast.warning("Select Product", "Please select a product from the list or picker before appending.");
      return;
    }
    if (!saleQty || saleQty < 1) {
      toast.warning("Invalid Quantity", "Item quantity must be at least 1.");
      return;
    }
    
    const updatedBill = await addItemToBill(activeBill.id, { 
      product_id: String(Number(saleSku)), 
      quantity: Number(saleQty) 
    });
    
    if (updatedBill) { 
      activeBill = updatedBill as Bill;
      toast.success("Item Appended", "Product line item has been added to invoice draft.");
      saleSku = ""; 
      saleQty = 1; 
    }
  }

  async function handleRemoveItem(itemId: number) {
    if (!activeBill) return;
    
    const updatedBill = await removeItemFromBill(activeBill.id, itemId);
    if (updatedBill) {
      activeBill = updatedBill as Bill;
      toast.info("Item Removed", "Line item has been removed from invoice draft.");
    } else {
      toast.error("Remove Item Failed", "Could not remove item from draft invoice.");
    }
  }

  async function handleCheckoutAndFinalize() {
    if (!activeBill) return;
    
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
    showLanding = true; 
    
    products = [];
    salesHistory = [];
    returnsHistory = [];
    salesAnalytics = null;
    activeBill = null;
    customerName = "";
    customerPhone = "";
    customerEmail = "";
    saleSku = "";
    saleQty = 1;
    billingDiscount = 0;
    billingTax = 0;

    window.history.pushState({}, "", "/"); // Reset URL to root
  }
</script>

{#if showLanding}
  <Landing launchApp={handleLaunch} />

{:else}
  <Toast />
  <CommandPalette 
    bind:isOpen={isCmdOpen} 
    {products} 
    onClose={() => isCmdOpen = false} 
    onNavigate={navigate}
    onSelectProduct={(p) => {
      saleSku = p.sku;
      navigate('counter');
    }}
  />

  <div class="StashGo-Layout">
    
    <!-- Top Header Navigation Bar -->
    <header class="app-header">
      <button class="header-brand-btn" onclick={() => navigate("landing")}>
        <span class="logo-box">📦</span>
        <span class="logo-text">Stash <span class="gradient-accent">GO</span></span>
      </button>

      <div class="header-status">
        <span class="status-pill {backendStatus === 'ok' ? 'online' : 'offline'}">
          <span class="dot"></span> Backend: {backendStatus}
        </span>
      </div>

      <nav class="app-nav">
        <!-- Direct Landing link -->
        <button class="nav-btn home-link" onclick={() => navigate("landing")}>
          <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>
          Home
        </button>

        {#if isAuthenticated}
          <button class="nav-btn" class:active={activePage === "dashboard"} onclick={() => navigate("dashboard")}>Dashboard</button>
          <button class="nav-btn" class:active={activePage === "inventory"} onclick={() => navigate("inventory")}>Inventory</button>
          <button class="nav-btn" class:active={activePage === "counter"} onclick={() => navigate("counter")}>Billing Counter</button>
          <button class="nav-btn" class:active={activePage === "sales"} onclick={() => navigate("sales")}>Sales Ledger</button>
          <button class="nav-btn" class:active={activePage === "returns"} onclick={() => navigate("returns")}>Returns</button>
          <button class="btn-logout" onclick={handleLogout}>Logout</button>
        {:else}
          <button class="nav-btn primary-login" onclick={() => activePage = "login"}>Shopkeeper Login</button>
        {/if}
      </nav>
    </header>

    <main class="app-main-content">
      {#if !isAuthenticated}
        <Login onLoginSuccess={() => { 
          isAuthenticated = true; 
          navigate("dashboard");
          refreshAllData(); 
        }} />

      {:else}
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
      {/if}
    </main>
  </div>
{/if}

<style>
  .StashGo-Layout {
    min-height: 100vh;
    background-color: var(--bg-app);
    color: var(--text-main);
  }

  .app-header {
    background: var(--glass-bg);
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border-bottom: var(--glass-border-subtle);
    padding: 14px 40px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: var(--shadow-sm);
    transition: background 0.3s ease;
  }

  .header-brand-btn {
    background: transparent;
    border: none;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 0;
    transition: transform 0.2s ease;
  }

  .header-brand-btn:hover {
    transform: scale(1.02);
  }

  .logo-box {
    font-size: 20px;
    background: rgba(15, 90, 71, 0.08);
    padding: 6px 10px;
    border-radius: 10px;
    border: 1px solid rgba(15, 90, 71, 0.2);
  }

  .logo-text {
    font-size: 22px;
    font-weight: 800;
    color: var(--accent-primary);
    letter-spacing: -0.5px;
  }

  .app-nav {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .nav-btn {
    background: transparent;
    border: none;
    color: var(--text-muted);
    padding: 8px 16px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 600;
    border-radius: 20px;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .nav-btn:hover {
    color: var(--accent-primary);
    background: #f1f5f9;
  }

  .nav-btn.active {
    color: #ffffff;
    background: var(--accent-primary);
    box-shadow: 0 4px 12px rgba(15, 90, 71, 0.25);
  }

  .home-link {
    color: var(--accent-secondary);
  }

  .primary-login {
    background: var(--accent-primary);
    color: #ffffff !important;
    padding: 8px 20px;
  }

  .btn-logout {
    background: rgba(225, 29, 72, 0.08);
    border: 1px solid rgba(225, 29, 72, 0.2);
    color: var(--accent-danger);
    padding: 8px 16px;
    cursor: pointer;
    font-size: 13px;
    font-weight: 700;
    border-radius: 20px;
    margin-left: 10px;
    transition: all 0.2s ease;
  }

  .btn-logout:hover {
    background: var(--accent-danger);
    color: #ffffff;
  }

  .status-pill {
    font-size: 12px;
    padding: 4px 12px;
    border-radius: 20px;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .status-pill .dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
  }

  .status-pill.online {
    background: rgba(16, 185, 129, 0.12);
    color: #047857;
    border: 1px solid rgba(16, 185, 129, 0.25);
  }

  .status-pill.online .dot {
    background: var(--accent-success);
    box-shadow: 0 0 6px var(--accent-success);
  }

  .status-pill.offline {
    background: rgba(225, 29, 72, 0.12);
    color: var(--accent-danger);
    border: 1px solid rgba(225, 29, 72, 0.25);
  }

  .status-pill.offline .dot {
    background: var(--accent-danger);
  }

  .app-main-content {
    max-width: 1240px;
    margin: 30px auto;
    padding: 0 20px;
  }
</style>