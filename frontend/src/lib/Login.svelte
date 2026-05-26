<script lang="ts">
  
  let username = "";
  let password = "";
  let errorMessage = "";
  let isLoading = false;

  const Base_URL = "http://127.0.0.1:8000";

 
  export let onLoginSuccess: () => void; 

  async function handleLogin() {
    errorMessage = "";
    isLoading = true;

    try {
      const formData = new URLSearchParams();
      formData.append("username", username);
      formData.append("password", password);

      const response = await fetch(`${Base_URL}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Invalid username or password");
      }

      const data = await response.json();
      localStorage.setItem("token", data.access_token);

      // 3. Call the prop function directly like a standard function!
      onLoginSuccess();
      
    } catch (error: any) {
      errorMessage = error.message || "Something went wrong.";
    } finally {
      isLoading = false;
    }
  }
</script>
<div class="login-container">
  <h2>Shopkeeper Login</h2>
  
  <form on:submit|preventDefault={handleLogin}>
    <div class="input-group">
      <label for="username">Username</label>
      <input 
        type="text" 
        id="username" 
        bind:value={username} 
        required 
        placeholder="Enter your username"
      />
    </div>

    <div class="input-group">
      <label for="password">Password</label>
      <input 
        type="password" 
        id="password" 
        bind:value={password} 
        required 
        placeholder="Enter your password"
      />
    </div>

    {#if errorMessage}
      <p class="error">{errorMessage}</p>
    {/if}

    <button type="submit" disabled={isLoading}>
      {isLoading ? "Logging in..." : "Login"}
    </button>
  </form>
</div>

<style>
  .login-container {
    max-width: 400px;
    margin: 100px auto;
    padding: 30px;
    background: #1e1e24;
    border-radius: 8px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.4);
    color: white;
    font-family: sans-serif;
  }
  h2 {
    text-align: center;
    margin-bottom: 24px;
    color: #00bcd4;
  }
  .input-group {
    margin-bottom: 20px;
  }
  label {
    display: block;
    margin-bottom: 8px;
    font-size: 14px;
    color: #b0bec5;
  }
  input {
    width: 100%;
    padding: 12px;
    border: 1px solid #333;
    border-radius: 4px;
    background: #2a2a35;
    color: white;
    box-sizing: border-box;
    font-size: 14px;
  }
  input:focus {
    outline: none;
    border-color: #00bcd4;
  }
  button {
    width: 100%;
    padding: 12px;
    background: #00bcd4;
    color: #121214;
    border: none;
    border-radius: 4px;
    font-weight: bold;
    cursor: pointer;
    font-size: 16px;
    transition: background 0.2s;
    margin-top: 10px;
  }
  button:hover:not(:disabled) {
    background: #0097a7;
  }
  button:disabled {
    background: #555;
    color: #aaa;
    cursor: not-allowed;
  }
  .error {
    color: #ff5252;
    font-size: 14px;
    margin-bottom: 16px;
    text-align: center;
    background: rgba(255, 82, 82, 0.1);
    padding: 8px;
    border-radius: 4px;
  }
</style>