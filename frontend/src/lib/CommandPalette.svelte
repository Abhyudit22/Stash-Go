<script lang="ts">
  import { onMount } from 'svelte';
  import type { Product } from './types';
  import { aiSemanticSearch } from './api';

  let { 
    isOpen = false, 
    products = [], 
    onClose = () => {}, 
    onNavigate = (page: string) => {},
    onSelectProduct = (p: Product) => {}
  }: {
    isOpen?: boolean;
    products?: Product[];
    onClose?: () => void;
    onNavigate?: (page: string) => void;
    onSelectProduct?: (p: Product) => void;
  } = $props();

  let searchQuery = $state('');
  let selectedIndex = $state(0);
  let aiResults: any[] = $state([]);
  let isSearchingAI = $state(false);
  let searchTimeout: any = $state(null);

  const pages = [
    { id: 'dashboard', name: 'Business Intelligence Dashboard', icon: '📊', group: 'Navigation' },
    { id: 'inventory', name: 'Inventory Control Workstation', icon: '📦', group: 'Navigation' },
    { id: 'counter', name: 'Billing Counter (POS)', icon: '💳', group: 'Navigation' },
    { id: 'sales', name: 'Sales Ledger & Analytics', icon: '🧾', group: 'Navigation' },
    { id: 'returns', name: 'Returns & Reversal Workspace', icon: '🔄', group: 'Navigation' }
  ];

  // Debounced AI semantic search
  $effect(() => {
    const q = searchQuery.trim();
    if (q.length >= 2) {
      if (searchTimeout) clearTimeout(searchTimeout);
      searchTimeout = setTimeout(async () => {
        isSearchingAI = true;
        const results = await aiSemanticSearch(q, 8);
        if (results && results.length > 0) {
          aiResults = results;
        } else {
          aiResults = [];
        }
        isSearchingAI = false;
      }, 300);
    } else {
      aiResults = [];
    }
  });

  let filteredItems = $derived.by(() => {
    const q = searchQuery.trim().toLowerCase();
    
    // If AI results are available, use them for products
    if (aiResults.length > 0) {
      const matchedPages = pages.filter(p => p.name.toLowerCase().includes(q)).map(p => ({ ...p, group: 'Navigation' }));
      const aiProducts = aiResults.map((r: any) => ({
        id: `p-${r.product_id}`,
        name: `${r.product_name} — ₹${r.selling_price.toFixed(2)}`,
        icon: '🏷️',
        group: `AI Match ${(r.similarity_score * 100).toFixed(0)}%`,
        product: products.find(p => String(p.id) === String(r.product_id)) || { id: r.product_id, name: r.product_name, sku: r.sku, selling_price: r.selling_price, quantity_left: r.quantity_left }
      }));
      return [...matchedPages, ...aiProducts];
    }
    
    // Fallback to local filtering
    if (!q) return [...pages, ...products.slice(0, 5).map(p => ({ id: `p-${p.id}`, name: `${p.name} (${p.sku})`, icon: '🏷️', group: 'Products', product: p }))];

    const matchedPages = pages.filter(p => p.name.toLowerCase().includes(q)).map(p => ({ ...p, group: 'Navigation' }));
    const matchedProducts = products.filter(p => p.name.toLowerCase().includes(q) || p.sku.toLowerCase().includes(q))
      .slice(0, 8)
      .map(p => ({ id: `p-${p.id}`, name: `${p.name} — ₹${p.selling_price.toFixed(2)}`, icon: '🏷️', group: 'Products', product: p }));

    return [...matchedPages, ...matchedProducts];
  });

  function handleKeyDown(e: KeyboardEvent) {
    if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      isOpen = !isOpen;
      if (isOpen) {
        searchQuery = '';
        selectedIndex = 0;
      }
    } else if (isOpen) {
      if (e.key === 'Escape') {
        isOpen = false;
        onClose();
      } else if (e.key === 'ArrowDown') {
        e.preventDefault();
        selectedIndex = (selectedIndex + 1) % (filteredItems.length || 1);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        selectedIndex = (selectedIndex - 1 + filteredItems.length) % (filteredItems.length || 1);
      } else if (e.key === 'Enter' && filteredItems[selectedIndex]) {
        e.preventDefault();
        executeItem(filteredItems[selectedIndex]);
      }
    }
  }

  function executeItem(item: any) {
    isOpen = false;
    onClose();
    if (item.product) {
      onSelectProduct(item.product);
      onNavigate('counter');
    } else {
      onNavigate(item.id);
    }
  }

  onMount(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  });
</script>

