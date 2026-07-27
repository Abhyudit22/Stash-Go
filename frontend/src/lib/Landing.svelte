<script lang="ts">
  export let launchApp: () => void = () => console.log("Routing to app...");
</script>

<div class="landing-container animate-fade-in" id="home">
  
  <!-- Navigation Header -->
  <nav class="navbar">
    <div class="logo">
      <span class="logo-icon">📦</span> Stash <span class="gradient-text">GO</span>
    </div>
    
    <div class="nav-links">
      <a href="#home" class="nav-link">Home</a>
      <button class="nav-launch-btn" onclick={launchApp}>
        Shopkeeper Terminal →
      </button>
    </div>
  </nav>

  <!-- Hero Section -->
  <header class="hero-section">
    <div class="badge-pill-live">
      <span class="pulse-dot"></span> v1.0 Production Ready
    </div>
    
    <h1 class="headline">
      Next-Gen Inventory & POS <br />
      <span class="gradient-text">Engineered for Speed.</span>
    </h1>

    <p class="subtitle">
      Seamlessly manage inventory, track real-time profit yields, generate digital receipts, and execute checkout operations with zero latency.
    </p>

    <div class="hero-actions">
      <button class="btn-primary" onclick={launchApp}>
        🚀 Launch Terminal
      </button>

      <a href="https://github.com/Abhyudit22/Stash-Go" target="_blank" rel="noreferrer" class="btn-secondary">
        GitHub Source
      </a>
    </div>
  </header>

  <!-- Stack Showcase Banner -->
  <div class="tech-stack-banner">
    <p class="tech-title">POWERED BY MODERN DISTRIBUTED ARCHITECTURE</p>
    <div class="tech-logos">
      <span class="tech-badge svelte">Svelte 5 & Vite</span>
      <span class="tech-badge python">FastAPI Async Core</span>
      <span class="tech-badge postgres">PostgreSQL Relational DB</span>
      <span class="tech-badge docker">Docker Containerized</span>
    </div>
  </div>

  <!-- Features Grid -->
  <section class="features-grid">
    <div class="feature-card">
      <div class="feature-icon text-cyan">⚡</div>
      <h3>Digital Terminal Counter</h3>
      <p>Lightning-fast POS terminal with dynamic percent-based tax, discount modifiers, and live receipt calculation.</p>
    </div>
    
    <div class="feature-card">
      <div class="feature-icon text-green">🧾</div>
      <h3>Sales Ledger & Invoicing</h3>
      <p>Audit detailed historical transactions, track item breakdowns, and safely manage bill deletions.</p>
    </div>
    
    <div class="feature-card">
      <div class="feature-icon text-purple">📊</div>
      <h3>Live Business Intelligence</h3>
      <p>Real-time SVG charts analyzing period gross revenue, net profit yields, and payment method distribution.</p>
    </div>

    <div class="feature-card">
      <div class="feature-icon text-amber">📦</div>
      <h3>Smart Inventory Control</h3>
      <p>Monitor SKU stock levels, trigger automated low-stock warnings, and manually adjust variances on the fly.</p>
    </div>
  </section>
  
  <footer class="footer">
    <p>Built with ❤️ for high-performance retail. © 2026 Stash GO.</p>
  </footer>
</div>

