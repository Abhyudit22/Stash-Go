<script lang="ts">
  import type { Product, BillItem, Bill } from './types';
  import { toast } from './toastStore';

  let {
    products = [],
    activeBill = null,
    handleCreateBill = async () => {},
    handleAddItemToBill = async () => {},
    handleRemoveItem = async () => {},
    handleCheckoutAndFinalize = async () => {},
    customerName = $bindable(""),
    customerPhone = $bindable(""),
    customerEmail = $bindable(""),
    saleSku = $bindable(""),
    saleQty = $bindable(1),
    billingDiscount = $bindable(0),
    billingTax = $bindable(0),
    paymentMethod = $bindable("Cash")
  }: {
    products?: Product[];
    activeBill?: Bill | null;
    handleCreateBill?: () => Promise<void>;
    handleAddItemToBill?: () => Promise<void>;
    handleRemoveItem?: (itemId: number) => Promise<void>;
    handleCheckoutAndFinalize?: () => Promise<void>;
    customerName?: string;
    customerPhone?: string;
    customerEmail?: string;
    saleSku?: string;
    saleQty?: number;
    billingDiscount?: number;
    billingTax?: number;
    paymentMethod?: string;
  } = $props();

  let searchQuery = $state("");
  let showReceiptModal = $state(false);
  let lastFinalizedReceipt: any = $state(null);

  let filteredProducts = $derived(
    products.filter(p => 
      p.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
      p.sku.toLowerCase().includes(searchQuery.toLowerCase())
    )
  );

  function getDisplayName(item: BillItem): string {
    if (item.product_name) return item.product_name;
    const matchedProduct = products.find(p => String(p.id) === String(item.product_id));
    return matchedProduct ? matchedProduct.name : `Item #${item.product_id}`;
  }

  function getDisplayPrice(item: BillItem): number {
    if (item.price) return Number(item.price); 
    const matchedProduct = products.find(p => String(p.id) === String(item.product_id));
    return matchedProduct ? Number(matchedProduct.selling_price) : 0; 
  }

  let currentSubtotal = $derived(activeBill?.subtotal || 0);
  let calculatedDiscount = $derived(currentSubtotal * ((billingDiscount || 0) / 100));
  let calculatedTax = $derived(currentSubtotal * ((billingTax || 0) / 100));
  let grandTotal = $derived(Math.max(0, currentSubtotal - calculatedDiscount + calculatedTax));

  async function localCheckout() {
    if (!activeBill || !activeBill.items || activeBill.items.length === 0) {
      toast.error("Checkout Failed", "Please add at least one product line item to the bill draft.");
      return;
    }

    lastFinalizedReceipt = {
      billNumber: activeBill.bill_number || `INV-${Date.now().toString().slice(-6)}`,
      customerName: activeBill.customer_name,
      customerPhone: activeBill.customer_phone,
      items: [...activeBill.items],
      subtotal: currentSubtotal,
      discount: calculatedDiscount,
      discountPct: billingDiscount,
      tax: calculatedTax,
      taxPct: billingTax,
      grandTotal: grandTotal,
      paymentMethod: paymentMethod,
      date: new Date().toLocaleString()
    };

    await handleCheckoutAndFinalize();
    toast.success("Checkout Successful", `Order #${lastFinalizedReceipt.billNumber} has been finalized.`);
    showReceiptModal = true;
  }

  function printThermalReceipt() {
    window.print();
  }
</script>

