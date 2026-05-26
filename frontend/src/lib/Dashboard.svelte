<script lang="ts">
  export let backendStatus: string;
  export let analyticsData: {
    total_products: number;
    total_sales_count: number;
    total_revenue: number;
    total_profit: number;
    low_stock_products: Array<{ id: number; name: string; sku: string; quantity_left: number }>;
    top_selling_products: Array<{ product_id: string; product_name: string; total_quantity_sold: number; total_revenue: number }>;
    recent_sales: Array<{ sale_id: number; product_name: string; quantity: number; total_amount: number; sale_date: string }>;
  } | null = null;
</script>

<div class="page-view animate-fade-in">
  <h2>BUSINESS INTELLIGENCE DASHBOARD</h2>
  <p class="welcome-text">Real-time performance metrics computed securely from your database cluster.</p>
  
  {#if !analyticsData}
    <div class="loading-placeholder">Loading business performance matrices...</div>
  {:else}
    <div class="metrics-grid">
      <div class="metric-card cyan-border">
        <span class="card-label">Gross Revenue</span>
        <div class="card-value text-green">₹{analyticsData.total_revenue.toFixed(2)}</div>
      </div>
      <div class="metric-card green-border">
        <span class="card-label">Net Profit Yield</span>
        <div class="card-value text-cyan">₹{analyticsData.total_profit.toFixed(2)}</div>
      </div>
      <div class="metric-card purple-border">
        <span class="card-label">Settle Transactions</span>
        <div class="card-value">{analyticsData.total_sales_count} Orders</div>
      </div>
      <div class="metric-card grey-border">
        <span class="card-label">Unique Stock Line Items</span>
        <div class="card-value">{analyticsData.total_products} SKUs</div>
      </div>
    </div>

    <div class="dashboard-split-layout">
      
      <div class="data-panel">
        <div class="panel-header-title">Top Selling Inventory Items</div>
        {#if analyticsData.top_selling_products.length === 0}
          <p class="no-data-msg">No sales items logged yet.</p>
        {:else}
          <div class="ranking-list">
            {#each analyticsData.top_selling_products as item, index}
              <div class="ranking-row">
                <span class="rank-badge">#{index + 1}</span>
                <div class="item-details">
                  <span class="item-name">{item.product_name}</span>
                  <span class="item-sub">{item.total_quantity_sold} units moved</span>
                </div>
                <span class="item-revenue">₹{item.total_revenue.toFixed(2)}</span>
              </div>
            {/each}
          </div>
        {/if}
      </div>

      <div class="data-panel">
        <div class="panel-header-title text-red">Critical Low Stock Warnings</div>
        {#if analyticsData.low_stock_products.length === 0}
          <div class="clean-state-box">✓ All inventory product levels are stable and healthy.</div>
        {:else}
          <div class="warning-list">
            {#each analyticsData.low_stock_products as product}
              <div class="warning-row">
                <div>
                  <span class="warn-name">{product.name}</span>
                  <span class="warn-sku">{product.sku}</span>
                </div>
                <span class="warn-pill">Only {product.quantity_left} left</span>
              </div>
            {/each}
          </div>
        {/if}
      </div>

    </div>
  {/if}

  <div class="footer-diagnostics-bar">
    <span>API Node Connection: <strong class={backendStatus === 'ok' ? 'text-green' : 'text-red'}>{backendStatus.toUpperCase()}</strong></span>
  </div>
</div>

<style>
  .page-view h2 { color: #ffffff; font-size: 24px; margin-bottom: 6px;  padding-left: 12px;}
  .welcome-text { color: #8e8e9a; font-size: 14px; margin-bottom: 35px; }
  
  .loading-placeholder { text-align: center; padding: 100px 0; color: #7c7c8a; font-size: 15px; }

  /* Top Metric Row Blocks */
  .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin-bottom: 35px; }
  .metric-card { background: #1e1e24; padding: 24px; border-radius: 6px; border: 1px solid #29292e; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
  .cyan-border { border-left: 4px solid #00bcd4; }
  .green-border { border-left: 4px solid #4caf50; }
  .purple-border { border-left: 4px solid #9c27b0; }
  .grey-border { border-left: 4px solid #7c7c8a; }
  .card-label { font-size: 11px; text-transform: uppercase; color: #8e8e9a; letter-spacing: 0.6px; font-weight: bold; }
  .card-value { font-size: 26px; font-weight: bold; margin-top: 8px; font-family: system-ui, sans-serif; }

  /* Split Layout Tables */
  .dashboard-split-layout { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-bottom: 35px; }
  @media (max-width: 850px) { .dashboard-split-layout { grid-template-columns: 1fr; } }
  
  .data-panel { background: #1e1e24; border: 1px solid #29292e; border-radius: 8px; padding: 25px; box-sizing: border-box; }
  .panel-header-title { font-size: 14px; font-weight: bold; text-transform: uppercase; color: #00bcd4; letter-spacing: 0.8px; margin-bottom: 20px; border-bottom: 1px solid #29292e; padding-bottom: 10px; }
  
  /* Ranking Items list */
  .ranking-list, .warning-list { display: flex; flex-direction: column; gap: 12px; }
  .ranking-row, .warning-row { display: flex; align-items: center; justify-content: space-between; background: #252530; padding: 12px 16px; border-radius: 6px; border: 1px solid #2e2e3a; }
  .rank-badge { background: rgba(0, 188, 212, 0.15); color: #00bcd4; font-weight: bold; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; border-radius: 4px; font-size: 13px; margin-right: 12px; }
  .item-details { flex: 1; display: flex; flex-direction: column; }
  .item-name { font-weight: bold; color: white; font-size: 14px; }
  .item-sub { font-size: 12px; color: #8e8e9a; margin-top: 2px; }
  .item-revenue { color: #4caf50; font-weight: bold; font-family: monospace; font-size: 15px; }

  /* Warnings box */
  .warning-row { border-left: 4px solid #ff5252; background: #251e22; border-color: #ff5252; }
  .warn-name { font-weight: bold; color: white; display: block; font-size: 14px; }
  .warn-sku { font-family: monospace; font-size: 12px; color: #ff5252; margin-top: 2px; display: block; }
  .warn-pill { background: rgba(255, 82, 82, 0.15); color: #ff5252; font-weight: bold; padding: 4px 10px; border-radius: 4px; font-size: 12px; }
  .clean-state-box { border: 2px dashed #29292e; color: #4caf50; text-align: center; padding: 30px; border-radius: 6px; font-size: 14px; background: rgba(76, 175, 80, 0.02); }
  .no-data-msg { color: #7c7c8a; text-align: center; font-size: 13px; padding: 20px 0; }

  .footer-diagnostics-bar { border-top: 1px solid #29292e; padding-top: 15px; text-align: right; font-size: 12px; color: #7c7c8a; }
  .text-green { color: #4caf50; }
  .text-cyan { color: #00bcd4; }
  .text-red { color: #ff5252; }

  .animate-fade-in { animation: fadeIn 0.3s ease-out forwards; }
  @keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }
</style>