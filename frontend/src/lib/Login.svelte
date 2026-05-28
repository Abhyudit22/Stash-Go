<script lang="ts">
  import { onMount } from 'svelte';

  // State Management
  let mode: 'login' | 'signup' = 'login';
  let username = "";
  let email = ""; // Only used for Sign Up
  let password = "";
  let errorMessage = "";
  let isLoading = false;
  let showPassword = false;
  let rememberMe = false;

  const Base_URL = "http://127.0.0.1:8000";

  export let onLoginSuccess: () => void; 

  async function handleSubmit() {
    errorMessage = "";
    isLoading = true;

    try {
      if (mode === 'login') {
        const formData = new URLSearchParams();
        formData.append("username", username);
        formData.append("password", password);

        const response = await fetch(`${Base_URL}/auth/login`, {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body: formData,
        });

        if (!response.ok) throw new Error("Invalid username or password credentials.");

        const data = await response.json();
        localStorage.setItem("token", data.access_token);
        
        if (rememberMe) localStorage.setItem("stashgo_user", username);
        else localStorage.removeItem("stashgo_user");

        onLoginSuccess();

      } else {
        const response = await fetch(`${Base_URL}/auth/signup`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username, email, password }),
        });

        if (!response.ok) {
          const errData = await response.json();
          throw new Error(errData.detail || "Registration failed. Username may be taken.");
        }

        mode = 'login';
        errorMessage = "Account created successfully! Please log in.";
      }
      
    } catch (error: any) {
      errorMessage = error.message || "Connection to backend failed.";
    } finally {
      isLoading = false;
    }
  }

  function toggleMode() {
    mode = mode === 'login' ? 'signup' : 'login';
    errorMessage = ""; 
    password = ""; 
  }

  onMount(() => {
    const savedUser = localStorage.getItem("stashgo_user");
    if (savedUser) {
      username = savedUser;
      rememberMe = true;
    }
  });
</script>

