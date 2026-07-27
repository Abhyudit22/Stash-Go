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
  import { Base_URL } from "./api";

  type ReportType = 'excel' | 'pdf';

  async function downloadReport(type: ReportType): Promise<void> {
    try {
      const response = await fetch(`${Base_URL}/reports/${type}`);
      
      if (!response.ok) {
        throw new Error(`Failed to generate ${type.toUpperCase()} report`);
      }

      const blob: Blob = await response.blob();
      const url: string = window.URL.createObjectURL(blob);
      const a: HTMLAnchorElement = document.createElement('a');
      a.href = url;
      a.download = `StashGO_Monthly_Report.${type === 'excel' ? 'xlsx' : 'pdf'}`;
      
      document.body.appendChild(a);
      a.click();
      
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
    } catch (error: any) {
      console.error("Download error:", error);
      alert("Could not download the report. Check server connection or sales data.");
    }
  }
</script>

<div class="page-view animate-fade-in">
  
  <!-- Header Title & Export Buttons -->
  <div class="header-container">
    <div>
      <h2 class="gradient-text-header">BUSINESS INTELLIGENCE DASHBOARD</h2>
      <p class="welcome-text">Real-time performance metrics computed securely from your store ledger.</p>
    </div>
    
    <div class="report-actions">
      <button class="btn-export excel" onclick={() => downloadReport('excel')}>
        <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="8" y1="13" x2="16" y2="13"></line><line x1="8" y1="17" x2="16" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
        Export Excel
      </button>

      <button class="btn-export pdf" onclick={() => downloadReport('pdf')}>
        <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><path d="M9 15v-6h4.5a2 2 0 1 1 0 4H9"></path></svg>
        Export PDF
      </button>
    </div>
  </div>
  
  {#if !analyticsData}
    <div class="loading-placeholder">Loading business performance matrices...</div>
  {:else}
    <!-- Reference Image Inspired Emerald Hero Card -->
    <div class="hero-emerald-card">
      <div class="hero-main-info">
        <span class="hero-label">Total Store Balance & Gross Revenue</span>
        <div class="hero-value-wrap">
          <span class="hero-value">₹{(analyticsData.total_revenue || 0).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
          <span class="hero-badge">
            <svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" stroke-width="2.5" fill="none"><line x1="7" y1="17" x2="17" y2="7"></line><polyline points="7 7 17 7 17 17"></polyline></svg>
            +18.4%
          </span>
        </div>
      </div>
      <div class="hero-actions">
        <div class="hero-stat-pill">
          <span class="hero-stat-lbl">Net Profit Yield</span>
          <span class="hero-stat-val">₹{(analyticsData.total_profit || 0).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
        </div>
        <div class="hero-stat-pill">
          <span class="hero-stat-lbl">Total Orders</span>
          <span class="hero-stat-val">{analyticsData.total_sales_count || 0}</span>
        </div>
      </div>
    </div>

    <!-- Metric Cards Grid -->
    <div class="metrics-grid">
      <div class="metric-card emerald-border">
        <div class="metric-icon-box emerald">
          <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none"><line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>
        </div>
        <div>
          <span class="card-label">Gross Revenue</span>
          <div class="card-value text-emerald">₹{(analyticsData.total_revenue || 0).toFixed(2)}</div>
        </div>
      </div>

      <div class="metric-card mint-border">
        <div class="metric-icon-box mint">
          <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>
        </div>
        <div>
          <span class="card-label">Net Profit Yield</span>
          <div class="card-value text-mint">₹{(analyticsData.total_profit || 0).toFixed(2)}</div>
        </div>
      </div>

      <div class="metric-card teal-border">
        <div class="metric-icon-box teal">
          <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none"><path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path><line x1="3" y1="6" x2="21" y2="6"></line><path d="M16 10a4 4 0 0 1-8 0"></path></svg>
        </div>
        <div>
          <span class="card-label">Completed Orders</span>
          <div class="card-value text-dark">{analyticsData.total_sales_count || 0} Orders</div>
        </div>
      </div>

      <div class="metric-card slate-border">
        <div class="metric-icon-box slate">
          <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path></svg>
        </div>
        <div>
          <span class="card-label">Unique Products</span>
          <div class="card-value text-dark">{analyticsData.total_products || 0} SKUs</div>
        </div>
      </div>
    </div>

    <!-- Split Data Layout -->
    <div class="dashboard-split-layout">
      
      <!-- Top Selling Products -->
      <div class="data-panel">
        <div class="panel-header-title text-emerald">
          <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>
          Top Selling Products
        </div>
        {#if !analyticsData.top_selling_products || analyticsData.top_selling_products.length === 0}
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
                <span class="item-revenue">₹{(item.total_revenue || 0).toFixed(2)}</span>
              </div>
            {/each}
          </div>
        {/if}
      </div>

      <!-- Critical Low Stock Warnings -->
      <div class="data-panel">
        <div class="panel-header-title text-red">
          <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
          Low Stock Warnings
        </div>
        {#if !analyticsData.low_stock_products || analyticsData.low_stock_products.length === 0}
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

    <!-- Recent Activity Stream -->
    <div class="data-panel full-width-panel margin-top-md">
      <div class="panel-header-title text-emerald">
        <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
        Recent Transactions Activity Stream
      </div>
      
      {#if !analyticsData.recent_sales || analyticsData.recent_sales.length === 0}
        <p class="no-data-msg">No recent customer sales orders detected in this session cycle.</p>
      {:else}
        <div class="table-frame">
          <table class="ledger-table">
            <thead>
              <tr>
                <th>Order ID</th>
                <th>Product Identifier</th>
                <th>Qty Demanded</th>
                <th>Gross Total Amount</th>
                <th>Execution Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {#each analyticsData.recent_sales as sale}
                <tr class="ledger-row">
                  <td class="text-monospace text-emerald">#TXN-{sale.sale_id}</td>
                  <td class="font-bold text-dark">{sale.product_name}</td>
                  <td>{sale.quantity} units</td>
                  <td class="text-mint font-bold">₹{(sale.total_amount || 0).toFixed(2)}</td>
                  <td class="text-muted text-xs">{new Date(sale.sale_date).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      {/if}
    </div>
  {/if}

  <div class="footer-diagnostics-bar">
    <span>API Node Connection: <strong class={backendStatus === 'ok' ? 'text-mint' : 'text-red'}>{backendStatus.toUpperCase()}</strong></span>
  </div>
</div>

<style>
  .header-container {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 24px;
    flex-wrap: wrap;
    gap: 15px;
  }

  .page-view h2 {
    font-size: 24px;
    margin-bottom: 4px;
    color: var(--accent-primary);
  }

  .welcome-text {
    color: var(--text-muted);
    font-size: 14px;
  }
  
  .report-actions {
    display: flex;
    gap: 12px;
  }

  .btn-export {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 18px;
    border: none;
    border-radius: 20px;
    font-weight: 700;
    font-size: 13px;
    cursor: pointer;
    color: white;
    transition: all 0.2s ease;
  }

  .btn-export.excel {
    background: #107c41;
    box-shadow: 0 2px 8px rgba(16, 124, 65, 0.25);
  }

  .btn-export.excel:hover {
    background: #0b5c30;
    transform: translateY(-2px);
  }

  .btn-export.pdf {
    background: #e11d48;
    box-shadow: 0 2px 8px rgba(225, 29, 72, 0.25);
  }

  .btn-export.pdf:hover {
    background: #be123c;
    transform: translateY(-2px);
  }
  
  .loading-placeholder {
    text-align: center;
    padding: 100px 0;
    color: var(--text-muted);
    font-size: 15px;
  }

  /* Reference Banner Card */
  .hero-emerald-card {
    background: linear-gradient(135deg, #0b4536 0%, #0f5a47 60%, #136a54 100%);
    border-radius: var(--radius-lg);
    padding: 30px;
    color: #ffffff;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    box-shadow: 0 10px 25px rgba(15, 90, 71, 0.25);
    flex-wrap: wrap;
    gap: 20px;
  }

  .hero-label {
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: rgba(255, 255, 255, 0.75);
    font-weight: 700;
  }

  .hero-value-wrap {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-top: 6px;
  }

  .hero-value {
    font-size: 38px;
    font-weight: 800;
    letter-spacing: -1px;
  }

  .hero-badge {
    background: rgba(16, 185, 129, 0.25);
    color: #34d399;
    border: 1px solid rgba(16, 185, 129, 0.4);
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 4px;
  }

  .hero-actions {
    display: flex;
    gap: 16px;
  }

  .hero-stat-pill {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.15);
    padding: 12px 20px;
    border-radius: var(--radius-md);
    display: flex;
    flex-direction: column;
  }

  .hero-stat-lbl {
    font-size: 11px;
    color: rgba(255, 255, 255, 0.7);
    font-weight: 600;
  }

  .hero-stat-val {
    font-size: 18px;
    font-weight: 800;
    color: #ffffff;
    margin-top: 2px;
  }

  /* Metric Cards Grid */
  .metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 20px;
    margin-bottom: 24px;
  }

  .metric-card {
    background: var(--bg-card);
    padding: 20px;
    border-radius: var(--radius-md);
    border: 1px solid var(--border-light);
    box-shadow: var(--shadow-sm);
    display: flex;
    align-items: center;
    gap: 16px;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
  }

  .metric-card:hover {
    transform: translateY(-3px);
    box-shadow: var(--shadow-md);
  }

  .metric-icon-box {
    width: 44px;
    height: 44px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .metric-icon-box.emerald { background: rgba(15, 90, 71, 0.1); color: var(--accent-primary); }
  .metric-icon-box.mint { background: rgba(16, 185, 129, 0.1); color: var(--accent-mint); }
  .metric-icon-box.teal { background: rgba(13, 148, 136, 0.1); color: var(--accent-secondary); }
  .metric-icon-box.slate { background: rgba(100, 116, 139, 0.1); color: var(--text-muted); }

  .card-label {
    font-size: 12px;
    color: var(--text-muted);
    font-weight: 600;
  }

  .card-value {
    font-size: 22px;
    font-weight: 800;
    margin-top: 2px;
  }

  .text-emerald { color: var(--accent-primary); }
  .text-mint { color: #047857; }
  .text-dark { color: var(--text-main); }

  /* Split Layout */
  .dashboard-split-layout {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
  }

  @media (max-width: 850px) {
    .dashboard-split-layout { grid-template-columns: 1fr; }
  }
  
  .data-panel {
    background: var(--bg-card);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-md);
    padding: 24px;
    box-shadow: var(--shadow-sm);
    box-sizing: border-box;
  }

  .panel-header-title {
    font-size: 14px;
    font-weight: 800;
    color: var(--accent-primary);
    margin-bottom: 18px;
    border-bottom: 1px solid var(--border-light);
    padding-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  
  .ranking-list, .warning-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
    max-height: 380px;
    overflow-y: auto;
  }
  
  .ranking-row, .warning-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: var(--bg-card-hover);
    padding: 12px 16px;
    border-radius: var(--radius-sm);
    border: 1px solid var(--border-light);
  }

  .rank-badge {
    background: rgba(16, 185, 129, 0.15);
    color: var(--accent-primary);
    font-weight: 800;
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 8px;
    font-size: 13px;
    margin-right: 12px;
  }

  .item-details { flex: 1; display: flex; flex-direction: column; }
  .item-name { font-weight: 700; color: var(--text-main); font-size: 14px; }
  .item-sub { font-size: 12px; color: var(--text-muted); margin-top: 2px; }
  .item-revenue { color: var(--accent-primary); font-weight: 800; font-family: monospace; font-size: 15px; }

  .warning-row {
    border-left: 4px solid var(--accent-danger);
    background: rgba(244, 63, 94, 0.08);
  }

  .warn-name { font-weight: 700; color: var(--text-main); display: block; font-size: 14px; }
  .warn-sku { font-family: monospace; font-size: 12px; color: var(--accent-danger); margin-top: 2px; display: block; }
  .warn-pill { background: rgba(244, 63, 94, 0.15); color: var(--accent-danger); font-weight: 700; padding: 4px 10px; border-radius: 6px; font-size: 12px; }
  
  .clean-state-box {
    border: 2px dashed rgba(16, 185, 129, 0.3);
    color: var(--accent-primary);
    text-align: center;
    padding: 30px;
    border-radius: var(--radius-sm);
    font-size: 14px;
    background: rgba(16, 185, 129, 0.08);
  }

  .no-data-msg { color: var(--text-muted); text-align: center; font-size: 13px; padding: 20px 0; }

  .full-width-panel { grid-column: 1 / -1; }
  .margin-top-md { margin-top: 24px; margin-bottom: 24px; }
  .table-frame { width: 100%; overflow-x: auto; }
  .ledger-table { width: 100%; border-collapse: collapse; text-align: left; }
  
  .ledger-table th {
    background: var(--bg-card-hover);
    color: var(--text-muted);
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    padding: 12px 16px;
    border-bottom: 1px solid var(--border-light);
  }

  .ledger-row td {
    padding: 12px 16px;
    border-bottom: 1px solid var(--border-light);
    font-size: 13px;
    color: var(--text-main);
  }

  .ledger-row:hover { background: var(--bg-card-hover); }

  .footer-diagnostics-bar {
    border-top: 1px solid var(--border-light);
    padding-top: 15px;
    text-align: right;
    font-size: 12px;
    color: var(--text-muted);
  }

  .text-monospace { font-family: monospace; font-weight: 700; }
  .font-bold { font-weight: 700; }
  .text-xs { font-size: 11px; }
  .text-red { color: var(--accent-danger); }
</style>