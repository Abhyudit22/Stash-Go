<script lang="ts">
  import type { Product } from "./types";

  // Component Props Interfaces
  export let products: Product[] = [];
  export let handleAddProduct: () => Promise<void>;
  export let handleStockChange: (sku: string, action: "increase-stock" | "decrease-stock") => Promise<void>;
  export let handleRemove: (id: number) => Promise<void>;

  // Defined object structural configuration mapping
  export let newProduct: {
    sku: string;
    name: string;
    cost_price: number;
    selling_price: number;
    quantity_left: number;
  };
</script>

<div class="page-view animate-fade-in">
  <div class="terminal-header">
    <div>
      <h2>INVENTORY CONTROL WORKSTATION</h2>
      <p class="subtitle">Register retail items, monitor stock levels, and manually patch quantity variances.</p>
    </div>
    <div class="terminal-badge">Total SKUs: {products.length}</div>
  </div>

  <div class="inventory-layout-grid">
    <div class="panel-card">
      <div class="panel-title">Product Provisioning Console</div>
      <form onsubmit={(e) => { e.preventDefault(); handleAddProduct(); }} class="stacked-form">
        <div class="field-group">
          <label for="inv-sku">Unique SKU Reference Identifier</label>
          <input type="text" id="inv-sku" bind:value={newProduct.sku} placeholder="e.g., PROD-CHIPS-01" required />
        </div>
        <div class="field-group">
          <label for="inv-name">Product Name Label</label>
          <input type="text" id="inv-name" bind:value={newProduct.name} placeholder="e.g., Potato Chips Spicy" required />
        </div>
        <div class="field-row">
          <div class="field-group">
            <label for="inv-cost">Cost Price (₹)</label>
            <input type="number" id="inv-cost" bind:value={newProduct.cost_price} min="0" step="0.01" placeholder="0.00" required />
          </div>
          <div class="field-group">
            <label for="inv-sell">Selling Price (₹)</label>
            <input type="number" id="inv-sell" bind:value={newProduct.selling_price} min="0" step="0.01" placeholder="0.00" required />
          </div>
        </div>
        <div class="field-group">
          <label for="inv-qty">Initial Opening Stock Quantity</label>
          <input type="number" id="inv-qty" bind:value={newProduct.quantity_left} min="0" placeholder="100" required />
        </div>
        <button type="submit" class="btn-add-product">Provision New Product Line</button>
      </form>
    </div>

    <div class="panel-card">
      <div class="panel-title">Master Stock Ledger Sheet</div>
      {#if products.length === 0}
        <div class="empty-box">No inventory listings registered in your system architecture layout nodes.</div>
      {:else}
        <div class="table-frame">
          <table>
            <thead>
              <tr>
                <th class="index-th">S.No</th>
                <th>SKU ID</th>
                <th>Item Label</th>
                <th>Retail Matrix</th>
                <th>Units Left</th>
                <th>Stock Actions</th>
              </tr>
            </thead>
            <tbody>
              {#each products as product, i}
                <tr>
                  <td class="index-cell">{i + 1}</td>
                  <td class="sku-text">{product.sku}</td>
                  <td><strong>{product.name}</strong></td>
                  <td class="price-matrix">
                    <span class="cost-tag">C: ₹{product.cost_price ? product.cost_price.toFixed(2) : '0.00'}</span>
                    <span class="sell-tag">S: ₹{product.selling_price.toFixed(2)}</span>
                  </td>
                  <td class="qty-text" class:low-stock={product.quantity_left <= 5}>
                    {product.quantity_left} units
                  </td>
                  <td class="actions-group">
                    <button type="button" class="btn-patch" onclick={() => handleStockChange(product.sku, 'increase-stock')}>+</button>
                    <button type="button" class="btn-patch" onclick={() => handleStockChange(product.sku, 'decrease-stock')}>-</button>
                    <button type="button" class="btn-remove" onclick={() => handleRemove(product.id)}>Remove</button>
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      {/if}
    </div>
  </div>
</div>

<style>
  .terminal-header, .field-row, .actions-group { display: flex; justify-content: space-between; align-items: center; }
  .terminal-header { margin-bottom: 30px; }
  .page-view h2 { color: #ffffff; font-size: 22px; margin: 0 0 6px 0; }
  .subtitle { color: #8e8e9a; font-size: 14px; margin: 0; }
  .terminal-badge { background: #1e1e24; border: 1px solid #29292e; color: #00bcd4; padding: 6px 14px; border-radius: 4px; font-size: 13px; font-weight: bold; }
  .inventory-layout-grid { display: grid; grid-template-columns: 1fr 1.4fr; gap: 30px; width: 100%; }
  @media (max-width: 900px) { .inventory-layout-grid { grid-template-columns: 1fr; } }
  .panel-card { background: #1e1e24; border: 1px solid #29292e; padding: 25px; border-radius: 8px; box-sizing: border-box; display: flex; flex-direction: column; }
  .panel-title { font-size: 13px; font-weight: bold; text-transform: uppercase; color: #00bcd4; letter-spacing: 0.8px; margin-bottom: 20px; border-bottom: 1px solid #29292e; padding-bottom: 8px; }
  .stacked-form, .price-matrix { display: flex; flex-direction: column; }
  .stacked-form { gap: 16px; }
  .field-row { gap: 16px; width: 100%; }
  .field-group { flex: 1; display: flex; flex-direction: column; }
  .field-group label { font-size: 13px; color: #b0bec5; margin-bottom: 8px; }
  input { background: #2a2a35; border: 1px solid #3a3a47; padding: 12px; color: #ffffff; border-radius: 4px; font-size: 14px; width: 100%; box-sizing: border-box; }
  input:focus { outline: none; border-color: #00bcd4; }
  .btn-add-product, .btn-remove { border-radius: 4px; cursor: pointer; font-weight: bold; }
  .btn-add-product { border: none; padding: 14px; font-size: 13px; text-transform: uppercase; background: #00bcd4; color: #121214; }
  .btn-add-product:hover { background: #0097a7; }
  .table-frame { overflow-x: auto; width: 100%; }
  table { width: 100%; border-collapse: collapse; background: #15151a; border-radius: 6px; overflow: hidden; }
  th { background: #23232b; color: #8e8e9a; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; padding: 12px; text-align: left; }
  .index-th { width: 30px; text-align: center; }
  td { padding: 12px; border-bottom: 1px solid #1e1e24; font-size: 14px; color: #e1e1e6; vertical-align: middle; }
  .index-cell { text-align: center; color: #7c7c8a; font-family: monospace; font-weight: bold; }
  .sku-text { font-family: monospace; color: #9cdcfe; font-weight: 500; }
  .price-matrix { gap: 2px; font-size: 12px; font-family: monospace; }
  .cost-tag { color: #ff8a65; }
  .sell-tag { color: #4caf50; font-weight: bold; }
  .qty-text.low-stock { color: #ff5252; font-weight: bold; background: rgba(255, 82, 82, 0.05); }
  .actions-group { gap: 6px; justify-content: flex-start; }
  .btn-patch { border: 1px solid #3a3a47; background: #2a2a35; color: #ffffff; width: 28px; height: 28px; border-radius: 4px; font-weight: bold; cursor: pointer; display: flex; align-items: center; justify-content: center; }
  .btn-patch:hover { color: #121214; }
  td:nth-child(6) button:nth-child(1):hover { background: #4caf50; border-color: #4caf50; }
  td:nth-child(6) button:nth-child(2):hover { background: #ff9800; border-color: #ff9800; }
  .btn-remove { border: 1px solid #ff5252; background: transparent; color: #ff5252; font-size: 12px; padding: 5px 10px; margin-left: 4px; }
  .btn-remove:hover { background: #ff5252; color: #ffffff; }
  .empty-box { text-align: center; color: #7c7c8a; font-size: 14px; padding: 40px 0; border: 2px dashed #29292e; border-radius: 6px; }
  .animate-fade-in { animation: fadeIn 0.25s ease-out forwards; }
  @keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }
</style>