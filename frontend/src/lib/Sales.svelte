<script lang="ts">
  export let salesHistory: any[] = [];
  export let handleDeleteSale: (billId: number) => Promise<void> = async () => {};

  type TimeFilter = 'day' | 'week' | 'month' | 'year';
  let activeFilter: TimeFilter = 'day';
  let expandedBillId: number | null = null;

  function aggregateSalesData(records: any[]) {
    if (!records || records.length === 0) return [];
    const billMap = new Map();

    for (const item of records) {
      const bId = item.bill_id || item.bill?.id || item.id || 0;
      if (!bId) continue;

      if (!billMap.has(bId)) {
        billMap.set(bId, {
          id: bId,
          bill_number: item.bill?.bill_number || item.bill_number || `BILL-${bId}`,
          customer_name: item.bill?.customer_name || item.customer_name || item.customer_info || "Walk-in",
          customer_phone: item.bill?.customer_phone || item.customer_phone || "N/A",
          payment_method: item.bill?.payment_method || item.payment_method || "Cash",
          subtotal: 0,
          discount: item.bill?.discount || item.discount || 0,
          tax: item.bill?.tax || item.tax || 0,
          created_at: item.bill?.created_at || item.created_at || new Date().toISOString(),
          total_profit: 0,
          items: []
        });
      }

      const currentBill = billMap.get(bId);
      const unitPrice = item.price || item.selling_price || item.product?.selling_price || 0;
      const costPrice = item.cost_price || item.product?.cost_price || (unitPrice * 0.8); 
      const qty = item.quantity || item.quantity_sold || 1;

      const netRev = unitPrice * qty;
      const netProf = (unitPrice - costPrice) * qty;

      currentBill.subtotal += netRev;
      currentBill.total_profit += netProf;

      currentBill.items.push({
        product_name: item.product_name || item.product?.name || `Item Ref #${item.product_id || '?'}`,
        sku: item.sku || item.product?.sku || "N/A", 
        quantity: qty, 
        unit_price: unitPrice, 
        net_revenue: netRev, 
        net_profit: netProf
      });
    }

    return Array.from(billMap.values()).map(bill => {
      bill.total_bill_amount = Math.max(0, bill.subtotal - bill.discount + bill.tax);
      return bill;
    }).sort((a, b) => b.id - a.id); 
  }

  function formatDateTime(dateStr: string): string {
    if (!dateStr) return "N/A";
    try {
      const date = new Date(dateStr);
      return date.toLocaleString('en-IN', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: true,
        timeZone: 'Asia/Kolkata'
      });
    } catch {
      return "Invalid Date";
    }
  }

  $: groupedBills = aggregateSalesData(salesHistory);

  function computeLiveChartData(bills: any[]) {
    const data = {
      day: [
        { label: '12AM-3AM', revenue: 0, profit: 0 }, { label: '3AM-6AM', revenue: 0, profit: 0 }, 
        { label: '6AM-9AM', revenue: 0, profit: 0 }, { label: '9AM-12PM', revenue: 0, profit: 0 }, 
        { label: '12PM-3PM', revenue: 0, profit: 0 }, { label: '3PM-6PM', revenue: 0, profit: 0 },
        { label: '6PM-9PM', revenue: 0, profit: 0 }, { label: '9PM-12AM', revenue: 0, profit: 0 }
      ],
      week: [
        { label: 'Sun', revenue: 0, profit: 0 }, { label: 'Mon', revenue: 0, profit: 0 }, { label: 'Tue', revenue: 0, profit: 0 }, 
        { label: 'Wed', revenue: 0, profit: 0 }, { label: 'Thu', revenue: 0, profit: 0 }, { label: 'Fri', revenue: 0, profit: 0 }, { label: 'Sat', revenue: 0, profit: 0 }
      ],
      month: [
        { label: 'Week 1', revenue: 0, profit: 0 }, { label: 'Week 2', revenue: 0, profit: 0 }, 
        { label: 'Week 3', revenue: 0, profit: 0 }, { label: 'Week 4+', revenue: 0, profit: 0 }
      ],
      year: [
        { label: 'Q1', revenue: 0, profit: 0 }, { label: 'Q2', revenue: 0, profit: 0 }, 
        { label: 'Q3', revenue: 0, profit: 0 }, { label: 'Q4', revenue: 0, profit: 0 }
      ]
    };

    if (!bills || bills.length === 0) return data;
    const now = new Date();

    bills.forEach(bill => {
      const recordDate = new Date(bill.created_at);
      const rev = bill.total_bill_amount;
      const prof = bill.total_profit;

      if (recordDate.toDateString() === now.toDateString()) {
        const bucketIndex = Math.floor(recordDate.getHours() / 3);
        data.day[bucketIndex].revenue += rev;
        data.day[bucketIndex].profit += prof;
      }

      const daysDiff = (now.getTime() - recordDate.getTime()) / (1000 * 3600 * 24);
      if (daysDiff <= 7) {
        data.week[recordDate.getDay()].revenue += rev;
        data.week[recordDate.getDay()].profit += prof;
      }

      if (recordDate.getMonth() === now.getMonth() && recordDate.getFullYear() === now.getFullYear()) {
        const date = recordDate.getDate();
        if (date <= 7) { data.month[0].revenue += rev; data.month[0].profit += prof; }
        else if (date <= 14) { data.month[1].revenue += rev; data.month[1].profit += prof; }
        else if (date <= 21) { data.month[2].revenue += rev; data.month[2].profit += prof; }
        else { data.month[3].revenue += rev; data.month[3].profit += prof; }
      }

      if (recordDate.getFullYear() === now.getFullYear()) {
        const month = recordDate.getMonth();
        if (month < 3) { data.year[0].revenue += rev; data.year[0].profit += prof; }
        else if (month < 6) { data.year[1].revenue += rev; data.year[1].profit += prof; }
        else if (month < 9) { data.year[2].revenue += rev; data.year[2].profit += prof; }
        else { data.year[3].revenue += rev; data.year[3].profit += prof; }
      }
    });

    return data;
  }

  $: chartDataMap = computeLiveChartData(groupedBills);
  $: activeData = chartDataMap[activeFilter as keyof typeof chartDataMap];
  
  $: maxRevenue = Math.max(...activeData.map((d: any) => d.revenue)) || 1; 
  $: maxProfit = Math.max(...activeData.map((d: any) => d.profit)) || 1; 
  
  $: totalPeriodSales = activeData.reduce((sum: number, d: any) => sum + d.revenue, 0);
  $: totalProfit = groupedBills.reduce((sum, b) => sum + b.total_profit, 0);
  
  $: upiCount = groupedBills.filter(b => b.payment_method.toUpperCase() === 'UPI').length;
  $: cashCount = groupedBills.filter(b => b.payment_method.toUpperCase() === 'CASH').length;

  function setFilter(filter: TimeFilter) { activeFilter = filter; }
  function toggleRow(billId: number) { expandedBillId = expandedBillId === billId ? null : billId; }

  $: revLinePoints = activeData.map((d: any, i: number) => {
    const step = 800 / activeData.length;
    const x = (i * step) + (step / 2);
    const y = 200 - (d.revenue / maxRevenue) * 180;
    return `${x},${y}`;
  }).join(" ");

  $: profLinePoints = activeData.map((d: any, i: number) => {
    const step = 800 / activeData.length;
    const x = (i * step) + (step / 2);
    const y = 200 - (d.profit / maxProfit) * 180;
    return `${x},${y}`;
  }).join(" ");