<div class="page-view animate-fade-in">
  <div class="terminal-header">
    <div>
      <h2 class="gradient-text-header">DIGITAL BILLING COUNTER TERMINAL</h2>
      <p class="subtitle">Open active draft containers, compile customer orders dynamically, and finalize records.</p>
    </div>
  </div>

  <div class="checkout-layout-grid">
    <div class="panel-card">
      
      {#if !activeBill}
        <div class="panel-title text-cyan">Step 1: Initialize Customer Invoice</div>
        <form onsubmit={(e) => { e.preventDefault(); handleCreateBill(); }} class="stacked-form">
          <div class="field-group">
            <label for="cust-name">Customer Full Name</label>
            <input type="text" id="cust-name" bind:value={customerName} placeholder="e.g., John Doe" required />
          </div>

          <div class="field-row">
            <div class="field-group">
              <label for="cust-phone">Mobile Phone String</label>
              <input type="text" id="cust-phone" bind:value={customerPhone} placeholder="e.g., 9876543210" required />
            </div>

            <div class="field-group">
              <label for="cust-email">Email Address</label>
              <input type="email" id="cust-email" bind:value={customerEmail} placeholder="e.g., john@gmail.com" required />
            </div>
          </div>

          <button type="submit" class="btn-action primary">Initialize New Invoice Draft</button>
        </form>
      
      {:else}
        <div class="panel-title text-cyan">Step 2: Add Products (Quick Picker Grid)</div>
        
        <div class="field-group margin-bottom-sm">
          <input type="text" bind:value={searchQuery} placeholder="🔍 Filter inventory products..." class="search-input" />
        </div>

        <!-- Visual Product Cards Picker Grid -->
        <div class="visual-picker-grid">
          {#each filteredProducts.slice(0, 6) as product}
            <button 
              type="button"
              class="visual-pick-card" 
              class:selected={saleSku === String(product.id)}
              onclick={() => {
                saleSku = String(product.id);
                handleAddItemToBill();
              }}
            >
              <span class="pick-name">{product.name}</span>
              <span class="pick-meta">SKU: {product.sku}</span>
              <div class="pick-footer">
                <span class="pick-price">₹{product.selling_price}</span>
                <span class="pick-stock" class:low={product.quantity_left <= 5}>Qty: {product.quantity_left}</span>
              </div>
            </button>
          {/each}
        </div>

        <form onsubmit={(e) => { e.preventDefault(); handleAddItemToBill(); }} class="stacked-form margin-top">
          <div class="field-row">
            <div class="field-group flex-2">
              <label for="bill-sku">Selected Product SKU</label>
              <select id="bill-sku" bind:value={saleSku} class="listbox-select" required>
                <option value="" disabled>-- Select a product --</option>
                {#each filteredProducts as product}
                  <option value={String(product.id)}>
                    {product.name} — ₹{product.selling_price} [Stock: {product.quantity_left}]
                  </option>
                {/each}
              </select>
            </div>

            <div class="field-group flex-1">
              <label for="bill-qty">Quantity</label>
              <input type="number" id="bill-qty" bind:value={saleQty} min="1" required />
            </div>
          </div>

          <button type="submit" class="btn-action secondary">Append Item Line</button>
        </form>

        <div class="panel-title margin-top text-amber">Step 3: Financial Modifiers</div>
        <form onsubmit={(e) => { e.preventDefault(); localCheckout(); }} class="stacked-form">
          <div class="field-row">
            <div class="field-group">
              <label for="bill-disc">Discount (%)</label>
              <input type="number" id="bill-disc" bind:value={billingDiscount} min="0" max="100" />
            </div>

            <div class="field-group">
              <label for="bill-tax">Tax Surcharge (%)</label>
              <input type="number" id="bill-tax" bind:value={billingTax} min="0" max="100" />
            </div>
          </div>

          <div class="field-group">
            <label for="bill-pay">Payment Method Requirement</label>
            <select id="bill-pay" bind:value={paymentMethod} required>
              <option value="Cash">Cash Currency Tender</option>
              <option value="UPI">UPI Digital Payment</option>
              <option value="Card">Credit / Debit Card Terminal</option>
            </select>
          </div>

          <button type="submit" class="btn-action success">Lock & Finalize Checkout Order</button>
        </form>
      {/if}
    </div>

    <div class="panel-card dark-bg">
      <div class="panel-title text-cyan text-center">Live Invoice Ledger Preview</div>
      
      {#if !activeBill}
        <div class="placeholder-box">
          <p>Initialize a customer invoice container draft sequence from the control console workspace panel.</p>
        </div>
      {:else}
        <div class="invoice-receipt">
          <div class="receipt-header">
            <h3>Invoice: <span class="text-cyan">{activeBill.bill_number || 'DRAFT'}</span></h3>
            <p><strong>Customer:</strong> {activeBill.customer_name} ({activeBill.customer_phone})</p>
            <p>Status: <span class="badge-draft">DRAFT IN PROGRESS</span></p>
          </div>

          <div class="table-frame">
            <table>
              <thead>
                <tr>
                  <th>Item Description</th>
                  <th>Qty</th>
                  <th>Rate</th>
                  <th>Net</th>
                  <th class="text-center">Action</th>
                </tr>
              </thead>
              <tbody>
                {#if !activeBill.items || activeBill.items.length === 0}
                  <tr>
                    <td colspan="5" class="text-center text-muted">No items appended to this draft invoice yet.</td>
                  </tr>
                {:else}
                  {#each activeBill.items as item}
                    <tr>
                      <td class="font-medium text-white">{getDisplayName(item)}</td>
                      <td>{item.quantity}</td>
                      <td>₹{getDisplayPrice(item).toFixed(2)}</td>
                      <td class="text-green font-bold">₹{(getDisplayPrice(item) * item.quantity).toFixed(2)}</td>
                      <td class="text-center">
                        <button type="button" class="btn-icon-delete" onclick={() => handleRemoveItem(item.id)} title="Remove item from bill">✕</button>
                      </td>
                    </tr>
                  {/each}
                {/if}
              </tbody>
            </table>
          </div>

          <div class="summary-breakdown">
            <div class="summary-line">
              <span>Items Subtotal:</span>
              <span>₹{currentSubtotal.toFixed(2)}</span>
            </div>

            <div class="summary-line text-amber">
              <span>Applied Discount ({billingDiscount || 0}%):</span>
              <span>- ₹{calculatedDiscount.toFixed(2)}</span>
            </div>

            <div class="summary-line text-cyan">
              <span>Tax Surcharge ({billingTax || 0}%):</span>
              <span>+ ₹{calculatedTax.toFixed(2)}</span>
            </div>

            <div class="summary-grand">
              <span>Final Outstanding Balance:</span>
              <span class="grand-price text-green">₹{grandTotal.toFixed(2)}</span>
            </div>
          </div>
        </div>
      {/if}
    </div>
  </div>
</div>

<!-- Thermal Receipt Preview Modal -->
{#if showReceiptModal && lastFinalizedReceipt}
  <div 
    class="modal-overlay" 
    onclick={() => showReceiptModal = false}
    onkeydown={(e) => { if (e.key === 'Escape') showReceiptModal = false; }}
    role="dialog"
    aria-modal="true"
    tabindex="-1"
  >
    <div class="modal-card printable-thermal-receipt" role="document">
      <div class="thermal-header">
        <h2>STASH GO RETAIL</h2>
        <p>High Performance Terminal POS</p>
        <div class="thermal-divider">--------------------------------</div>
        <p>Order: #{lastFinalizedReceipt.billNumber}</p>
        <p>Date: {lastFinalizedReceipt.date}</p>
        <p>Customer: {lastFinalizedReceipt.customerName}</p>
        <div class="thermal-divider">--------------------------------</div>
      </div>

      <div class="thermal-items">
        {#each lastFinalizedReceipt.items as item}
          <div class="thermal-line">
            <span>{getDisplayName(item)} x{item.quantity}</span>
            <span>₹{(getDisplayPrice(item) * item.quantity).toFixed(2)}</span>
          </div>
        {/each}
      </div>

      <div class="thermal-divider">--------------------------------</div>

      <div class="thermal-totals">
        <div class="thermal-line"><span>Subtotal:</span><span>₹{lastFinalizedReceipt.subtotal.toFixed(2)}</span></div>
        <div class="thermal-line"><span>Discount ({lastFinalizedReceipt.discountPct}%):</span><span>-₹{lastFinalizedReceipt.discount.toFixed(2)}</span></div>
        <div class="thermal-line"><span>Tax ({lastFinalizedReceipt.taxPct}%):</span><span>+₹{lastFinalizedReceipt.tax.toFixed(2)}</span></div>
        <div class="thermal-line grand"><span>TOTAL:</span><span>₹{lastFinalizedReceipt.grandTotal.toFixed(2)}</span></div>
        <div class="thermal-line"><span>Payment:</span><span>{lastFinalizedReceipt.paymentMethod}</span></div>
      </div>

      <div class="thermal-footer">
        <div class="thermal-divider">--------------------------------</div>
        <p>Thank you for shopping with us!</p>
        <div class="no-print modal-actions">
          <button type="button" class="btn-print" onclick={printThermalReceipt}>🖨️ Print Thermal Receipt</button>
          <button type="button" class="btn-close-modal" onclick={() => showReceiptModal = false}>Close</button>
        </div>
      </div>
    </div>
  </div>
{/if}

<style>
  .terminal-header { margin-bottom: 24px; }
  .page-view h2 { font-size: 24px; margin: 0 0 4px 0; color: var(--accent-primary); }
  .subtitle { color: var(--text-muted); font-size: 14px; margin: 0; }
  
  .checkout-layout-grid { display: grid; grid-template-columns: 1fr 1.2fr; gap: 24px; width: 100%; }

  @media (max-width: 900px) {
    .checkout-layout-grid { grid-template-columns: 1fr; }
  }
  
  .panel-card {
    background: var(--bg-card);
    border: 1px solid var(--border-light);
    padding: 24px;
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-sm);
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
  }

  .panel-card.dark-bg { background: var(--bg-card-hover); }
  
  .panel-title { font-size: 13px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 16px; border-bottom: 1px solid var(--border-light); padding-bottom: 8px; color: var(--accent-primary); }
  .panel-title.margin-top { margin-top: 24px; }

  .stacked-form { display: flex; flex-direction: column; gap: 14px; }
  .field-row { display: flex; gap: 14px; width: 100%; }
  .field-group { flex: 1; display: flex; flex-direction: column; }
  .flex-2 { flex: 2; }
  .flex-1 { flex: 1; }
  
  .field-group label { display: block; font-size: 12px; color: var(--text-muted); margin-bottom: 6px; font-weight: 600; }

  input, select {
    background: var(--bg-input);
    border: 1px solid var(--border-solid);
    padding: 10px 12px;
    color: var(--text-main);
    border-radius: 8px;
    font-size: 13px;
    width: 100%;
    box-sizing: border-box;
  }

  input:focus, select:focus { outline: none; border-color: var(--accent-primary); box-shadow: 0 0 0 3px rgba(15, 90, 71, 0.12); }
  
  .search-input { margin-bottom: 4px; }
  .listbox-select { height: 42px; font-size: 13px; }

  /* Visual Pick Grid */
  .visual-picker-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
    gap: 10px;
    margin-bottom: 12px;
  }

  .visual-pick-card {
    background: var(--bg-card);
    border: 1px solid var(--border-light);
    border-radius: 10px;
    padding: 10px;
    text-align: left;
    cursor: pointer;
    display: flex;
    flex-direction: column;
    gap: 4px;
    transition: all 0.2s ease;
  }

  .visual-pick-card:hover {
    border-color: var(--accent-primary);
    transform: translateY(-2px);
  }

  .visual-pick-card.selected {
    border-color: var(--accent-primary);
    background: rgba(15, 90, 71, 0.08);
  }

  .pick-name { font-size: 12px; font-weight: 700; color: var(--text-main); line-height: 1.2; }
  .pick-meta { font-size: 10px; color: var(--text-muted); font-family: monospace; }
  .pick-footer { display: flex; justify-content: space-between; margin-top: 4px; font-size: 11px; }
  .pick-price { font-weight: 800; color: #047857; }
  .pick-stock { color: var(--text-muted); }
  .pick-stock.low { color: var(--accent-danger); font-weight: bold; }

  .btn-action {
    border: none;
    padding: 12px;
    font-weight: 700;
    font-size: 13px;
    text-transform: uppercase;
    border-radius: 8px;
    cursor: pointer;
    color: #ffffff;
    transition: transform 0.2s ease;
    width: 100%;
    margin-top: 4px;
  }

  .btn-action.primary { background: var(--accent-primary); }
  .btn-action.secondary { background: var(--accent-secondary); }
  .btn-action.success { background: #047857; }
  .btn-action:hover { transform: translateY(-1px); }

  .invoice-receipt { display: flex; flex-direction: column; gap: 16px; }
  .receipt-header h3 { margin: 0 0 6px 0; font-size: 18px; color: var(--text-main); }
  .receipt-header p { margin: 2px 0; font-size: 13px; color: var(--text-muted); }
  
  .badge-draft { background: rgba(217, 119, 6, 0.12); color: var(--accent-warning); padding: 2px 8px; border-radius: 12px; font-size: 10px; font-weight: 800; }

  .table-frame { overflow-x: auto; border: 1px solid var(--border-light); border-radius: 8px; }
  table { width: 100%; border-collapse: collapse; background: var(--bg-card); font-size: 13px; }
  th { background: var(--bg-card-hover); color: var(--text-muted); font-size: 11px; text-transform: uppercase; padding: 10px; text-align: left; }
  td { padding: 10px; border-bottom: 1px solid var(--border-light); }

  .btn-icon-delete { background: transparent; border: none; color: var(--accent-danger); cursor: pointer; font-size: 14px; font-weight: bold; }

  .summary-breakdown { display: flex; flex-direction: column; gap: 8px; border-top: 1px dashed var(--border-light); padding-top: 14px; }
  .summary-line { display: flex; justify-content: space-between; font-size: 13px; color: var(--text-muted); }
  .summary-grand { display: flex; justify-content: space-between; font-size: 16px; font-weight: 800; color: var(--text-main); margin-top: 8px; padding-top: 10px; border-top: 1px solid var(--border-light); }
  
  .grand-price { font-size: 20px; font-weight: 800; }

  .text-cyan { color: var(--accent-secondary); }
  .text-amber { color: var(--accent-warning); }
  .text-green { color: #047857; }
  .text-center { text-align: center; }
  .font-medium { font-weight: 600; }
  .font-bold { font-weight: 700; }
  .text-white { color: var(--text-main); }
  .placeholder-box { text-align: center; padding: 60px 20px; color: var(--text-muted); font-size: 14px; }

  /* Thermal Receipt Modal */
  .modal-overlay {
    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(4px);
    z-index: 9999; display: flex; justify-content: center; align-items: center; padding: 20px;
  }

  .modal-card {
    background: #ffffff; color: #000000; padding: 24px; border-radius: 12px;
    width: 320px; box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3); font-family: monospace; font-size: 12px;
  }

  .thermal-header { text-align: center; margin-bottom: 12px; }
  .thermal-header h2 { margin: 0; font-size: 16px; color: #000; }
  .thermal-header p { margin: 2px 0; font-size: 11px; }
  .thermal-divider { margin: 8px 0; text-align: center; }

  .thermal-items { display: flex; flex-direction: column; gap: 4px; }
  .thermal-line { display: flex; justify-content: space-between; }
  .thermal-line.grand { font-weight: bold; font-size: 13px; margin-top: 4px; }

  .thermal-footer { text-align: center; margin-top: 12px; }

  .modal-actions { display: flex; flex-direction: column; gap: 8px; margin-top: 16px; }
  .btn-print { background: var(--accent-primary); color: #fff; border: none; padding: 10px; border-radius: 6px; font-weight: bold; cursor: pointer; }
  .btn-close-modal { background: #e2e8f0; color: #334155; border: none; padding: 8px; border-radius: 6px; cursor: pointer; }

  @media (max-width: 600px) {
    .panel-card {
      padding: 16px;
    }
    .field-row {
      flex-direction: column;
      gap: 10px;
    }
    .visual-picker-grid {
      grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
      gap: 8px;
    }
    .visual-pick-card {
      padding: 8px;
    }
    .pick-name {
      font-size: 11px;
    }
    .pick-price {
      font-size: 11px;
    }
    .pick-stock {
      font-size: 10px;
    }
    table {
      font-size: 11px;
    }
    th, td {
      padding: 8px 6px;
    }
    .summary-grand {
      font-size: 14px;
    }
    .grand-price {
      font-size: 16px;
    }
    .modal-card {
      width: 100%;
      max-width: 320px;
      padding: 16px;
    }
  }
</style>