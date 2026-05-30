<script lang="ts">
  // This prop will let you switch from the Landing Page to your Dashboard
  export let launchApp: () => void = () => console.log("Routing to app...");
</script>

<div class="landing-container animate-fade-in" id="home">
  <nav class="navbar">
    <div class="logo">
      <span class="logo-icon">📦</span> Stash <span class="text-cyan">GO</span>
    </div>
    
    <div class="nav-links">
      <button class="nav-link">Home</button>
      <button class="nav-link" on:click={launchApp}>Login / Sign Up</button>
      <!-- <button class="nav-launch-btn" on:click={launchApp}>Sign Up →</button> -->
    </div>
  </nav>

  <header class="hero-section">
    <div class="badge">v1.0 is Live</div>
    <h1 class="headline">
      Next-Gen Inventory & POS <br />
      <span class="text-cyan">For Modern Businesses.</span>
    </h1>
    <p class="subtitle">
      Seamlessly manage sales, track inventory, and generate beautiful invoices with a lightning-fast digital terminal built for speed.
    </p>
    <div class="hero-actions">
      <button class="btn-primary" on:click={launchApp}>Launch Terminal</button>
      <a href="https://github.com/Abhyudit22/Stash-Go" target="_blank" class="btn-secondary">View Source Code</a>
    </div>
  </header>

  <div class="tech-stack-banner">
    <p class="tech-title">ENGINEERED WITH A MODERN STACK</p>
    <div class="tech-logos">
      <span class="tech-badge svelte">Svelte & Vite</span>
      <span class="tech-badge python">FastAPI</span>
      <span class="tech-badge postgres">PostgreSQL</span>
      <span class="tech-badge docker">Docker</span>
    </div>
  </div>

  <section class="features-grid">
    <div class="feature-card">
      <div class="feature-icon text-cyan">⚡</div>
      <h3>Digital Terminal</h3>
      <p>Lightning-fast checkout system with dynamic tax and discount modifiers. Built for zero latency.</p>
    </div>
    
    <div class="feature-card">
      <div class="feature-icon text-green">🧾</div>
      <h3>Invoice Ledger</h3>
      <p>Audit and manage historical sales data securely in a highly organized matrix view.</p>
    </div>
    
    <div class="feature-card">
      <div class="feature-icon text-red">📊</div>
      <h3>Live Analytics</h3>
      <p>Real-time custom SVG charts tracking revenue, operational profit margins, and payment distribution.</p>
    </div>
  </section>
  
  <footer class="footer">
    <p>Built with ❤️ for the web. © 2026 Stash GO.</p>
  </footer>
</div>

<style>
  .landing-container {
    min-height: 100vh;
    background: #121214;
    color: #e1e1e6;
    font-family: system-ui, -apple-system, sans-serif;
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
    padding: 20px 40px;
    box-sizing: border-box;
  }
  .logo { font-size: 20px; font-weight: bold; letter-spacing: 1px; display: flex; align-items: center; gap: 8px; }
  .logo-icon { font-size: 24px; }
  

  .nav-links { display: flex; align-items: center; gap: 24px; }
  .nav-link { background: transparent; border: none; color: #a1a1aa; font-size: 15px; font-weight: 500; cursor: pointer; transition: 0.2s; padding: 0; }
  .nav-link:hover { color: #ffffff; }
  
  .nav-launch-btn { background: transparent; border: 1px solid #292933; color: #a1a1aa; padding: 8px 16px; border-radius: 6px; cursor: pointer; transition: 0.2s; font-weight: 500; margin-left: 8px; }
  .nav-launch-btn:hover { background: #292933; color: #ffffff; }


  .hero-section {
    text-align: center;
    padding: 80px 20px;
    max-width: 800px;
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  .badge { background: rgba(0, 188, 212, 0.1); border: 1px solid rgba(0, 188, 212, 0.2); color: #00bcd4; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; margin-bottom: 24px; letter-spacing: 1px; text-transform: uppercase; }
  .headline { font-size: 56px; font-weight: 800; line-height: 1.1; margin: 0 0 24px 0; color: #ffffff; }
  .subtitle { font-size: 18px; color: #a1a1aa; line-height: 1.6; margin: 0 0 40px 0; max-width: 600px; }
  
  .hero-actions { display: flex; gap: 16px; }
  .btn-primary { background: #00bcd4; color: #121214; border: none; padding: 14px 28px; border-radius: 6px; font-size: 15px; font-weight: bold; cursor: pointer; transition: 0.2s; }
  .btn-primary:hover { background: #0097a7; transform: translateY(-2px); }
  .btn-secondary { background: #202028; color: #ffffff; border: 1px solid #292933; padding: 14px 28px; border-radius: 6px; font-size: 15px; font-weight: 600; cursor: pointer; transition: 0.2s; text-decoration: none; }
  .btn-secondary:hover { background: #292933; transform: translateY(-2px); }

  .tech-stack-banner { border-top: 1px dashed #292933; border-bottom: 1px dashed #292933; width: 100%; padding: 40px 20px; text-align: center; background: #15151a; }
  .tech-title { font-size: 12px; color: #7c7c8a; font-weight: 600; letter-spacing: 2px; margin-bottom: 20px; }
  .tech-logos { display: flex; justify-content: center; gap: 16px; flex-wrap: wrap; }
  .tech-badge { padding: 8px 16px; border-radius: 6px; font-size: 14px; font-weight: 600; background: #1a1a21; border: 1px solid #292933; }
  .svelte { color: #ff3e00; }
  .python { color: #4caf50; }
  .postgres { color: #336791; }
  .docker { color: #0db7ed; }

  .features-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 24px; max-width: 1200px; width: 100%; padding: 80px 40px; box-sizing: border-box; }
  .feature-card { background: #1a1a21; border: 1px solid #292933; padding: 32px; border-radius: 12px; transition: 0.3s; }
  .feature-card:hover { transform: translateY(-5px); border-color: #3a3a47; }
  .feature-icon { font-size: 32px; margin-bottom: 20px; }
  .feature-card h3 { color: #ffffff; font-size: 20px; margin: 0 0 12px 0; }
  .feature-card p { color: #a1a1aa; font-size: 15px; line-height: 1.5; margin: 0; }


  .footer { padding: 40px; color: #7c7c8a; font-size: 13px; text-align: center; }
  .text-cyan { color: #00bcd4; }
  .text-green { color: #4caf50; }
  .text-red { color: #ff5252; }
  
  .animate-fade-in { animation: fadeIn 0.4s ease-out; }
  @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>