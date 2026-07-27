<script lang="ts">
  import { toast, type ToastMessage } from './toastStore';

  let toasts: ToastMessage[] = $state([]);

  $effect(() => {
    const unsubscribe = toast.subscribe(value => {
      toasts = value;
    });
    return unsubscribe;
  });
</script>

{#if toasts.length > 0}
  <div class="toast-container">
    {#each toasts as t (t.id)}
      <div class="toast-card {t.type} animate-slide-up">
        <div class="toast-icon">
          {#if t.type === 'success'}
            <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2.5" fill="none"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
          {:else if t.type === 'error'}
            <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2.5" fill="none"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>
          {:else if t.type === 'warning'}
            <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2.5" fill="none"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
          {:else}
            <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2.5" fill="none"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
          {/if}
        </div>
        <div class="toast-content">
          <span class="toast-title">{t.title}</span>
          <span class="toast-msg">{t.message}</span>
        </div>
        <button class="toast-close" onclick={() => toast.remove(t.id)}>×</button>
      </div>
    {/each}
  </div>
{/if}

<style>
  .toast-container {
    position: fixed;
    bottom: 24px;
    right: 24px;
    z-index: 9999;
    display: flex;
    flex-direction: column;
    gap: 10px;
    max-width: 380px;
    pointer-events: none;
  }

  .toast-card {
    pointer-events: auto;
    background: var(--bg-card);
    border-radius: 12px;
    padding: 14px 18px;
    display: flex;
    align-items: center;
    gap: 14px;
    box-shadow: 0 10px 30px rgba(15, 23, 42, 0.15);
    border: 1px solid var(--border-light);
    color: var(--text-main);
  }

  .toast-card.success { border-left: 4px solid #10b981; }
  .toast-card.success .toast-icon { color: #10b981; }

  .toast-card.error { border-left: 4px solid #e11d48; }
  .toast-card.error .toast-icon { color: #e11d48; }

  .toast-card.warning { border-left: 4px solid #d97706; }
  .toast-card.warning .toast-icon { color: #d97706; }

  .toast-card.info { border-left: 4px solid #0f5a47; }
  .toast-card.info .toast-icon { color: #0f5a47; }

  .toast-content {
    display: flex;
    flex-direction: column;
    flex: 1;
  }

  .toast-title {
    font-weight: 700;
    font-size: 13px;
    color: var(--text-main);
  }

  .toast-msg {
    font-size: 12px;
    color: var(--text-muted);
    margin-top: 2px;
  }

  .toast-close {
    background: transparent;
    border: none;
    font-size: 18px;
    color: var(--text-muted);
    cursor: pointer;
    line-height: 1;
    padding: 0 4px;
  }

  .animate-slide-up {
    animation: slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  }

  @keyframes slideUp {
    from { opacity: 0; transform: translateY(20px) scale(0.95); }
    to { opacity: 1; transform: translateY(0) scale(1); }
  }
</style>
