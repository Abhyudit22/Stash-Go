<script lang="ts">
  interface ProductData {
    id?: number;
    sku?: string;
    name?: string;
    cost_price?: number;
    selling_price?: number;
  }

  interface BillData {
    id?: number;
    bill_number?: string;
    customer_name?: string;
    customer_phone?: string;
    customer_email?: string;
    payment_method?: string;
    discount?: number;
    tax?: number;
  }

  interface SaleRecord {
    id?: number;
    bill_id?: number;
    product_id?: number;
    quantity?: number;
    quantity_sold?: number;
    price?: number;
    selling_price?: number;
    cost_price?: number;
    customer_info?: string;
    bill_number?: string;
    customer_name?: string;
    customer_phone?: string;
    payment_method?: string;
    discount?: number;
    tax?: number;
    bill?: BillData;
    product?: ProductData;
  }

  interface GroupedBillItem {
    product_name: string;
    sku: string;
    quantity: number;
    unit_price: number;
    net_revenue: number;
    net_profit: number;
  }

  interface GroupedBill {
    id: number;
    bill_number: string;
    customer_name: string;
    customer_phone: string;
    payment_method: string;
    subtotal: number;
    discount: number;
    tax: number;
    total_bill_amount: number;
    total_profit: number;
    items: GroupedBillItem[];
  }

  export let salesHistory: SaleRecord[] = [];

  let expandedBillId: number | null = null;

  function toggleRow(billId: number) {
    expandedBillId = expandedBillId === billId ? null : billId;
  }

  $: groupedBills = Object.values(
    (salesHistory || []).reduce((acc: Record<number, GroupedBill>, currentItem: SaleRecord) => {
      if (!currentItem) return acc;

      const bId = currentItem.bill_id || currentItem.bill?.id || currentItem.id || 0;
      if (!bId) return acc;

      if (!acc[bId]) {
        acc[bId] = {
          id: bId,
          bill_number: currentItem.bill?.bill_number || currentItem.bill_number || `BILL-2026-${bId}`,
          customer_name: currentItem.bill?.customer_name || currentItem.customer_name || currentItem.customer_info || "Walk-in Customer",
          customer_phone: currentItem.bill?.customer_phone || currentItem.customer_phone || "N/A",
          payment_method: currentItem.bill?.payment_method || currentItem.payment_method || "Cash",
          subtotal: 0,
          discount: currentItem.bill?.discount || currentItem.discount || 0,
          tax: currentItem.bill?.tax || currentItem.tax || 0,
          total_bill_amount: 0,
          total_profit: 0,
          items: []
        };
      }

      
      const unitPrice = currentItem.price || currentItem.selling_price || currentItem.product?.selling_price || 0;
      const costPrice = currentItem.cost_price || currentItem.product?.cost_price || 0;
      const qty = currentItem.quantity || currentItem.quantity_sold || 1;
      
      const netRevenue = unitPrice * qty;
      const netProfit = (unitPrice - costPrice) * qty;

      acc[bId].subtotal += netRevenue;
      acc[bId].total_profit += netProfit;

      acc[bId].items.push({
        product_name: currentItem.product?.name || `Product ID #${currentItem.product_id || '?'}`,
        sku: currentItem.product?.sku || "N/A",
        quantity: qty,
        unit_price: unitPrice,
        net_revenue: netRevenue,
        net_profit: netProfit
      });

      return acc;
    }, {} as Record<number, GroupedBill>)
  ).map((bill: GroupedBill) => {
    bill.total_bill_amount = Math.max(0, bill.subtotal - bill.discount + bill.tax);
    return bill;
  });

  $: totalRevenue = groupedBills.reduce((sum, b) => sum + b.total_bill_amount, 0);
  $: totalProfit = groupedBills.reduce((sum, b) => sum + b.total_profit, 0);
  $: upiCount = groupedBills.filter(b => b.payment_method.toUpperCase() === 'UPI').length;
  $: cashCount = groupedBills.filter(b => b.payment_method.toUpperCase() === 'CASH').length;