<style>
  .landing-container {
    min-height: 100vh;
    background: var(--bg-app);
    color: var(--text-main);
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .navbar {
    width: 100%;
    max-width: 1200px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 24px 40px;
    box-sizing: border-box;
  }

  .logo {
    font-size: 22px;
    font-weight: 800;
    letter-spacing: -0.5px;
    display: flex;
    align-items: center;
    gap: 10px;
    color: var(--accent-primary);
  }

  .logo-icon {
    font-size: 20px;
    background: rgba(15, 90, 71, 0.08);
    padding: 6px 10px;
    border-radius: 10px;
    border: 1px solid rgba(15, 90, 71, 0.2);
  }

  .gradient-text {
    color: var(--accent-mint);
  }

  .nav-links {
    display: flex;
    align-items: center;
    gap: 16px;
  }

  .nav-link {
    background: transparent;
    border: none;
    color: var(--text-muted);
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: color 0.2s ease;
  }

  .nav-link:hover {
    color: var(--accent-primary);
  }

  .nav-launch-btn {
    background: var(--accent-primary);
    color: #ffffff;
    border: none;
    padding: 8px 20px;
    border-radius: 20px;
    cursor: pointer;
    font-weight: 700;
    font-size: 14px;
    box-shadow: 0 4px 12px rgba(15, 90, 71, 0.25);
    transition: transform 0.2s ease, background 0.2s ease;
  }

  .nav-launch-btn:hover {
    background: var(--accent-primary-hover);
    transform: translateY(-1px);
  }

  .hero-section {
    text-align: center;
    padding: 70px 20px;
    max-width: 860px;
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .badge-pill-live {
    background: rgba(16, 185, 129, 0.12);
    border: 1px solid rgba(16, 185, 129, 0.3);
    color: #047857;
    padding: 6px 16px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
    margin-bottom: 24px;
    letter-spacing: 0.5px;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .pulse-dot {
    width: 8px;
    height: 8px;
    background: var(--accent-success);
    border-radius: 50%;
    box-shadow: 0 0 6px var(--accent-success);
  }

  .headline {
    font-size: 52px;
    font-weight: 800;
    line-height: 1.15;
    margin: 0 0 24px 0;
    color: var(--text-main);
    letter-spacing: -1px;
  }

  .subtitle {
    font-size: 18px;
    color: var(--text-muted);
    line-height: 1.6;
    margin: 0 0 40px 0;
    max-width: 660px;
  }

  .hero-actions {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
    justify-content: center;
  }

  .btn-primary {
    background: var(--accent-primary);
    color: #ffffff;
    border: none;
    padding: 14px 28px;
    border-radius: 20px;
    font-size: 15px;
    font-weight: 700;
    cursor: pointer;
    box-shadow: 0 4px 15px rgba(15, 90, 71, 0.3);
    transition: transform 0.2s ease, background 0.2s ease;
  }

  .btn-primary:hover {
    background: var(--accent-primary-hover);
    transform: translateY(-2px);
  }

  .btn-secondary {
    background: var(--bg-card);
    color: var(--text-main);
    border: 1px solid var(--border-solid);
    padding: 14px 24px;
    border-radius: 20px;
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    text-decoration: none;
    box-shadow: var(--shadow-sm);
  }

  .btn-secondary:hover {
    background: var(--bg-card-hover);
    border-color: var(--accent-primary);
    transform: translateY(-2px);
  }

  .tech-stack-banner {
    border-top: 1px dashed var(--border-light);
    border-bottom: 1px dashed var(--border-light);
    width: 100%;
    padding: 40px 20px;
    text-align: center;
    background: var(--bg-card);
  }

  .tech-title {
    font-size: 12px;
    color: var(--text-muted);
    font-weight: 700;
    letter-spacing: 2px;
    margin-bottom: 20px;
  }

  .tech-logos {
    display: flex;
    justify-content: center;
    gap: 16px;
    flex-wrap: wrap;
  }

  .tech-badge {
    padding: 8px 18px;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 700;
    background: var(--bg-card-hover);
    border: 1px solid var(--border-light);
  }

  .svelte { color: #e03100; }
  .python { color: #047857; }
  .postgres { color: #0284c7; }
  .docker { color: #0d9488; }

  .features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 24px;
    max-width: 1200px;
    width: 100%;
    padding: 70px 40px;
    box-sizing: border-box;
  }

  .feature-card {
    background: #ffffff;
    border: 1px solid var(--border-light);
    padding: 32px;
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-sm);
    transition: all 0.3s ease;
  }

  .feature-card:hover {
    transform: translateY(-4px);
    border-color: var(--accent-primary);
    box-shadow: var(--shadow-md);
  }

  .feature-icon {
    font-size: 32px;
    margin-bottom: 20px;
  }

  .feature-card h3 {
    color: var(--text-main);
    font-size: 20px;
    margin: 0 0 12px 0;
  }

  .feature-card p {
    color: var(--text-muted);
    font-size: 15px;
    line-height: 1.6;
    margin: 0;
  }

  .footer {
    padding: 40px;
    color: var(--text-muted);
    font-size: 13px;
    text-align: center;
  }

  .text-cyan { color: var(--accent-secondary); }
  .text-green { color: #047857; }
  .text-purple { color: var(--accent-purple); }
  .text-amber { color: var(--accent-warning); }
</style>