</script>

<div class="page-view animate-fade-in">
  <div class="header-flex">
    <div class="header-text">
      <h2 class="gradient-text-header">SALES LEDGER & ANALYTICS</h2>
      <p class="subtitle">Real-time transaction history with revenue and profit metrics.</p>
    </div>
    <div class="filter-tabs">
      <button class:active={activeFilter === 'day'} on:click={() => setFilter('day')}>DAY</button>
      <button class:active={activeFilter === 'week'} on:click={() => setFilter('week')}>WEEK</button>
      <button class:active={activeFilter === 'month'} on:click={() => setFilter('month')}>MONTH</button>
      <button class:active={activeFilter === 'year'} on:click={() => setFilter('year')}>YEAR</button>
    </div>
  </div>

  {#if groupedBills.length === 0}
    <div class="empty-box">
      <p>No sales records found. Create a bill and finalize it to see transaction data.</p>
    </div>
  {:else}
    <div class="analytics-viz-grid">
      <div class="metric-viz-card">
        <svg class="chart-svg" viewBox="0 0 800 220" xmlns="http://www.w3.org/2000/svg">
          <line x1="0" y1="200" x2="800" y2="200" stroke="rgba(255,255,255,0.1)" stroke-width="1" />
          <line x1="0" y1="100" x2="800" y2="100" stroke="rgba(255,255,255,0.05)" stroke-width="1" />
          <polyline points={revLinePoints} fill="none" stroke="var(--accent-cyan)" stroke-width="3" />
          <polyline points={profLinePoints} fill="none" stroke="var(--accent-success)" stroke-width="3" />
          
          {#each activeData as point, idx}
            <circle
              cx={(idx * (800 / activeData.length)) + (800 / (2 * activeData.length))}
              cy={200 - (point.revenue / maxRevenue) * 180}
              r="4"
              fill="var(--accent-cyan)"
              stroke="#ffffff"
              stroke-width="2"
              class="svg-dot"
            />
          {/each}
          
          {#each activeData as point, idx}
            <circle
              cx={(idx * (800 / activeData.length)) + (800 / (2 * activeData.length))}
              cy={200 - (point.profit / maxProfit) * 180}
              r="4"
              fill="var(--accent-success)"
              stroke="#ffffff"
              stroke-width="2"
              class="svg-dot"
            />
          {/each}
        </svg>

        <div class="axis-labels">
          {#each activeData as point}
            <span>{point.label}</span>
          {/each}
        </div>
      </div>

      <div class="mini-widgets-col">
        <div class="metric-viz-card mini-card cyan-border">
          <div class="viz-label">Total Period Sales</div>
          <h3>₹{totalPeriodSales.toFixed(2)}</h3>
        </div>

        <div class="metric-viz-card mini-card green-border">
          <div class="viz-label">Net Profit</div>
          <h3>₹{totalProfit.toFixed(2)}</h3>
        </div>

        <div class="metric-viz-card mini-card indigo-border">
          <div class="viz-label">Payment Breakdown</div>
          <div class="payment-ratio-bar">
            {#if upiCount > 0 || cashCount > 0}
              <div class="segment upi" style="width: {(upiCount / (upiCount + cashCount)) * 100}%"></div>
              <div class="segment cash" style="width: {(cashCount / (upiCount + cashCount)) * 100}%"></div>
            {/if}
          </div>
          <div class="ratio-legends">
            <div class="dot-legend upi-dot">UPI: {upiCount} txns</div>
            <div class="dot-legend cash-dot">Cash: {cashCount} txns</div>
          </div>
        </div>
      </div>
    </div>

    {#if groupedBills.length > 0}
      <div class="panel-card">
        <div class="panel-title text-cyan">Transaction History Ledger</div>
        <div class="table-frame">
          <table>
            <thead>
              <tr>
                <th>Invoice ID</th>
                <th>Customer</th>
                <th>Date & Time</th>
                <th>Items</th>
                <th>Subtotal</th>
                <th>Discount</th>
                <th>Total</th>
                <th>Profit</th>
                <th>Status / Actions</th>
              </tr>
            </thead>
            <tbody>
              {#each groupedBills as bill}
                <tr class="clickable-row" class:active-row={expandedBillId === bill.id} on:click={() => toggleRow(bill.id)}>
                  <td><span class="invoice-number-text text-cyan">{bill.bill_number}</span></td>
                  <td>
                    <div class="cust-title text-white">{bill.customer_name}</div>
                    <div class="cust-subtitle">{bill.customer_phone}</div>
                  </td>
                  <td>{formatDateTime(bill.created_at)}</td>
                  <td class="text-center">{bill.items.length}</td>
                  <td class="text-right">₹{bill.subtotal.toFixed(2)}</td>
                  <td class="text-right text-amber">₹{bill.discount.toFixed(2)}</td>
                  <td class="text-right text-bold text-white">₹{bill.total_bill_amount.toFixed(2)}</td>
                  <td class="text-right text-green font-bold">₹{bill.total_profit.toFixed(2)}</td>
                  <td>
                    <div style="display: flex; gap: 8px; align-items: center;">
                      <span class="badge-status-finalized">FINALIZED</span>
                      <button class="btn-delete-row" on:click|stopPropagation={() => handleDeleteSale(bill.id)}>
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
                {#if expandedBillId === bill.id}
                  <tr class="nested-expansion-wrapper">
                    <td colspan="9">
                      <div class="expanded-details-drawer animate-slide-down">
                        <h4>Bill Breakdown Details</h4>
                        <table class="inner-details-table">
                          <thead>
                            <tr>
                              <th>Item Name</th>
                              <th>SKU</th>
                              <th class="text-center">Qty</th>
                              <th class="text-right">Rate</th>
                              <th class="text-right">Total</th>
                            </tr>
                          </thead>
                          <tbody>
                            {#if !bill.items || bill.items.length === 0}
                              <tr><td colspan="5" class="text-muted">No line items found.</td></tr>
                            {:else}
                              {#each bill.items as item}
                                <tr>
                                  <td class="text-white font-medium">{item.product_name}</td>
                                  <td class="sku-sub-text">{item.sku}</td>
                                  <td class="text-center">{item.quantity}</td>
                                  <td class="text-right">₹{item.unit_price.toFixed(2)}</td>
                                  <td class="text-right text-white">₹{item.net_revenue.toFixed(2)}</td>
                                </tr>
                              {/each}
                            {/if}
                          </tbody>
                        </table>
                        <div class="expanded-summary-footer">
                          <div class="summary-line"><span>Subtotal:</span> <span>₹{bill.subtotal.toFixed(2)}</span></div>
                          {#if bill.discount > 0}<div class="summary-line text-amber"><span>Discount:</span> <span>- ₹{bill.discount.toFixed(2)}</span></div>{/if}
                          {#if bill.tax > 0}<div class="summary-line text-cyan"><span>Tax:</span> <span>+ ₹{bill.tax.toFixed(2)}</span></div>{/if}
                        </div>
                      </div>
                    </td>
                  </tr>
                {/if}
              {/each}
            </tbody>
          </table>
        </div>
      </div>
    {/if}
  {/if}
</div>

<style>
  .page-view { color: var(--text-main); }
  .header-flex { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; flex-wrap: wrap; gap: 15px; }
  .header-text h2 { font-size: 24px; margin: 0 0 4px 0; color: var(--accent-primary); }
  .subtitle { font-size: 14px; color: var(--text-muted); margin: 0; }

  .filter-tabs {
    display: flex;
    background: #e2e8f0;
    border-radius: 20px;
    padding: 4px;
    border: 1px solid var(--border-light);
  }

  .filter-tabs button {
    background: transparent;
    border: none;
    color: var(--text-muted);
    padding: 6px 16px;
    font-size: 13px;
    font-weight: 700;
    cursor: pointer;
    border-radius: 16px;
    transition: all 0.2s ease;
  }

  .filter-tabs button:hover { color: var(--accent-primary); }
  .filter-tabs button.active {
    background: var(--accent-primary);
    color: #ffffff;
    box-shadow: 0 2px 8px rgba(15, 90, 71, 0.25);
  }

  .analytics-viz-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 24px; margin-bottom: 24px; }

  @media (max-width: 900px) {
    .analytics-viz-grid { grid-template-columns: 1fr; }
  }

  .mini-widgets-col { display: flex; flex-direction: column; gap: 16px; }
  
  .metric-viz-card {
    background: var(--bg-card);
    border: 1px solid var(--border-light);
    padding: 20px;
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-sm);
  }

  .cyan-border { border-left: 4px solid var(--accent-secondary); }
  .green-border { border-left: 4px solid #047857; }
  .indigo-border { border-left: 4px solid var(--accent-primary); }

  .mini-card { flex: 1; display: flex; flex-direction: column; justify-content: center; }
  .metric-viz-card h3 { margin: 6px 0 0 0; font-size: 24px; color: var(--text-main); font-weight: 800; }
  .viz-label { font-size: 11px; color: var(--text-muted); text-transform: uppercase; font-weight: 700; letter-spacing: 0.8px; }

  .chart-svg { width: 100%; height: 100%; overflow: visible; }
  .svg-dot { transition: all 0.2s; cursor: pointer; }
  .svg-dot:hover { r: 7; fill: var(--accent-primary); }

  .axis-labels { display: flex; justify-content: space-around; width: 100%; font-size: 11px; color: var(--text-muted); font-weight: 600; padding: 0 10px; }
  
  .payment-ratio-bar { height: 8px; border-radius: 4px; display: flex; overflow: hidden; margin-top: 12px; background: var(--bg-card-hover); }
  .segment.upi { background: var(--accent-secondary); }
  .segment.cash { background: var(--accent-warning); }
  .ratio-legends { display: flex; gap: 16px; margin-top: 10px; }
  .dot-legend { font-size: 12px; color: var(--text-muted); display: flex; align-items: center; gap: 6px; }
  .dot-legend::before { content: ''; width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
  .upi-dot::before { background: var(--accent-secondary); }
  .cash-dot::before { background: var(--accent-warning); }

  .panel-card { min-width: 0;
    background: var(--bg-card);
    border: 1px solid var(--border-light);
    padding: 24px;
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-sm);
  }

  .panel-title { font-size: 14px; font-weight: 800; text-transform: uppercase; margin-bottom: 20px; letter-spacing: 0.8px; color: var(--accent-primary); }
  .table-frame { overflow-x: auto; width: 100%; }
  
  table { width: 100%; border-collapse: separate; border-spacing: 0; }
  th { background: var(--bg-card-hover); color: var(--text-muted); font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; padding: 12px 16px; text-align: left; font-weight: 700; border-bottom: 1px solid var(--border-light); }
  td { padding: 14px 16px; border-bottom: 1px solid var(--border-light); font-size: 14px; color: var(--text-main); vertical-align: middle; }
  
  .clickable-row { cursor: pointer; transition: background 0.2s ease; }
  .clickable-row:hover { background: var(--bg-card-hover); }
  .active-row { background: rgba(15, 90, 71, 0.05); }
  
  .invoice-number-text { font-family: monospace; font-weight: 700; color: var(--accent-primary); }
  .cust-title { font-weight: 600; color: var(--text-main); }
  .cust-subtitle { font-size: 12px; color: var(--text-muted); margin-top: 2px; }
  
  .badge-status-finalized {
    background: rgba(16, 185, 129, 0.12);
    color: #047857;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 700;
    border: 1px solid rgba(16, 185, 129, 0.25);
  }
  
  .btn-delete-row {
    background: rgba(225, 29, 72, 0.08);
    border: 1px solid rgba(225, 29, 72, 0.2);
    color: var(--accent-danger);
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-delete-row:hover { background: var(--accent-danger); color: #ffffff; }

  .nested-expansion-wrapper td { padding: 0 !important; border-bottom: none; }
  .expanded-details-drawer { padding: 20px; background: var(--bg-card-hover); border-radius: 0 0 10px 10px; border-top: 1px solid var(--border-light); }
  .expanded-details-drawer h4 { margin: 0 0 14px 0; font-size: 13px; font-weight: 700; color: var(--accent-primary); }
  
  .inner-details-table th { background: transparent; color: var(--text-muted); border-bottom: 1px solid var(--border-light); padding: 8px 0; }
  .inner-details-table td { padding: 10px 0; border-bottom: 1px dashed var(--border-light); font-size: 13px; color: var(--text-main); }
  
  .font-medium { font-weight: 600; }
  .sku-sub-text { font-family: monospace; color: var(--text-muted); font-size: 12px; }
  .expanded-summary-footer { display: flex; flex-direction: column; align-items: flex-end; gap: 6px; margin-top: 14px; padding-top: 14px; border-top: 1px solid var(--border-light); }
  .summary-line { display: flex; justify-content: space-between; width: 250px; font-size: 13px; color: var(--text-muted); }
  .summary-line span:last-child { font-weight: 700; font-family: monospace; color: var(--text-main); }

  .text-center { text-align: center; }
  .text-right { text-align: right; }
  .text-bold { font-weight: 700; }
  .text-green { color: #047857; }
  .text-cyan { color: var(--accent-secondary); }
  .text-amber { color: var(--accent-warning); }
  .text-white { color: var(--text-main); }
  .text-muted { color: var(--text-muted); }
  
  .empty-box { text-align: center; color: var(--text-muted); padding: 40px; border: 1px dashed var(--border-light); border-radius: var(--radius-sm); }
</style>
