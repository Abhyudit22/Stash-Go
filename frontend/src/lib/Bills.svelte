<script lang="ts">
  import type { Product, BillItem, Bill } from './types';

  export let products: Product[] = [];
  export let activeBill: Bill | null = null;

  export let handleCreateBill: () => Promise<void>;
  export let handleAddItemToBill: () => Promise<void>;
  export let handleRemoveItem: (itemId: number) => Promise<void>;
  export let handleCheckoutAndFinalize: () => Promise<void>;

  export let customerName: string;
  export let customerPhone: string;
  export let customerEmail: string;
  export let saleSku: string = ""; 
  export let saleQty: number;
  export let billingDiscount: number; // Now represents a %
  export let billingTax: number;      // Now represents a %
  export let paymentMethod: string;

  let searchQuery = "";
  $: filteredProducts = products.filter(p => 
    p.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
    p.sku.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // --- BULLETPROOF LOOKUP HELPERS ---
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

  // --- PERCENTAGE MATH (Converts % to ₹) ---
  $: currentSubtotal = activeBill?.subtotal || 0;
  $: calculatedDiscount = currentSubtotal * ((billingDiscount || 0) / 100);
  $: calculatedTax = currentSubtotal * ((billingTax || 0) / 100);
  $: grandTotal = Math.max(0, currentSubtotal - calculatedDiscount + calculatedTax);
</script>

<div class="page-view animate-fade-in">
  <div class="terminal-header">
    <div>
      <h2>DIGITAL BILLING COUNTER TERMINAL</h2>
      <p class="subtitle">Open active draft containers, compile customer orders dynamically, and finalize records.</p>
    </div>
  </div>

  <div class="checkout-layout-grid">
    <div class="panel-card">
      
      {#if !activeBill}
        <div class="panel-title">Step 1: Initialize Customer Invoice</div>
        <form on:submit|preventDefault={handleCreateBill} class="stacked-form">
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
        <div class="panel-title">Step 2: Scan Line Items</div>
        <form on:submit|preventDefault={handleAddItemToBill} class="stacked-form">
          
          <div class="field-group">
            <label for="search-sku">Search Inventory (Name or SKU)</label>
            <input type="text" id="search-sku" bind:value={searchQuery} placeholder="Type to filter items..." class="search-input" />
          </div>

          <div class="field-group">
            <label for="bill-sku">Select Product</label>
            <select id="bill-sku" bind:value={saleSku} size="4" class="listbox-select" required>
              {#each filteredProducts as product}
                <option value={String(product.id)}>
                  {product.name} — ₹{product.selling_price} [Stock: {product.quantity_left}]
                </option>
              {/each}
              {#if filteredProducts.length === 0}
                <option value="" disabled>No products match your search.</option>
              {/if}
            </select>
          </div>

          <div class="field-group">
            <label for="bill-qty">Order Item Quantity</label>
            <input type="number" id="bill-qty" bind:value={saleQty} min="1" required />
          </div>
          <button type="submit" class="btn-action secondary">Append Item Line</button>
        </form>

        <div class="panel-title margin-top">Step 3: Financial Modifiers</div>
        <form on:submit|preventDefault={handleCheckoutAndFinalize} class="stacked-form">
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
            <h3>Invoice Number: {activeBill.bill_number || 'DRAFT'}</h3>
            <p><strong>Customer:</strong> {activeBill.customer_name} ({activeBill.customer_phone})</p>
            <p>Status: <span class="badge-draft">DRAFT</span></p>
          </div>

          <div class="table-frame">
            <table>
              <thead>
                <tr>
                  <th>Item ID Reference</th>
                  <th>Qty</th>
                  <th>Unit Rate</th>
                  <th>Net Total</th>
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
                      <td class="font-medium">{getDisplayName(item)}</td>
                      <td>{item.quantity}</td>
                      <td>₹{getDisplayPrice(item).toFixed(2)}</td>
                      <td class="text-white font-bold">₹{(getDisplayPrice(item) * item.quantity).toFixed(2)}</td>
                      <td class="text-center">
                        <button type="button" class="btn-icon-delete" on:click={() => handleRemoveItem(item.id)} title="Remove item from bill">✕</button>
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
            <div class="summary-line text-red">
              <span>Applied Discount ({billingDiscount || 0}%):</span>
              <span>- ₹{calculatedDiscount.toFixed(2)}</span>
            </div>
            <div class="summary-line text-cyan">
              <span>Tax Surcharge ({billingTax || 0}%):</span>
              <span>+ ₹{calculatedTax.toFixed(2)}</span>
            </div>
            <div class="summary-total">
              <span>Estimated Bill Total:</span>
              <span>₹{grandTotal.toFixed(2)}</span>
            </div>
          </div>
        </div>
      {/if}
    </div>
  </div>
</div>

<style>
  .terminal-header { margin-bottom: 30px; }
  .page-view h2 { color: #ffffff; font-size: 22px; margin: 0 0 6px 0; }
  .subtitle { color: #8e8e9a; font-size: 14px; margin: 0; }
  .checkout-layout-grid { display: grid; grid-template-columns: 1fr 1.2fr; gap: 30px; width: 100%; }
  
  .panel-card { background: #1e1e24; border: 1px solid #29292e; padding: 25px; border-radius: 8px; box-sizing: border-box; display: flex; flex-direction: column; }
  .panel-card.dark-bg { background: #15151a; }
  .panel-title { font-size: 13px; font-weight: bold; text-transform: uppercase; color: #00bcd4; letter-spacing: 0.8px; margin-bottom: 20px; border-bottom: 1px solid #29292e; padding-bottom: 8px; }
  .panel-title.margin-top { margin-top: 25px; }
  
  .stacked-form { display: flex; flex-direction: column; gap: 14px; }
  .field-row { display: flex; gap: 14px; width: 100%; }
  .field-group { flex: 1; display: flex; flex-direction: column; }
  .field-group label { font-size: 13px; color: #b0bec5; margin-bottom: 6px; font-weight: bold; }
  
  input, select { background: #2a2a35; border: 1px solid #3a3a47; padding: 12px; color: #ffffff; border-radius: 4px; font-size: 14px; width: 100%; box-sizing: border-box; }
  input:focus, select:focus { outline: none; border-color: #00bcd4; }
  
  .search-input { border-bottom-left-radius: 0; border-bottom-right-radius: 0; border-bottom: 1px dashed #444; background: #202028; }
  .listbox-select { border-top-left-radius: 0; border-top-right-radius: 0; padding: 8px; }
  .listbox-select option { padding: 8px; border-bottom: 1px solid #29292e; cursor: pointer; }
  .listbox-select option:checked { background: #00bcd4; color: #121214; font-weight: bold; }

  .btn-action { border: none; padding: 12px; font-weight: bold; border-radius: 4px; cursor: pointer; font-size: 13px; text-transform: uppercase; margin-top: 6px; transition: background 0.2s; }
  .btn-action.primary { background: #00bcd4; color: #121214; }
  .btn-action.primary:hover { background: #0097a7; }
  .btn-action.secondary { background: #ff9800; color: #121214; }
  .btn-action.secondary:hover { background: #e68a00; }
  .btn-action.success { background: #4caf50; color: #121214; padding: 14px; font-size: 14px; }
  .btn-action.success:hover { background: #388e3c; }
  
  .placeholder-box { text-align: center; color: #7c7c8a; font-size: 14px; padding: 60px 20px; border: 2px dashed #29292e; border-radius: 6px; margin: auto 0; }
  .invoice-receipt { display: flex; flex-direction: column; gap: 20px; background: #1e1e24; border: 1px solid #29292e; padding: 20px; border-radius: 6px; }
  .receipt-header h3 { margin: 0 0 10px 0; color: #ffffff; font-size: 16px; font-family: monospace; }
  .receipt-header p { margin: 4px 0; font-size: 13px; color: #b0bec5; }
  .badge-draft { background: rgba(255, 152, 0, 0.15); color: #ff9800; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: bold; }
  
  .table-frame { overflow-x: auto; width: 100%; margin-top: 10px; }
  table { width: 100%; border-collapse: collapse; }
  th { background: #23232b; color: #8e8e9a; font-size: 11px; text-transform: uppercase; padding: 10px; text-align: left; }
  td { padding: 10px; border-bottom: 1px solid #15151a; font-size: 13px; color: #e1e1e6; vertical-align: middle; }
  .font-medium { font-weight: 500; }
  .text-white { color: #ffffff; }
  .font-bold { font-weight: bold; }
  
  .btn-icon-delete { background: rgba(255, 82, 82, 0.1); border: 1px solid rgba(255, 82, 82, 0.3); color: #ff5252; font-weight: bold; padding: 6px 10px; border-radius: 4px; cursor: pointer; transition: all 0.2s; }
  .btn-icon-delete:hover { background: #ff5252; color: #ffffff; }

  .summary-breakdown { display: flex; flex-direction: column; gap: 8px; border-top: 1px dashed #3a3a47; padding-top: 15px; margin-top: 10px; }
  .summary-line { display: flex; justify-content: space-between; font-size: 13px; color: #b0bec5; }
  .summary-total { display: flex; justify-content: space-between; font-size: 15px; font-weight: bold; color: #4caf50; border-top: 1px solid #29292e; padding-top: 10px; margin-top: 5px; }
  
  .text-center { text-align: center !important; }
  .text-muted { color: #7c7c8a; }
  .text-cyan { color: #00bcd4; }
  .text-red { color: #ff5252; }
  
  .animate-fade-in { animation: fadeIn 0.25s ease-out forwards; }
  @keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }
</style>