{#if isOpen}
  <div 
    class="cmd-overlay" 
    onclick={() => { isOpen = false; onClose(); }} 
    onkeydown={(e) => { if (e.key === 'Escape') { isOpen = false; onClose(); } }}
    role="dialog" 
    aria-modal="true" 
    tabindex="-1"
  >
    <div 
      class="cmd-modal animate-scale-in" 
      onclick={e => e.stopPropagation()} 
      onkeydown={e => e.stopPropagation()}
      role="document"
      tabindex="-1"
    >
      <div class="cmd-search-header">
        <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
        <input 
          type="text" 
          bind:value={searchQuery} 
          placeholder="Search products, SKUs, or navigate... (Press Esc to exit)" 
        />
        <span class="cmd-esc-tag">ESC</span>
      </div>

      <div class="cmd-results-list">
        {#if filteredItems.length === 0}
          <div class="cmd-empty">No matching products or pages found for "{searchQuery}"</div>
        {:else}
          {#each filteredItems as item, idx}
            <button 
              type="button"
              class="cmd-item" 
              class:selected={idx === selectedIndex}
              onclick={() => executeItem(item)}
              onmouseenter={() => selectedIndex = idx}
            >
              <span class="cmd-icon">{item.icon}</span>
              <span class="cmd-name">{item.name}</span>
              <span class="cmd-badge">{item.group}</span>
            </button>
          {/each}
        {/if}
      </div>

      <div class="cmd-footer">
        <span>{isSearchingAI ? '🧠 AI searching...' : 'Use'} <kbd>↑</kbd> <kbd>↓</kbd> to navigate</span>
        <span><kbd>Enter</kbd> to select</span>
        {#if aiResults.length > 0}
          <span class="ai-search-badge">🤖 Semantic Search Active</span>
        {/if}
      </div>
    </div>
  </div>
{/if}

<style>
  .cmd-overlay {
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(15, 23, 42, 0.6);
    backdrop-filter: blur(6px);
    z-index: 99999;
    display: flex;
    justify-content: center;
    align-items: flex-start;
    padding-top: 100px;
  }

  .cmd-modal {
    width: 100%;
    max-width: 620px;
    background: var(--bg-card);
    border-radius: 16px;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.25);
    border: 1px solid var(--border-light);
    overflow: hidden;
  }

  .cmd-search-header {
    display: flex;
    align-items: center;
    padding: 16px 20px;
    border-bottom: 1px solid var(--border-light);
    gap: 12px;
    color: var(--text-muted);
  }

  .cmd-search-header input {
    flex: 1;
    border: none;
    background: transparent;
    font-size: 16px;
    color: var(--text-main);
    outline: none;
  }

  .cmd-esc-tag {
    font-size: 11px;
    font-weight: 700;
    background: var(--bg-card-hover);
    padding: 3px 8px;
    border-radius: 6px;
    color: var(--text-muted);
  }

  .cmd-results-list {
    max-height: 340px;
    overflow-y: auto;
    padding: 10px;
  }

  .cmd-empty {
    padding: 30px;
    text-align: center;
    color: var(--text-muted);
    font-size: 14px;
  }

  .cmd-item {
    display: flex;
    align-items: center;
    width: 100%;
    border: none;
    background: transparent;
    text-align: left;
    padding: 12px 16px;
    border-radius: 10px;
    cursor: pointer;
    gap: 14px;
    transition: background 0.15s ease;
  }

  .cmd-item.selected {
    background: rgba(16, 185, 129, 0.15);
  }

  .cmd-icon { font-size: 18px; }
  .cmd-name { flex: 1; font-size: 14px; font-weight: 600; color: var(--text-main); }
  .cmd-badge { font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; }

  .cmd-footer {
    display: flex;
    justify-content: space-between;
    padding: 12px 20px;
    background: var(--bg-card-hover);
    border-top: 1px solid var(--border-light);
    font-size: 12px;
    color: var(--text-muted);
  }

  kbd {
    background: var(--bg-card);
    border: 1px solid var(--border-solid);
    border-radius: 4px;
    padding: 2px 6px;
    font-family: monospace;
    font-size: 11px;
    color: var(--text-main);
  }

  .animate-scale-in {
    animation: scaleIn 0.2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  }

  @keyframes scaleIn {
    from { opacity: 0; transform: scale(0.96) translateY(-10px); }
    to { opacity: 1; transform: scale(1) translateY(0); }
  }

  .ai-search-badge {
    background: rgba(16, 185, 129, 0.12);
    color: var(--accent-primary);
    padding: 2px 8px;
    border-radius: 8px;
    font-size: 10px;
    font-weight: 700;
  }
</style>
