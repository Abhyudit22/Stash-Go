<script lang="ts">
  import { onMount } from 'svelte';

  // State Management
  let mode: 'login' | 'signup' | 'forgot' = 'login';
  let username = "";
  let email = ""; // Used for Sign Up & Forgot Password
  let password = "";
  let errorMessage = "";
  let isLoading = false;
  let showPassword = false;
  let rememberMe = false;
  import { Base_URL } from "./api";

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

        if (response.status === 429) {
          const errData = await response.json().catch(() => ({}));
          throw new Error(errData.detail || "Too many attempts. Please wait 60 seconds.");
        }

        if (!response.ok) throw new Error("Invalid username or password credentials.");

        const data = await response.json();
        localStorage.setItem("token", data.access_token);
        
        if (rememberMe) localStorage.setItem("stashgo_user", username);
        else localStorage.removeItem("stashgo_user");

        onLoginSuccess();

      } else if (mode === 'signup') {
        const response = await fetch(`${Base_URL}/auth/signup`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username, email, password }),
        });

        if (response.status === 429) {
          const errData = await response.json().catch(() => ({}));
          throw new Error(errData.detail || "Too many attempts. Please wait 60 seconds.");
        }

        if (!response.ok) {
          const errData = await response.json();
          throw new Error(errData.detail || "Registration failed. Username or email may be taken.");
        }

        mode = 'login';
        errorMessage = "Account created successfully! Please log in.";

      } else if (mode === 'forgot') {
        const response = await fetch(`${Base_URL}/auth/forgot-password`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: email.trim(), new_password: password }),
        });

        if (response.status === 429) {
          const errData = await response.json().catch(() => ({}));
          throw new Error(errData.detail || "Too many attempts. Please wait 60 seconds.");
        }

        if (!response.ok) {
          const errData = await response.json();
          throw new Error(errData.detail || "Password reset failed. Please check your email or username.");
        }

        const data = await response.json();
        if (data.username) {
          username = data.username;
        }

        mode = 'login';
        errorMessage = "Password reset successfully! You can now log in with your new password.";
      }
      
    } catch (error: any) {
      errorMessage = error.message || "Connection to backend failed.";
    } finally {
      isLoading = false;
    }
  }

  function toggleMode(targetMode: 'login' | 'signup' | 'forgot') {
    mode = targetMode;
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
      <h2>
        {#if mode === 'login'}Welcome Back
        {:else if mode === 'signup'}Create Account
        {:else}Reset Password
        {/if}
      </h2>
      <p class="subtitle">
        {#if mode === 'login'}Secure Shopkeeper Terminal
        {:else if mode === 'signup'}Register for Stash GO
        {:else}Enter account email/username & new password
        {/if}
      </p>
    </div>
    
    <form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }}>
      
      {#if mode === 'login'}
        <div class="input-group">
          <label for="username">Username</label>
          <div class="input-wrapper">
            <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
            <input type="text" id="username" bind:value={username} required placeholder="e.g., admin" autocomplete="username"/>
          </div>
        </div>
      {/if}

      {#if mode === 'signup' || mode === 'forgot'}
        <div class="input-group animate-slide-down">
          <label for="email">{mode === 'forgot' ? 'Email or Username' : 'Email Address'}</label>
          <div class="input-wrapper">
            <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              {#if mode === 'forgot'}
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle>
              {:else}
                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline>
              {/if}
            </svg>
            <input
              type={mode === 'forgot' ? "text" : "email"}
              id="email"
              bind:value={email}
              required
              placeholder={mode === 'forgot' ? "store@example.com or admin" : "store@example.com"}
              autocomplete={mode === 'forgot' ? "username" : "email"}
            />
          </div>
        </div>
      {/if}

      {#if mode === 'signup'}
        <div class="input-group animate-slide-down">
          <label for="username">Username</label>
          <div class="input-wrapper">
            <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
            <input type="text" id="username" bind:value={username} required placeholder="e.g., admin" autocomplete="username"/>
          </div>
        </div>
      {/if}

      <div class="input-group">
        <label for="password">{mode === 'forgot' ? 'New Password' : 'Password'}</label>
        <div class="input-wrapper">
          <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
          <input type={showPassword ? "text" : "password"} id="password" bind:value={password} required placeholder="••••••••" autocomplete={mode === 'login' ? 'current-password' : 'new-password'}/>
          <button type="button" class="toggle-password" onclick={() => showPassword = !showPassword} tabindex="-1">
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
          <button type="button" class="forgot-link" onclick={() => toggleMode('forgot')}>Forgot password?</button>
        </div>
      {/if}

      {#if errorMessage}
        <div class="error-box animate-slide-down" style={errorMessage.includes('successfully') ? 'color: var(--accent-success); background: rgba(16, 185, 129, 0.12); border-color: rgba(16, 185, 129, 0.3);' : ''}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
          <p>{errorMessage}</p>
        </div>
      {/if}

      <button type="submit" class="btn-submit" disabled={isLoading}>
        {#if isLoading}
          <svg class="spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><path d="M21 12a9 9 0 1 1-6.219-8.56"></path></svg>
          {#if mode === 'login'}Authenticating...
          {:else if mode === 'signup'}Registering...
          {:else}Resetting Password...
          {/if}
        {:else}
          {#if mode === 'login'}Secure Login
          {:else if mode === 'signup'}Create Account
          {:else}Update Password
          {/if}
        {/if}
      </button>
    </form>

    <div class="toggle-mode">
      {#if mode === 'login'}
        Don't have an account? <button type="button" class="link-btn" onclick={() => toggleMode('signup')}>Sign up</button>
      {:else if mode === 'signup'}
        Already have an account? <button type="button" class="link-btn" onclick={() => toggleMode('login')}>Log in</button>
      {:else}
        Remembered your password? <button type="button" class="link-btn" onclick={() => toggleMode('login')}>Log in</button>
      {/if}
    </div>

  </div>
</div>

<style>
  .login-wrapper { 
    display: flex; 
    justify-content: center; 
    align-items: center; 
    min-height: calc(100vh - 120px);
    background-color: var(--bg-app);
    background-image: 
      radial-gradient(at 0% 0%, rgba(15, 90, 71, 0.06) 0px, transparent 50%),
      radial-gradient(at 100% 100%, rgba(16, 185, 129, 0.06) 0px, transparent 50%);
  }

  .login-container { 
    width: 100%; 
    max-width: 420px; 
    padding: 40px; 
    background: var(--bg-card); 
    border: 1px solid var(--border-light); 
    border-radius: var(--radius-lg); 
    box-shadow: var(--shadow-lg); 
    color: var(--text-main); 
  }
  
  .brand-header { text-align: center; margin-bottom: 32px; }
  
  .logo-icon { 
    width: 52px; 
    height: 52px; 
    margin: 0 auto 16px; 
    color: var(--accent-primary); 
    background: rgba(15, 90, 71, 0.08); 
    padding: 12px; 
    border-radius: 16px;
    border: 1px solid rgba(15, 90, 71, 0.2);
  }
  
  h2 { margin: 0 0 6px 0; font-size: 26px; font-weight: 800; letter-spacing: -0.5px; color: var(--accent-primary); }
  .subtitle { margin: 0; font-size: 12px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1.5px; font-weight: 700; }

  .input-group { margin-bottom: 22px; }
  .input-group label { display: block; margin-bottom: 8px; font-size: 13px; font-weight: 600; color: var(--text-muted); transition: color 0.2s; }
  .input-group:focus-within label { color: var(--accent-primary); }
  
  .input-wrapper { position: relative; display: flex; align-items: center; }
  .input-icon { position: absolute; left: 14px; width: 18px; height: 18px; color: var(--text-muted); transition: color 0.2s; pointer-events: none; }
  .input-group:focus-within .input-icon { color: var(--accent-primary); }
  
  input { 
    width: 100%; 
    padding: 14px 44px 14px 44px; 
    border: 1px solid var(--border-solid); 
    border-radius: 10px; 
    background: #ffffff; 
    color: #0f172a !important; 
    font-size: 15px; 
    font-weight: 600;
    transition: all 0.25s ease; 
  }
  input:focus { 
    outline: none; 
    border-color: var(--accent-primary); 
    box-shadow: 0 0 0 3px rgba(15, 90, 71, 0.12); 
  }
  
  .toggle-password { position: absolute; right: 14px; background: none; border: none; padding: 0; color: var(--text-muted); cursor: pointer; display: flex; align-items: center; }
  .toggle-password:hover { color: var(--accent-primary); }
  .toggle-password svg { width: 18px; height: 18px; }

  .form-options { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; font-size: 13px; }
  .remember-me { display: flex; align-items: center; gap: 8px; color: var(--text-muted); cursor: pointer; margin: 0; }
  .remember-me:hover { color: var(--text-main); }
  .remember-me input { width: 16px; height: 16px; margin: 0; accent-color: var(--accent-primary); cursor: pointer; }
  
  .forgot-link, .link-btn { background: none; border: none; padding: 0; font: inherit; font-size: 13px; color: var(--accent-primary); cursor: pointer; text-decoration: none; font-weight: 600; }
  .forgot-link:hover, .link-btn:hover { color: var(--accent-mint); text-decoration: underline; }

  .btn-submit { 
    width: 100%; 
    padding: 14px; 
    background: linear-gradient(135deg, #0f5a47 0%, #0b4536 100%); 
    color: #ffffff; 
    border: none; 
    border-radius: 10px; 
    font-weight: 700; 
    letter-spacing: 0.5px;
    cursor: pointer; 
    font-size: 15px; 
    transition: all 0.25s ease; 
    display: flex; 
    justify-content: center; 
    align-items: center; 
    gap: 8px; 
    box-shadow: 0 4px 12px rgba(15, 90, 71, 0.25);
  }
  .btn-submit:hover:not(:disabled) { 
    transform: translateY(-2px); 
    box-shadow: 0 6px 18px rgba(15, 90, 71, 0.35);
  }

  .toggle-mode { text-align: center; font-size: 13px; color: var(--text-muted); margin-top: 28px; padding-top: 24px; border-top: 1px solid var(--border-light); }
  .spinner { width: 18px; height: 18px; animation: spin 1s linear infinite; }
  
  .error-box { display: flex; align-items: center; gap: 12px; color: var(--accent-danger); background: rgba(225, 29, 72, 0.08); border: 1px solid rgba(225, 29, 72, 0.2); padding: 14px; border-radius: 10px; margin-bottom: 24px; }
  .error-box svg { width: 20px; height: 20px; flex-shrink: 0; }
  .error-box p { margin: 0; font-size: 13px; font-weight: 600; }

  @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
  .animate-fade-in-up { animation: fadeInUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
  .animate-slide-down { animation: slideDown 0.3s ease-out forwards; }
  .animate-pulse-glow { animation: pulseGlow 3s infinite alternate ease-in-out; }

  @keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
  @keyframes slideDown { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
  @keyframes pulseGlow { 0% { box-shadow: 0 0 0 0 rgba(15, 90, 71, 0.3); } 100% { box-shadow: 0 0 15px 3px rgba(15, 90, 71, 0.1); } }
</style>