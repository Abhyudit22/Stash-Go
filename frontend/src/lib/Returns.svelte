<script lang="ts">
  export let returnsHistory: any[] = [];
  export let handleProcessReturn: (data: any) => Promise<void>;

  let saleId = "", productId: number = 0, returnQty = 1, returnReason = "";

  async function localSubmit() {
    await handleProcessReturn({
      sale_id: parseInt(saleId),
      product_id: Number(productId),
      quantity: returnQty,
      reason: returnReason
    });
    saleId = ""; productId = 0; returnQty = 1; returnReason = "";
  }
</script>

<div class="page-view animate-fade-in">
  <div class="terminal-header">
    <div>
      <h2 class="gradient-text-header">RETURNS & REVERSAL WORKSPACE</h2>
      <p class="subtitle">Process inventory intake reversals, balance gross revenue sheets, and verify matching references.</p>
    </div>
    <div class="terminal-badge">Total Returns Logged: {returnsHistory.length}</div>
  </div>

  <div class="checkout-layout-grid">
    <div class="panel-card">
      <div class="panel-title text-amber">Initiate Product Return</div>
      <form on:submit|preventDefault={localSubmit} class="stacked-form">
        <div class="field-row">
          <div class="field-group">
            <label for="ret-sale">Target Sale ID</label>
            <input type="number" id="ret-sale" bind:value={saleId} placeholder="104" required />
          </div>
          <div class="field-group">
            <label for="ret-sku">Product ID</label>
            <input type="number" id="ret-sku" bind:value={productId} placeholder="3" required />
          </div>
        </div>
        <div class="field-group">
          <label for="ret-qty">Quantity to Return</label>
          <input type="number" id="ret-qty" bind:value={returnQty} min="1" required />
        </div>
        <div class="field-group">
          <label for="ret-reason">Reason for Reversal</label>
          <select id="ret-reason" bind:value={returnReason} required>
            <option value="" disabled selected>-- Select an explanation --</option>
            <option value="Damaged/Defective">Damaged / Defective Stock</option>
            <option value="Customer Dissatisfaction">Customer Dissatisfaction</option>
            <option value="Incorrect Item Dispensed">Incorrect Item Dispensed</option>
          </select>
        </div>
        <button type="submit" class="btn-return">Authorize Return Intake</button>
      </form>
    </div>

    <div class="panel-card dark-bg">
      <div class="panel-title text-amber">Returns Audit Ledger</div>
      <div class="audit-stream">
        {#if returnsHistory.length === 0}
          <div class="placeholder-text">
            <p>No historical inventory processing return records logged in the database architecture context.</p>
          </div>
        {:else}
          {#each returnsHistory as ret}
            <div class="audit-card">
              <div class="audit-header">
                <span class="text-white">Return Registry #{ret.id}</span>
                <span class="text-muted">Origin Sale: #{ret.sale_id}</span>
              </div>
              <div class="audit-body">
                <p><strong>Product Line:</strong> {ret.product_name || ret.product_id}</p>
                <p><strong>Quantity Returned:</strong> <span class="text-amber">{ret.quantity} items</span></p>
                <p class="reason-quote">" {ret.reason || 'No explanation specified.'} "</p>
              </div>
            </div>
          {/each}
        {/if}
      </div>
    </div>
  </div>
</div>

<style>
  .terminal-header, .audit-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .terminal-header { margin-bottom: 24px; flex-wrap: wrap; gap: 15px; }
  .page-view h2 { font-size: 24px; margin: 0 0 4px 0; color: var(--accent-primary); }
  .subtitle { color: var(--text-muted); font-size: 14px; margin: 0; }
  
  .terminal-badge {
    background: rgba(217, 119, 6, 0.1);
    border: 1px solid rgba(217, 119, 6, 0.25);
    color: var(--accent-warning);
    padding: 6px 16px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 700;
  }

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
  .panel-title { font-size: 14px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 20px; border-bottom: 1px solid var(--border-light); padding-bottom: 8px; color: var(--accent-warning); }

  .stacked-form, .audit-stream, .audit-card { display: flex; flex-direction: column; }
  .stacked-form { gap: 16px; }
  .field-row { display: flex; gap: 16px; width: 100%; }
  .field-group { flex: 1; }
  .field-group label { display: block; font-size: 13px; color: var(--text-muted); margin-bottom: 6px; font-weight: 600; }

  input, select {
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

  input:focus, select:focus { outline: none; border-color: var(--accent-warning); box-shadow: 0 0 0 3px rgba(217, 119, 6, 0.12); }
  
  .btn-return {
    border: none;
    padding: 12px;
    font-weight: 700;
    border-radius: 8px;
    cursor: pointer;
    font-size: 13px;
    text-transform: uppercase;
    background: var(--accent-warning);
    color: #ffffff;
    transition: transform 0.2s ease;
    box-shadow: 0 4px 12px rgba(217, 119, 6, 0.25);
  }

  .btn-return:hover { transform: translateY(-1px); }

  .audit-stream { gap: 14px; max-height: 420px; overflow-y: auto; }
  
  .audit-card {
    background: var(--bg-card);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-sm);
    padding: 16px;
    border-left: 4px solid var(--accent-warning);
  }

  .audit-header { font-size: 12px; font-weight: 700; margin-bottom: 10px; }
  .audit-body p { margin: 4px 0; font-size: 13px; color: var(--text-muted); }

  .text-amber { color: var(--accent-warning); font-weight: 700; }
  .text-muted { color: var(--text-muted); }
  .text-white { color: var(--text-main); font-weight: 700; }
  .reason-quote { font-style: italic; color: var(--text-muted); margin-top: 8px !important; }
  .placeholder-text { text-align: center; color: var(--text-muted); font-size: 14px; padding: 40px 0; }
</style>