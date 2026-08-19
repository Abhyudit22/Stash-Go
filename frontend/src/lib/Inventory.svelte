<script lang="ts">
  import type { Product } from "./types";

  let {
    products = [],
    handleAddProduct = async () => {},
    handleStockChange = async () => {},
    handleRemove = async () => {},
    newProduct = $bindable({
      sku: "",
      name: "",
      cost_price: 0,
      selling_price: 0,
      quantity_left: 0
    })
  }: {
    products?: Product[];
    handleAddProduct?: () => Promise<void>;
    handleStockChange?: (sku: string, action: "increase-stock" | "decrease-stock") => Promise<void>;
    handleRemove?: (id: number) => Promise<void>;
    newProduct?: any;
  } = $props();

  let totalCostValuation = $derived(products.reduce((sum, p) => sum + (p.cost_price * p.quantity_left), 0));
  let totalRetailValuation = $derived(products.reduce((sum, p) => sum + (p.selling_price * p.quantity_left), 0));
  let projectedProfit = $derived(totalRetailValuation - totalCostValuation);
  let averageMargin = $derived(totalRetailValuation > 0 ? (projectedProfit / totalRetailValuation) * 100 : 0);
</script>

<div class="page-view animate-fade-in">
  <div class="terminal-header">
    <div>
      <h2 class="gradient-text-header">INVENTORY CONTROL WORKSTATION</h2>
      <p class="subtitle">Register retail items, monitor stock levels, and manually patch quantity variances.</p>
    </div>
    <div class="terminal-badge">Total SKUs: {products.length}</div>
  </div>

  <!-- Financial Valuation Metrics Bar -->
  <div class="valuation-bar">
    <div class="val-card">
      <span class="val-label">TOTAL CAPITAL INVESTMENT (COST)</span>
      <span class="val-num">₹{totalCostValuation.toFixed(2)}</span>
      <span class="val-sub">Sum of (Cost Price × Stock Qty)</span>
    </div>
    <div class="val-card">
      <span class="val-label">PROJECTED RETAIL ASSET VALUE</span>
      <span class="val-num text-emerald">₹{totalRetailValuation.toFixed(2)}</span>
      <span class="val-sub">Sum of (Selling Price × Stock Qty)</span>
    </div>
    <div class="val-card">
      <span class="val-label">POTENTIAL NET PROFIT YIELD</span>
      <span class="val-num text-mint">₹{projectedProfit.toFixed(2)}</span>
      <span class="val-sub">Avg Margin: <strong>{averageMargin.toFixed(1)}%</strong></span>
    </div>
  </div>

  <div class="inventory-layout-grid">
    <div class="panel-card">
      <div class="panel-title text-cyan">Product Provisioning Console</div>
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
      <div class="panel-title text-indigo">Master Stock Ledger Sheet</div>
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
                  <td><strong class="text-white">{product.name}</strong></td>
                  <td class="price-matrix">
                    <span class="cost-tag">C: ₹{product.cost_price ? product.cost_price.toFixed(2) : '0.00'}</span>
                    <span class="sell-tag">S: ₹{product.selling_price.toFixed(2)}</span>
                  </td>
                  <td class="qty-text" class:low-stock={product.quantity_left <= 5}>
                    {product.quantity_left} units
                  </td>
                  <td class="actions-group">
                    <button type="button" class="btn-patch inc" onclick={() => handleStockChange(product.sku, 'increase-stock')}>+</button>
                    <button type="button" class="btn-patch dec" onclick={() => handleStockChange(product.sku, 'decrease-stock')}>-</button>
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
  .terminal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    flex-wrap: wrap;
    gap: 15px;
  }

  .page-view h2 {
    font-size: 24px;
    margin-bottom: 4px;
    color: var(--accent-primary);
  }

  .subtitle {
    color: var(--text-muted);
    font-size: 14px;
  }

  .terminal-badge {
    background: rgba(15, 90, 71, 0.1);
    color: var(--accent-primary);
    border: 1px solid rgba(15, 90, 71, 0.2);
    padding: 6px 16px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 700;
  }

  .inventory-layout-grid {
    display: grid;
    grid-template-columns: 360px 1fr;
    gap: 24px;
  }

  @media (max-width: 990px) {
    .inventory-layout-grid { grid-template-columns: 1fr; }
  }

  .panel-card {
    background: var(--bg-card);
    border: 1px solid var(--border-light);
    padding: 24px;
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-sm);
    display: flex;
    flex-direction: column;
    min-width: 0;
  }

  .panel-title {
    font-size: 14px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 20px;
    border-bottom: 1px solid var(--border-light);
    padding-bottom: 8px;
  }

  .valuation-bar {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
  }

  .val-card {
    background: var(--bg-card);
    border: 1px solid var(--border-light);
    padding: 16px 20px;
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-sm);
    display: flex;
    flex-direction: column;
  }

  .val-label {
    font-size: 11px;
    font-weight: 800;
    color: var(--text-muted);
    letter-spacing: 0.5px;
  }

  .val-num {
    font-size: 24px;
    font-weight: 800;
    color: var(--text-main);
    margin: 4px 0;
  }

  .val-num.text-emerald { color: #047857; }
  .val-num.text-mint { color: var(--accent-mint); }

  .val-sub {
    font-size: 12px;
    color: var(--text-muted);
  }

  .stacked-form, .price-matrix { display: flex; flex-direction: column; }
  .stacked-form { gap: 16px; }
  .field-row { gap: 16px; width: 100%; display: flex; flex-wrap: wrap; }
  .field-group { flex: 1; display: flex; flex-direction: column; }
  .field-group label { font-size: 13px; color: var(--text-muted); margin-bottom: 6px; font-weight: 600; }
  
  input {
    background: var(--bg-input);
    border: 1px solid var(--border-solid);
    padding: 10px 12px;
    color: var(--text-main);
    border-radius: 8px;
    font-size: 14px;
    width: 100%;
    box-sizing: border-box;
    transition: all 0.2s ease;
  }

  input:focus {
    outline: none;
    border-color: var(--accent-primary);
    box-shadow: 0 0 0 3px rgba(15, 90, 71, 0.12);
  }

  .btn-add-product {
    border: none;
    padding: 12px;
    font-weight: 700;
    font-size: 13px;
    text-transform: uppercase;
    background: var(--accent-primary);
    color: #ffffff;
    border-radius: 8px;
    cursor: pointer;
    box-shadow: 0 4px 12px rgba(15, 90, 71, 0.25);
    transition: transform 0.2s ease, background 0.2s ease;
  }

  .btn-add-product:hover {
    background: var(--accent-primary-hover);
    transform: translateY(-1px);
  }

  .table-frame { overflow-x: auto; width: 100%; }
  
  table {
    width: 100%;
    border-collapse: collapse;
    background: var(--bg-card);
    border-radius: var(--radius-sm);
    overflow: hidden;
  }

  th {
    background: var(--bg-card-hover);
    color: var(--text-muted);
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding: 12px;
    text-align: left;
    border-bottom: 1px solid var(--border-light);
  }

  .index-th { width: 30px; text-align: center; }
  td { padding: 12px; border-bottom: 1px solid var(--border-light); font-size: 14px; color: var(--text-main); vertical-align: middle; }
  
  .index-cell { text-align: center; color: var(--text-muted); font-family: monospace; font-weight: 700; }
  .sku-text { font-family: monospace; color: var(--accent-primary); font-weight: 700; }
  .price-matrix { gap: 2px; font-size: 12px; font-family: monospace; }
  .cost-tag { color: var(--accent-warning); }
  .sell-tag { color: #047857; font-weight: 700; }
  .qty-text.low-stock { color: var(--accent-danger); font-weight: 800; background: rgba(225, 29, 72, 0.1); padding: 2px 6px; border-radius: 4px; }
  
  .actions-group { gap: 6px; justify-content: flex-start; display: flex; align-items: center; }
  
  .btn-patch {
    border: 1px solid var(--border-solid);
    background: var(--bg-card-hover);
    color: var(--text-main);
    width: 28px;
    height: 28px;
    border-radius: 6px;
    font-weight: 700;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
  }

  .btn-patch.inc:hover { background: #047857; color: #ffffff; border-color: #047857; }
  .btn-patch.dec:hover { background: var(--accent-warning); color: #ffffff; border-color: var(--accent-warning); }

  .btn-remove {
    border: 1px solid rgba(225, 29, 72, 0.2);
    background: rgba(225, 29, 72, 0.08);
    color: var(--accent-danger);
    font-size: 12px;
    padding: 5px 10px;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 700;
    transition: all 0.2s ease;
  }

  .btn-remove:hover {
    background: var(--accent-danger);
    color: #ffffff;
  }

  .empty-box {
    text-align: center;
    color: var(--text-muted);
    font-size: 14px;
    padding: 40px 0;
    border: 2px dashed var(--border-light);
    border-radius: var(--radius-sm);
  }
</style>