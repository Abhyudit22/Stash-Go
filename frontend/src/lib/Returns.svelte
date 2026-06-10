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

<div class="page-view animate-fade">
  <div class="terminal-header">
    <div>
      <h2>RETURNS & REVERSAL WORKSPACE</h2>
      <p class="subtitle">Process inventory intake reversals, balance gross revenue sheets, and verify matching references.</p>
    </div>
    <div class="terminal-badge">Total Returns Logged: {returnsHistory.length}</div>
  </div>

  <div class="checkout-layout-grid">
    <div class="panel-card">
      <div class="panel-title">Initiate Product Return</div>
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
      <div class="panel-title text-orange">Returns Audit Ledger</div>
      <div class="audit-stream">
        {#if returnsHistory.length === 0}
          <div class="placeholder-text">
            <p>No historical inventory processing return records logged in the database architecture context.</p>
          </div>
        {:else}
          {#each returnsHistory as ret}
            <div class="audit-card">
              <div class="audit-header">
                <span>Return Registry #{ret.id}</span>
                <span class="text-muted">Origin Sale: #{ret.sale_id}</span>
              </div>
              <div class="audit-body">
                <p><strong>Product Line:</strong> {ret.product_name || ret.product_id}</p>
                <p><strong>Quantity Returned:</strong> <span class="text-orange">{ret.quantity} items</span></p>
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
  
  .terminal-header, .audit-header, .field-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .terminal-header { margin-bottom: 30px; }
  .page-view h2 { color: #ffffff; font-size: 22px; margin: 0 0 6px 0; border-left: 4px solid #ff9800; padding-left: 12px; }
  .subtitle { color: #8e8e9a; font-size: 14px; margin: 0; }
  
  .terminal-badge { 
    background: #1e1e24; border: 1px solid #29292e; color: #ff9800; 
    padding: 6px 14px; border-radius: 4px; font-size: 13px; font-weight: bold; 
  }

  .checkout-layout-grid { display: grid; grid-template-columns: 1fr 1.2fr; gap: 30px; width: 100%; }
  .panel-card { background: #1e1e24; border: 1px solid #29292e; padding: 30px; border-radius: 8px; box-sizing: border-box; display: flex; flex-direction: column; }
  .panel-card.dark-bg { background: #15151a; }
  .panel-title { font-size: 14px; font-weight: bold; text-transform: uppercase; color: #ff9800; letter-spacing: 0.8px; margin-bottom: 20px; border-bottom: 1px solid #29292e; padding-bottom: 8px; }

  .stacked-form, .audit-stream, .audit-card { display: flex; flex-direction: column; }
  .stacked-form { gap: 16px; }
  .field-row { gap: 16px; width: 100%; }
  .field-group { flex: 1; }
  .field-group label { display: block; font-size: 13px; color: #b0bec5; margin-bottom: 8px; }

  input, select { background: #2a2a35; border: 1px solid #3a3a47; padding: 12px; color: white; border-radius: 4px; font-size: 14px; width: 100%; box-sizing: border-box; }
  input:focus, select:focus { outline: none; border-color: #ff9800; }
  
  .btn-return { border: none; padding: 14px; font-weight: bold; border-radius: 4px; cursor: pointer; font-size: 14px; text-transform: uppercase; background: #ff9800; color: #121214; transition: background 0.2s; }
  .btn-return:hover { background: #e68a00; }

  .audit-stream { gap: 14px; max-height: 420px; overflow-y: auto; }
  .audit-card { background: #1e1e24; border: 1px solid #29292e; border-radius: 6px; padding: 16px; border-left: 4px solid #ff9800; }
  .audit-header { font-size: 12px; font-weight: bold; margin-bottom: 10px; color: #ffffff; }
  .audit-body p { margin: 4px 0; font-size: 13px; color: #b0bec5; }

  .text-orange { color: #ff9800; font-weight: bold; }
  .text-muted { color: #8e8e9a; }
  .reason-quote { font-style: italic; color: #7c7c8a; margin-top: 8px !important; }
  .placeholder-text { text-align: center; color: #7c7c8a; font-size: 14px; padding: 40px 0; }
  
  .animate-fade { animation: fadeIn 0.25s ease-out forwards; }
  @keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }
</style>