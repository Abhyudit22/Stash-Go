<script lang="ts">
  export let salesHistory: any[] = [];
  export let handleDeleteSale: (billId: number) => Promise<void> = async () => {};

  type TimeFilter = 'day' | 'week' | 'month' | 'year';
  let activeFilter: TimeFilter = 'day';
  let expandedBillId: number | null = null;
  let hoveredData: any = null; 

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
      <h2>Sales Overview</h2>
      <p class="subtitle">Analyze revenue trends and audit invoice records.</p>
    </div>
    <div class="filter-tabs">
      <button class:active={activeFilter === 'day'} on:click={() => setFilter('day')}>Today</button>
      <button class:active={activeFilter === 'week'} on:click={() => setFilter('week')}>7 Days</button>
      <button class:active={activeFilter === 'month'} on:click={() => setFilter('month')}>30 Days</button>
      <button class:active={activeFilter === 'year'} on:click={() => setFilter('year')}>12 Months</button>
    </div>
  </div>

  <div class="analytics-viz-grid">
    <div class="metric-viz-card chart-panel">
      <div class="chart-header">
        <span class="viz-label">Revenue vs Profit: {activeFilter}</span>
        <div class="legend">
          <span class="legend-item"><div class="legend-line" style="background: #00bcd4;"></div> Revenue</span>
          <span class="legend-item"><div class="legend-line" style="background: #4caf50;"></div> Profit</span>
        </div>
        <span class="chart-total">₹{totalPeriodSales.toLocaleString(undefined, {minimumFractionDigits: 2})}</span>
      </div>

      <div class="svg-container" role="figure" on:mouseleave={() => hoveredData = null}>
        <svg viewBox="0 0 800 200" preserveAspectRatio="none" class="chart-svg">
          <polyline points={revLinePoints} fill="none" stroke="#00bcd4" stroke-width="4" stroke-linejoin="round" />
          {#each activeData as d, i}
            {@const step = 800 / activeData.length}
            {@const xPos = (i * step) + (step / 2)}
            {@const yPos = 200 - (d.revenue / maxRevenue) * 180}
            <circle cx={xPos} cy={yPos} r="5" fill="#1a1a21" stroke="#00bcd4" stroke-width="3" class="svg-dot" role="graphics-symbol" tabindex="-1" on:mouseenter={() => hoveredData = d} />
          {/each}

          <polyline points={profLinePoints} fill="none" stroke="#4caf50" stroke-width="4" stroke-linejoin="round" />
          {#each activeData as d, i}
            {@const step = 800 / activeData.length}
            {@const xPos = (i * step) + (step / 2)}
            {@const yPos = 200 - (d.profit / maxProfit) * 180}
            <circle cx={xPos} cy={yPos} r="5" fill="#1a1a21" stroke="#4caf50" stroke-width="3" class="svg-dot" role="graphics-symbol" tabindex="-1" on:mouseenter={() => hoveredData = d} />
          {/each}
        </svg>

        {#if hoveredData}
          <div class="chart-tooltip animate-fade-in">
            <strong>{hoveredData.label}</strong>
            <div class="tooltip-line">Gross: <span>₹{hoveredData.revenue.toFixed(2)}</span></div>
            <div class="tooltip-line text-green">Profit: <span>₹{hoveredData.profit.toFixed(2)}</span></div>
          </div>
        {/if}
      </div>

      <div class="axis-labels">
        {#each activeData as d}
          <span>{d.label}</span>
        {/each}
      </div>
    </div>

    <div class="mini-widgets-col">
      <div class="metric-viz-card emerald mini-card">
        <span class="viz-label">Total Operational Margin</span>
        <h3 class="text-green">₹{totalProfit.toFixed(2)}</h3>
      </div>
      <div class="metric-viz-card cyan mini-card">
        <span class="viz-label">Payment Distribution</span>
        <div class="payment-ratio-bar">
          <span class="segment upi" style="width: {groupedBills.length ? (upiCount / groupedBills.length) * 100 : 50}%" title="UPI"></span>
          <span class="segment cash" style="width: {groupedBills.length ? (cashCount / groupedBills.length) * 100 : 50}%" title="Cash"></span>
        </div>
        <div class="ratio-legends">
          <span class="dot-legend upi-dot">UPI ({upiCount})</span>
          <span class="dot-legend cash-dot">Cash ({cashCount})</span>
        </div>
      </div>
    </div>
  </div>

  <div class="panel-card">
    <div class="panel-title">Invoice Ledger Matrix</div>
    {#if groupedBills.length === 0}
      <div class="empty-box">No finalized invoices recorded yet.</div>
    {:else}
      <div class="table-frame">
        <table>
          <thead>
            <tr>
              <th style="width: 40px;"></th>
              <th>Invoice No.</th>
              <th>Sale ID</th>
              <th>Customer Info</th>
              <th>Payment</th>
              <th class="text-right">Gross Total</th>
              <th class="text-right">Net Profit</th>
              <th class="text-center">Status</th>
              <th class="text-center">Action</th>
            </tr>
          </thead>
          <tbody>
            {#each groupedBills as bill}
              <tr class="clickable-row {expandedBillId === bill.id ? 'active-row' : ''}" on:click={() => toggleRow(bill.id)}>
                <td class="text-center text-muted expansion-arrow">{expandedBillId === bill.id ? "▼" : "▶"}</td>
                <td class="invoice-number-text">{bill.bill_number}</td>
                <td class="sale-id-text">#{bill.id}</td>
                <td>
                  <div class="cust-title">{bill.customer_name}</div>
                  <div class="cust-subtitle">{bill.customer_phone}</div>
                </td>
                <td><span class="badge-pay">{bill.payment_method}</span></td>
                <td class="text-right text-bold">₹{bill.total_bill_amount.toFixed(2)}</td>
                <td class="text-right text-green">₹{bill.total_profit.toFixed(2)}</td>
                <td class="text-center"><span class="badge-status-finalized">PAID</span></td>
                <td class="text-center">
                  <button class="btn-delete-row" on:click|stopPropagation={() => handleDeleteSale(bill.id)} title="Delete Invoice">✕</button>
                </td>
              </tr>

              {#if expandedBillId === bill.id}
                <tr class="nested-expansion-wrapper">
                  <td colspan="9">
                    <div class="expanded-details-drawer animate-slide-down">
                      <h4>Bill Breakdown</h4>
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
                        {#if bill.discount > 0}<div class="summary-line text-red"><span>Discount:</span> <span>- ₹{bill.discount.toFixed(2)}</span></div>{/if}
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
    {/if}
  </div>
</div>

<style>
  .page-view { padding: 10px; color: #e1e1e6; }
  .header-flex { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
  .header-text h2 { font-size: 24px; font-weight: 600; color: #ffffff; margin: 0 0 4px 0; }
  .subtitle { font-size: 14px; color: #8e8e9a; margin: 0; }

  .filter-tabs { display: flex; background: #18181f; border-radius: 8px; padding: 4px; border: 1px solid #292933; }
  .filter-tabs button { background: transparent; border: none; color: #8e8e9a; padding: 8px 16px; font-size: 13px; font-weight: 500; cursor: pointer; border-radius: 6px; transition: 0.2s ease; }
  .filter-tabs button:hover { color: #ffffff; }
  .filter-tabs button.active { background: #262631; color: #00bcd4; }

  .analytics-viz-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 24px; margin-bottom: 32px; }
  .mini-widgets-col { display: flex; flex-direction: column; gap: 24px; }
  
  .metric-viz-card { background: #1a1a21; border: 1px solid #292933; padding: 24px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.15); }
  .mini-card { flex: 1; display: flex; flex-direction: column; justify-content: center; }
  .metric-viz-card h3 { margin: 12px 0 0 0; font-size: 28px; color: #ffffff; font-weight: 600; }
  .viz-label { font-size: 12px; color: #8e8e9a; text-transform: uppercase; font-weight: 600; letter-spacing: 0.8px; }

  .chart-panel { display: flex; flex-direction: column; min-height: 280px; }
  .chart-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
  .chart-total { font-size: 22px; font-weight: 700; color: #ffffff; }
  
  .legend { display: flex; gap: 16px; font-size: 12px; color: #a1a1aa; font-weight: 500; }
  .legend-item { display: flex; align-items: center; gap: 6px; }
  .legend-line { width: 16px; height: 3px; border-radius: 2px; }

  .svg-container { position: relative; flex: 1; width: 100%; min-height: 180px; margin-bottom: 10px; border-bottom: 1px solid #292933; }
  .chart-svg { width: 100%; height: 100%; overflow: visible; }
  
  .svg-dot { transition: r 0.2s, fill 0.2s, stroke-width 0.2s; cursor: pointer; }
  .svg-dot:hover { r: 8; fill: #ffffff; stroke-width: 4; }

  .chart-tooltip { position: absolute; top: -10px; right: 10px; background: rgba(21, 21, 26, 0.95); border: 1px solid #292933; padding: 12px; border-radius: 6px; font-size: 13px; color: #e1e1e6; box-shadow: 0 8px 24px rgba(0,0,0,0.4); pointer-events: none; z-index: 10; min-width: 140px; }
  .chart-tooltip strong { display: block; color: #ffffff; margin-bottom: 8px; font-size: 14px; border-bottom: 1px solid #292933; padding-bottom: 4px; }
  .tooltip-line { display: flex; justify-content: space-between; margin-bottom: 4px; }
  .tooltip-line span { font-weight: 600; font-family: monospace; }

  .axis-labels { display: flex; justify-content: space-around; width: 100%; font-size: 11px; color: #8e8e9a; font-weight: 500; padding: 0 10px; }
  
  .payment-ratio-bar { height: 8px; border-radius: 4px; display: flex; overflow: hidden; margin-top: 16px; background: #202028; }
  .segment.upi { background: #00bcd4; }
  .segment.cash { background: #ff9800; }
  .ratio-legends { display: flex; gap: 16px; margin-top: 12px; }
  .dot-legend { font-size: 12px; color: #a1a1aa; display: flex; align-items: center; gap: 6px; }
  .dot-legend::before { content: ''; width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
  .upi-dot::before { background: #00bcd4; }
  .cash-dot::before { background: #ff9800; }

  .panel-card { background: #1a1a21; border: 1px solid #292933; padding: 24px; border-radius: 12px; }
  .panel-title { font-size: 14px; font-weight: 600; color: #ffffff; margin-bottom: 24px; }
  .table-frame { overflow-x: auto; width: 100%; }
  
  table { width: 100%; border-collapse: separate; border-spacing: 0; }
  th { background: #202028; color: #8e8e9a; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; padding: 14px 16px; text-align: left; font-weight: 600; }
  th:first-child { border-top-left-radius: 8px; border-bottom-left-radius: 8px; }
  th:last-child { border-top-right-radius: 8px; border-bottom-right-radius: 8px; }
  td { padding: 16px; border-bottom: 1px solid #202028; font-size: 14px; color: #a1a1aa; vertical-align: middle; }
  
  .clickable-row { cursor: pointer; transition: background 0.2s ease; }
  .clickable-row:hover { background: #202028; }
  .active-row { background: #202028; }
  
  .invoice-number-text { font-family: monospace; color: #e1e1e6; font-weight: 600; }
  .sale-id-text { font-family: monospace; color: #00bcd4; font-weight: 600; }
  .cust-title { font-weight: 500; color: #ffffff; }
  .cust-subtitle { font-size: 12px; color: #8e8e9a; margin-top: 4px; }
  
  .badge-pay { background: #262631; color: #a1a1aa; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 500; }
  .badge-status-finalized { background: rgba(76, 175, 80, 0.1); color: #4caf50; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 600; border: 1px solid rgba(76, 175, 80, 0.2); }
  .btn-delete-row { background: rgba(255, 82, 82, 0.1); border: 1px solid rgba(255, 82, 82, 0.3); color: #ff5252; padding: 6px 12px; border-radius: 6px; font-weight: bold; cursor: pointer; transition: all 0.2s; }
  .btn-delete-row:hover { background: #ff5252; color: #ffffff; }

  .nested-expansion-wrapper td { padding: 0 !important; border-bottom: none; }
  .expanded-details-drawer { padding: 24px; background: #15151a; border-radius: 0 0 8px 8px; box-shadow: inset 0 4px 12px rgba(0,0,0,0.1); }
  .expanded-details-drawer h4 { margin: 0 0 16px 0; font-size: 13px; font-weight: 600; color: #e1e1e6; }
  
  .inner-details-table { background: transparent; }
  .inner-details-table th { background: transparent; color: #7c7c8a; border-bottom: 1px solid #292933; border-radius: 0; padding: 10px 0; }
  .inner-details-table td { padding: 12px 0; border-bottom: 1px dashed #292933; font-size: 13px; color: #8e8e9a; }
  .inner-details-table tr:last-child td { border-bottom: none; }
  
  .font-medium { font-weight: 500; }
  .sku-sub-text { font-family: monospace; color: #8e8e9a; font-size: 12px; }
  .expanded-summary-footer { display: flex; flex-direction: column; align-items: flex-end; gap: 8px; margin-top: 16px; padding-top: 16px; border-top: 1px solid #292933; }
  .summary-line { display: flex; justify-content: space-between; width: 250px; font-size: 13px; color: #a1a1aa; }
  .summary-line span:last-child { font-weight: 600; font-family: monospace; color: #ffffff; }

  .text-center { text-align: center; }
  .text-right { text-align: right; }
  .text-bold { font-weight: 600; }
  .text-green { color: #4caf50; }
  .text-cyan { color: #00bcd4; }
  .text-red { color: #ff5252; }
  .text-white { color: #ffffff; }
  .text-muted { color: #7c7c8a; }
  
  .empty-box { text-align: center; color: #7c7c8a; padding: 40px; border: 1px dashed #3a3a47; border-radius: 8px; }
  .animate-fade-in { animation: fadeIn 0.3s ease; }
  .animate-slide-down { animation: slideDown 0.2s ease-out; }
  @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
  @keyframes slideDown { from { opacity: 0; transform: translateY(-8px); } to { opacity: 1; transform: translateY(0); } }
</style>