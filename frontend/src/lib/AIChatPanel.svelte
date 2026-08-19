<script lang="ts">
  import { Base_URL } from "./api";

  let isOpen = $state(false);
  let isLoading = $state(false);
  let inputText = $state("");
  let messages = $state<Array<{ role: 'user' | 'ai'; text: string; data?: any }>>([]);
  let chatBox: HTMLElement | undefined = $state(undefined);

  function togglePanel() {
    isOpen = !isOpen;
    if (isOpen && messages.length === 0) {
      messages = [{ role: 'ai', text: "Hello! I'm Stash AI. How can I help you manage your store today?" }];
    }
  }

  $effect(() => {
    if (messages.length > 0 && chatBox) {
      setTimeout(() => {
        chatBox.scrollTop = chatBox.scrollHeight;
      }, 50);
    }
  });

  async function sendMessage(text: string = inputText) {
    const q = text.trim();
    if (!q) return;
    
    messages = [...messages, { role: 'user', text: q }];
    inputText = "";
    isLoading = true;

    try {
      const token = localStorage.getItem("token");
      const res = await fetch(`${Base_URL}/ai/chat`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ question: q })
      });

      if (!res.ok) throw new Error("AI request failed");
      
      const data = await res.json();
      messages = [...messages, { role: 'ai', text: data.answer, data: data.data }];
    } catch (err) {
      messages = [...messages, { role: 'ai', text: "Sorry, I'm having trouble connecting right now." }];
    } finally {
      isLoading = false;
    }
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter') {
      e.preventDefault();
      sendMessage();
    }
  }

  const suggestions = [
    "Top products this week",
    "Today's revenue",
    "Low stock items",
    "Recent sales"
  ];
</script>