</script>

<div class="page-view animate-fade-in">
  <div class="terminal-header">
    <div>
      <h2>SALES TRANSACTION HISTORICAL RECORDS</h2>
      <p class="subtitle">Review grouped checkout invoices, track absolute profit margin yields, and expand line items.</p>
    </div>
  </div>

  <div class="analytics-viz-grid">
    <div class="metric-viz-card crimson">
      <div class="card-glow"></div>
      <span class="viz-label">Gross Revenue Stream</span>
      <h3>₹{totalRevenue.toFixed(2)}</h3>
      <div class="viz-progress-bar"><div class="fill" style="width: 85%"></div></div>
    </div>

    <div class="metric-viz-card emerald">
      <div class="card-glow"></div>
      <span class="viz-label">Net Operational Margin</span>
      <h3 class="text-green">₹{totalProfit.toFixed(2)}</h3>
      <div class="viz-progress-bar"><div class="fill" style="width: 70%"></div></div>
    </div>

    <div class="metric-viz-card cyan">
      <div class="card-glow"></div>
      <span class="viz-label">Average Basket Value</span>
      <div class="payment-ratio-bar">
        <span class="segment upi" style="width: {groupedBills.length ? (upiCount / groupedBills.length) * 100 : 50}%" title="UPI payments"></span>
        <span class="segment cash" style="width: {groupedBills.length ? (cashCount / groupedBills.length) * 100 : 50}%" title="Cash payments"></span>
      </div>
      <div class="ratio-legends">
        <span class="dot-legend upi-dot">UPI: {upiCount}</span>
        <span class="dot-legend cash-dot">Cash: {cashCount}</span>
      </div>
    </div>
  </div>

  <div class="panel-card">
    <div class="panel-title">Master Invoice Audit Ledger Matrix</div>
    {#if groupedBills.length === 0}
      <div class="empty-box">No finalized invoice documents recorded in current database nodes.</div>
    {:else}
      <div class="table-frame">
        <table>
          <thead>
            <tr>
              <th style="width: 40px;"></th>
              <th>INVOICE NO.</th>
              <th>CUSTOMER PARTICULARS</th>
              <th>PAYMENT METHOD</th>
              <th class="text-right">GROSS PAYLOAD</th>
              <th class="text-right">NET SYSTEM PROFIT</th>
              <th class="text-center">STATUS</th>
            </tr>
          </thead>
          <tbody>
            {#each groupedBills as bill}
              <tr class="clickable-row" class:active-row={expandedBillId === bill.id} on:click={() => toggleRow(bill.id)}>
                <td class="text-center text-muted expansion-arrow">
                  {expandedBillId === bill.id ? "▼" : "▶"}
                </td>
                <td class="invoice-number-text">{bill.bill_number}</td>
                <td>
                  <div class="cust-title">{bill.customer_name}</div>
                  <div class="cust-subtitle">{bill.customer_phone}</div>
                </td>
                <td><span class="badge-pay">{bill.payment_method}</span></td>
                <td class="text-right text-bold">₹{bill.total_bill_amount.toFixed(2)}</td>
                <td class="text-right text-green">₹{bill.total_profit.toFixed(2)}</td>
                <td class="text-center"><span class="badge-status-finalized">PAID</span></td>
              </tr>

              {#if expandedBillId === bill.id}
                <tr class="nested-expansion-wrapper">
                  <td colspan="7">
                    <div class="expanded-details-drawer animate-slide-down">
                      <h4>Bill Specifications Breakdown Analysis</h4>
                      <table class="inner-details-table">
                        <thead>
                          <tr>
                            <th>ITEM PARTICULARS</th>
                            <th>SKU IDENTIFIER</th>
                            <th class="text-center">QTY PURCHASED</th>
                            <th class="text-right">UNIT RATE</th>
                            <th class="text-right">NET TOTAL</th>
                            <th class="text-right">MARGIN YIELD</th>
                          </tr>
                        </thead>
                        <tbody>
                          {#each bill.items as item}
                            <tr>
                              <td><strong>{item.product_name}</strong></td>
                              <td class="sku-sub-text">{item.sku}</td>
                              <td class="text-center text-bold">{item.quantity} units</td>
                              <td class="text-right">₹{item.unit_price.toFixed(2)}</td>
                              <td class="text-right text-bold">₹{item.net_revenue.toFixed(2)}</td>
                              <td class="text-right text-green">₹{item.net_profit.toFixed(2)}</td>
                            </tr>
                          {/each}
                          
                          <tr class="summary-spacer-row"><td colspan="6"></td></tr>
                          <tr class="inner-summary-line">
                            <td colspan="4" class="text-right label-text">Items Subtotal:</td>
                            <td class="text-right value-text">₹{bill.subtotal.toFixed(2)}</td>
                            <td></td>
                          </tr>
                          {#if bill.discount > 0}
                            <tr class="inner-summary-line text-red">
                              <td colspan="4" class="text-right label-text">Applied Discount Deductions:</td>
                              <td class="text-right value-text">- ₹{bill.discount.toFixed(2)}</td>
                              <td></td>
                            </tr>
                          {/if}
                          {#if bill.tax > 0}
                            <tr class="inner-summary-line text-cyan">
                              <td colspan="4" class="text-right label-text">Tax Surcharge Additions:</td>
                              <td class="text-right value-text">+ ₹{bill.tax.toFixed(2)}</td>
                              <td></td>
                            </tr>
                          {/if}
                        </tbody>
                      </table>
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
  /* VISUALIZATION CARDS DESIGN */
  .analytics-viz-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 30px; }
  @media (max-width: 850px) { .analytics-viz-grid { grid-template-columns: 1fr; } }
  
  .metric-viz-card { background: #16161c; border: 1px solid #23232a; padding: 20px; border-radius: 8px; position: relative; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.2); }
  .metric-viz-card h3 { margin: 8px 0; font-size: 26px; color: #ffffff; font-family: monospace; font-weight: bold; }
  .viz-label { font-size: 12px; color: #8e8e9a; text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px; }
  
  /* Glowing card effects map */
  .card-glow { position: absolute; width: 100px; height: 100px; top: -50px; right: -50px; border-radius: 50%; opacity: 0.15; filter: blur(30px); }
  .crimson .card-glow { background: #ff5252; }
  .emerald .card-glow { background: #4caf50; }
  .cyan .card-glow { background: #00bcd4; }

  /* Progress Metrics Visuals Elements */
  .viz-progress-bar { background: #22222b; height: 6px; border-radius: 3px; margin-top: 15px; overflow: hidden; }
  .viz-progress-bar .fill { height: 100%; border-radius: 3px; }
  .crimson .fill { background: #ff5252; }
  .emerald .fill { background: #4caf50; }

  /* Payment distribution visualizations tracking */
  .payment-ratio-bar { height: 10px; border-radius: 4px; display: flex; overflow: hidden; margin-top: 15px; background: #22222b; }
  .segment.upi { background: #00bcd4; }
  .segment.cash { background: #ff9800; }
  .ratio-legends { display: flex; gap: 15px; margin-top: 10px; }
  .dot-legend { font-size: 11px; font-family: monospace; color: #b0bec5; display: flex; align-items: center; gap: 5px; }
  .dot-legend::before { content: ''; display: inline-block; width: 8px; height: 8px; border-radius: 50%; }
  .upi-dot::before { background: #00bcd4; }
  .cash-dot::before { background: #ff9800; }

  /* STANDARD DATA LEDGER STYLING SYSTEM MAPS */
  .terminal-header { margin-bottom: 30px; }
  .page-view h2 { color: #ffffff; font-size: 22px; margin: 0 0 6px 0; }
  .subtitle { color: #8e8e9a; font-size: 14px; margin: 0; }
  
  .panel-card { background: #1e1e24; border: 1px solid #29292e; padding: 25px; border-radius: 8px; box-sizing: border-box; }
  .panel-title { font-size: 13px; font-weight: bold; text-transform: uppercase; color: #00bcd4; letter-spacing: 0.8px; margin-bottom: 20px; border-bottom: 1px solid #29292e; padding-bottom: 8px; }

  .table-frame { overflow-x: auto; width: 100%; }
  table { width: 100%; border-collapse: collapse; background: #15151a; border-radius: 6px; overflow: hidden; }
  th { background: #23232b; color: #8e8e9a; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; padding: 14px 12px; text-align: left; }
  td { padding: 14px 12px; border-bottom: 1px solid #1e1e24; font-size: 14px; color: #e1e1e6; vertical-align: middle; }
  
  .clickable-row { cursor: pointer; transition: background 0.15s ease-out; }
  .clickable-row:hover { background: #23232b; }
  .active-row { background: #1f242e !important; border-left: 3px solid #00bcd4; }
  .expansion-arrow { font-size: 10px; transition: transform 0.2s; user-select: none; }
  
  .invoice-number-text { font-family: monospace; color: #9cdcfe; font-weight: bold; font-size: 15px; }
  .cust-title { font-weight: 600; color: #ffffff; }
  .cust-subtitle { font-size: 12px; color: #7c7c8a; font-family: monospace; margin-top: 2px; }
  
  .badge-pay { background: #2a2a35; border: 1px solid #3a3a47; color: #b0bec5; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-family: monospace; }
  .badge-status-finalized { background: rgba(76, 175, 80, 0.15); color: #4caf50; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; border: 1px solid rgba(76, 175, 80, 0.2); }
  
  .nested-expansion-wrapper { background: #0e0e12; }
  .nested-expansion-wrapper td { padding: 0 !important; border-bottom: 1px solid #29292e; }
  .expanded-details-drawer { padding: 20px; background: #0f1012; border-bottom: 3px solid #29292e; }
  .expanded-details-drawer h4 { margin: 0 0 12px 0; font-size: 12px; text-transform: uppercase; color: #8e8e9a; letter-spacing: 0.5px; }
  
  .inner-details-table { width: 100%; border-collapse: collapse; background: #141619; border: 1px solid #1f2226; border-radius: 4px; }
  .inner-details-table th { background: #1a1d22; font-size: 10px; color: #7c7c8a; padding: 10px; }
  .inner-details-table td { padding: 10px; border-bottom: 1px solid #1a1d22; font-size: 13px; color: #c5c5d0; }
  .sku-sub-text { font-family: monospace; color: #dcdcaa; font-size: 12px; }

  .summary-spacer-row td { border: none !important; height: 8px; background: transparent; }
  .inner-summary-line td { padding: 4px 10px !important; border: none !important; font-size: 12px; background: transparent; }
  .inner-summary-line .label-text { color: #7c7c8a; font-weight: 500; }
  .inner-summary-line .value-text { font-family: monospace; font-weight: bold; color: #ffffff; font-size: 13px; }

  .text-center { text-align: center; }
  .text-right { text-align: right; }
  .text-bold { font-weight: bold; }
  .text-green { color: #4caf50; font-weight: bold; }
  .text-cyan { color: #00bcd4; }
  .text-red { color: #ff5252; }
  .text-muted { color: #5a5a65; }
  .empty-box { text-align: center; color: #7c7c8a; font-size: 14px; padding: 40px 0; border: 2px dashed #29292e; border-radius: 6px; }

  .animate-fade-in { animation: fadeIn 0.2s ease-out forwards; }
  .animate-slide-down { animation: slideDown 0.18s ease-out forwards; }
  @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
  @keyframes slideDown { from { opacity: 0; transform: translateY(-6px); } to { opacity: 1; transform: translateY(0); } }
</style>