<div class="login-wrapper">
  <div class="login-container animate-fade-in-up">
    <div class="brand-header">
      <div class="logo-icon animate-pulse-glow">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
          <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
          <line x1="12" y1="22.08" x2="12" y2="12"></line>
        </svg>
      </div>
      <h2>{mode === 'login' ? 'Welcome Back' : 'Create Account'}</h2>
      <p class="subtitle">{mode === 'login' ? 'Secure Shopkeeper Terminal' : 'Register for Stash GO'}</p>
    </div>
    
    <form on:submit|preventDefault={handleSubmit}>
      
      <div class="input-group">
        <label for="username">Username</label>
        <div class="input-wrapper">
          <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
          <input type="text" id="username" bind:value={username} required placeholder="e.g., admin" autocomplete="username"/>
        </div>
      </div>

      {#if mode === 'signup'}
        <div class="input-group animate-slide-down">
          <label for="email">Email Address</label>
          <div class="input-wrapper">
            <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg>
            <input type="email" id="email" bind:value={email} required placeholder="store@example.com" autocomplete="email"/>
          </div>
        </div>
      {/if}

      <div class="input-group">
        <label for="password">Password</label>
        <div class="input-wrapper">
          <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
          <input type={showPassword ? "text" : "password"} id="password" bind:value={password} required placeholder="••••••••" autocomplete={mode === 'login' ? 'current-password' : 'new-password'}/>
          <button type="button" class="toggle-password" on:click={() => showPassword = !showPassword} tabindex="-1">
            {#if showPassword}
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>
            {:else}
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
            {/if}
          </button>
        </div>
      </div>

      {#if mode === 'login'}
        <div class="form-options">
          <label class="remember-me">
            <input type="checkbox" bind:checked={rememberMe} />
            <span>Remember me</span>
          </label>
          <button type="button" class="forgot-link" on:click|preventDefault>Forgot password?</button>
        </div>
      {/if}

      {#if errorMessage}
        <div class="error-box animate-slide-down" style={errorMessage.includes('successfully') ? 'color: #4caf50; background: rgba(76, 175, 80, 0.1); border-color: rgba(76, 175, 80, 0.3); box-shadow: 0 4px 12px rgba(76, 175, 80, 0.15);' : ''}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
          <p>{errorMessage}</p>
        </div>
      {/if}

      <button type="submit" class="btn-submit" disabled={isLoading}>
        {#if isLoading}
          <svg class="spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><path d="M21 12a9 9 0 1 1-6.219-8.56"></path></svg>
          {mode === 'login' ? 'Authenticating...' : 'Registering...'}
        {:else}
          {mode === 'login' ? 'Secure Login' : 'Create Account'}
        {/if}
      </button>
    </form>

    <div class="toggle-mode">
      {#if mode === 'login'}
        Don't have an account? <button type="button" class="link-btn" on:click={toggleMode}>Sign up</button>
      {:else}
        Already have an account? <button type="button" class="link-btn" on:click={toggleMode}>Log in</button>
      {/if}
    </div>

  </div>
</div>

<style>
  /* 1. Full-screen modern grid background */
  .login-wrapper { 
    display: flex; 
    justify-content: center; 
    align-items: center; 
    min-height: 100vh;
    background-color: #0b0b0e;
    background-image: 
      radial-gradient(at 0% 0%, rgba(0, 188, 212, 0.15) 0px, transparent 50%),
      radial-gradient(at 100% 100%, rgba(0, 188, 212, 0.05) 0px, transparent 50%),
      linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
    background-size: 100% 100%, 100% 100%, 32px 32px, 32px 32px;
  }

  /* 2. Glassmorphism Card */
  .login-container { 
    width: 100%; 
    max-width: 420px; 
    padding: 40px; 
    background: rgba(30, 30, 36, 0.65); 
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.08); 
    border-radius: 16px; 
    box-shadow: 0 24px 40px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1); 
    color: white; 
  }
  
  .brand-header { text-align: center; margin-bottom: 32px; }
  
  /* 3. Logo Glow Animation */
  .logo-icon { 
    width: 52px; 
    height: 52px; 
    margin: 0 auto 16px; 
    color: #00bcd4; 
    background: rgba(0, 188, 212, 0.1); 
    padding: 12px; 
    border-radius: 14px;
    border: 1px solid rgba(0, 188, 212, 0.2);
  }
  
  h2 { margin: 0 0 6px 0; font-size: 26px; font-weight: 700; letter-spacing: 0.5px; }
  .subtitle { margin: 0; font-size: 13px; color: #8e8e9a; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600; }

  .input-group { margin-bottom: 22px; }
  .input-group label { display: block; margin-bottom: 8px; font-size: 13px; font-weight: 600; color: #a1a1aa; transition: color 0.2s; }
  .input-group:focus-within label { color: #00bcd4; } /* Highlights label when typing */
  
  .input-wrapper { position: relative; display: flex; align-items: center; }
  .input-icon { position: absolute; left: 14px; width: 18px; height: 18px; color: #7c7c8a; transition: color 0.2s; pointer-events: none; }
  .input-group:focus-within .input-icon { color: #00bcd4; } /* Highlights icon when typing */
  
  /* 4. Enhanced Input Fields */
  input { 
    width: 100%; 
    padding: 14px 14px 14px 44px; 
    border: 1px solid rgba(255, 255, 255, 0.1); 
    border-radius: 10px; 
    background: rgba(15, 15, 18, 0.6); 
    color: white; 
    font-size: 15px; 
    transition: all 0.3s ease; 
  }
  input:focus { 
    outline: none; 
    border-color: #00bcd4; 
    background: rgba(15, 15, 18, 0.9);
    box-shadow: 0 0 0 4px rgba(0, 188, 212, 0.15), inset 0 1px 2px rgba(0,0,0,0.2); 
  }
  
  .toggle-password { position: absolute; right: 14px; background: none; border: none; padding: 0; color: #7c7c8a; cursor: pointer; display: flex; align-items: center; transition: color 0.2s; }
  .toggle-password:hover { color: #00bcd4; }
  .toggle-password svg { width: 18px; height: 18px; }

  .form-options { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; font-size: 13px; }
  .remember-me { display: flex; align-items: center; gap: 8px; color: #a1a1aa; cursor: pointer; margin: 0; transition: color 0.2s; }
  .remember-me:hover { color: #e1e1e6; }
  .remember-me input { width: 16px; height: 16px; margin: 0; accent-color: #00bcd4; cursor: pointer; }
  
  .forgot-link, .link-btn { background: none; border: none; padding: 0; font: inherit; font-size: 13px; color: #00bcd4; cursor: pointer; text-decoration: none; transition: all 0.2s; }
  .forgot-link:hover, .link-btn:hover { color: #00e5ff; text-shadow: 0 0 8px rgba(0, 188, 212, 0.4); }

  /* 5. Glowing Submit Button */
  .btn-submit { 
    width: 100%; 
    padding: 14px; 
    background: linear-gradient(135deg, #00bcd4 0%, #00838f 100%); 
    color: #ffffff; 
    border: none; 
    border-radius: 10px; 
    font-weight: 700; 
    letter-spacing: 0.5px;
    cursor: pointer; 
    font-size: 15px; 
    transition: all 0.3s ease; 
    display: flex; 
    justify-content: center; 
    align-items: center; 
    gap: 8px; 
    box-shadow: 0 4px 15px rgba(0, 188, 212, 0.3);
  }
  .btn-submit:hover:not(:disabled) { 
    transform: translateY(-2px); 
    box-shadow: 0 8px 25px rgba(0, 188, 212, 0.5);
    filter: brightness(1.1);
  }
  .btn-submit:active:not(:disabled) {
    transform: translateY(1px);
    box-shadow: 0 2px 10px rgba(0, 188, 212, 0.4);
  }
  .btn-submit:disabled { background: #2a2a35; color: #7c7c8a; box-shadow: none; cursor: not-allowed; }

  .toggle-mode { text-align: center; font-size: 13px; color: #a1a1aa; margin-top: 28px; padding-top: 24px; border-top: 1px solid rgba(255,255,255,0.05); }

  .spinner { width: 18px; height: 18px; animation: spin 1s linear infinite; }
  
  .error-box { display: flex; align-items: center; gap: 12px; color: #ff5252; background: rgba(255, 82, 82, 0.1); border: 1px solid rgba(255, 82, 82, 0.2); padding: 14px; border-radius: 10px; margin-bottom: 24px; box-shadow: 0 4px 12px rgba(255, 82, 82, 0.1); }
  .error-box svg { width: 20px; height: 20px; flex-shrink: 0; }
  .error-box p { margin: 0; font-size: 13px; font-weight: 500; line-height: 1.4; }

  /* Smooth Animations */
  @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
  
  .animate-fade-in-up { animation: fadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
  .animate-slide-down { animation: slideDown 0.3s ease-out forwards; }
  
  .animate-pulse-glow { animation: pulseGlow 3s infinite alternate ease-in-out; }

  @keyframes fadeInUp { 
    from { opacity: 0; transform: translateY(20px); } 
    to { opacity: 1; transform: translateY(0); } 
  }
  
  @keyframes slideDown { 
    from { opacity: 0; transform: translateY(-10px); } 
    to { opacity: 1; transform: translateY(0); } 
  }

  @keyframes pulseGlow {
    0% { box-shadow: 0 0 0 0 rgba(0, 188, 212, 0.4); }
    100% { box-shadow: 0 0 20px 5px rgba(0, 188, 212, 0.1); }
  }
</style>