<div class="ai-chat-container">
  {#if isOpen}
    <div class="ai-panel animate-slide-up">
      <div class="ai-header">
        <div class="ai-title">
          <span class="ai-icon">🧠</span>
          <span>Stash AI</span>
        </div>
        <button class="ai-close-btn" onclick={togglePanel}>✕</button>
      </div>

      <div class="ai-messages" bind:this={chatBox}>
        {#each messages as msg}
          <div class="msg-wrapper {msg.role}">
            <div class="msg-bubble">
              <div class="msg-text">{msg.text}</div>
              {#if msg.data}
                <div class="msg-data">
                  <pre>{JSON.stringify(msg.data, null, 2)}</pre>
                </div>
              {/if}
            </div>
          </div>
        {/each}
        {#if isLoading}
          <div class="msg-wrapper ai">
            <div class="msg-bubble typing">
              <span class="dot"></span>
              <span class="dot"></span>
              <span class="dot"></span>
            </div>
          </div>
        {/if}
      </div>

      {#if messages.length === 1}
        <div class="ai-suggestions">
          {#each suggestions as sug}
            <button class="sug-chip" onclick={() => sendMessage(sug)}>{sug}</button>
          {/each}
        </div>
      {/if}

      <div class="ai-input-area">
        <input 
          type="text" 
          bind:value={inputText} 
          onkeydown={handleKeydown}
          placeholder="Ask Stash AI anything..."
          disabled={isLoading}
        />
        <button class="send-btn" onclick={() => sendMessage()} disabled={!inputText.trim() || isLoading} aria-label="Send message">
          <svg viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" stroke-width="2" fill="none"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
        </button>
      </div>
    </div>
  {/if}

  <button class="ai-toggle-btn" class:is-open={isOpen} onclick={togglePanel}>
    {#if isOpen}
      <svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
    {:else}
      🤖
    {/if}
  </button>
</div>

<style>
  .ai-chat-container {
    position: fixed;
    bottom: 24px;
    right: 24px;
    z-index: 9998;
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 16px;
  }

  .ai-toggle-btn {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: var(--accent-primary, #10b981);
    color: white;
    border: none;
    box-shadow: 0 8px 24px rgba(16, 185, 129, 0.4);
    cursor: pointer;
    font-size: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  }

  .ai-toggle-btn:hover {
    transform: scale(1.1);
  }

  .ai-toggle-btn.is-open {
    background: var(--bg-card-hover, #334155);
    font-size: 20px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  }

  .ai-panel {
    width: 380px;
    height: 500px;
    background: var(--glass-bg, rgba(30, 41, 59, 0.85));
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid var(--border-light, rgba(255, 255, 255, 0.1));
    border-radius: var(--radius-lg, 16px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .ai-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    background: rgba(0, 0, 0, 0.2);
    border-bottom: 1px solid var(--border-light, rgba(255, 255, 255, 0.1));
  }

  .ai-title {
    display: flex;
    align-items: center;
    gap: 10px;
    font-weight: 800;
    font-size: 16px;
    color: var(--text-main, #f8fafc);
  }

  .ai-icon {
    font-size: 20px;
  }

  .ai-close-btn {
    background: transparent;
    border: none;
    color: var(--text-muted, #94a3b8);
    cursor: pointer;
    font-size: 18px;
    transition: color 0.2s;
  }

  .ai-close-btn:hover {
    color: var(--text-main, #fff);
  }

  .ai-messages {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .msg-wrapper {
    display: flex;
    width: 100%;
  }

  .msg-wrapper.user {
    justify-content: flex-end;
  }

  .msg-wrapper.ai {
    justify-content: flex-start;
  }

  .msg-bubble {
    max-width: 85%;
    padding: 12px 16px;
    border-radius: 16px;
    font-size: 14px;
    line-height: 1.5;
    word-break: break-word;
  }

  .user .msg-bubble {
    background: var(--accent-primary, #10b981);
    color: #fff;
    border-bottom-right-radius: 4px;
  }

  .ai .msg-bubble {
    background: var(--bg-card-hover, #334155);
    color: var(--text-main, #f8fafc);
    border: 1px solid var(--border-light, rgba(255, 255, 255, 0.1));
    border-bottom-left-radius: 4px;
  }

  .msg-data pre {
    background: rgba(0, 0, 0, 0.3);
    padding: 10px;
    border-radius: 8px;
    font-size: 12px;
    overflow-x: auto;
    margin-top: 10px;
    color: var(--text-muted, #94a3b8);
  }

  .typing {
    display: flex;
    gap: 4px;
    padding: 16px 20px;
    align-items: center;
  }

  .dot {
    width: 6px;
    height: 6px;
    background: var(--text-muted, #94a3b8);
    border-radius: 50%;
    animation: typing 1.4s infinite ease-in-out both;
  }

  .dot:nth-child(1) { animation-delay: -0.32s; }
  .dot:nth-child(2) { animation-delay: -0.16s; }

  @keyframes typing {
    0%, 80%, 100% { transform: scale(0); }
    40% { transform: scale(1); }
  }

  .ai-suggestions {
    padding: 0 20px 10px;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .sug-chip {
    background: rgba(16, 185, 129, 0.15);
    border: 1px solid rgba(16, 185, 129, 0.3);
    color: var(--accent-primary, #10b981);
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }

  .sug-chip:hover {
    background: var(--accent-primary, #10b981);
    color: #fff;
  }

  .ai-input-area {
    padding: 16px 20px;
    background: rgba(0, 0, 0, 0.2);
    border-top: 1px solid var(--border-light, rgba(255, 255, 255, 0.1));
    display: flex;
    gap: 10px;
  }

  .ai-input-area input {
    flex: 1;
    background: var(--bg-input, #0f172a);
    border: 1px solid var(--border-solid, #334155);
    padding: 12px 16px;
    border-radius: 24px;
    color: var(--text-main, #f8fafc);
    font-size: 14px;
    outline: none;
    transition: border-color 0.2s;
  }

  .ai-input-area input:focus {
    border-color: var(--accent-primary, #10b981);
  }

  .send-btn {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    background: var(--accent-primary, #10b981);
    color: white;
    border: none;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: transform 0.2s, opacity 0.2s;
  }

  .send-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }

  .send-btn:not(:disabled):hover {
    transform: scale(1.05);
  }

  .animate-slide-up {
    animation: slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  }

  @keyframes slideUp {
    from { opacity: 0; transform: translateY(20px) scale(0.95); }
    to { opacity: 1; transform: translateY(0) scale(1); }
  }
</style>
