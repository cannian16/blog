<script lang="ts">
// 响应式数据
let isLoading = $state(false);

import { goto } from "$app/navigation";
import { api } from "$lib/api/client";

let message = $state();

let user = $state({
	username: "",
	password: "",
});

interface LoginResponse {
	access_token: string;
	token_type: string;
}
async function handleSubmit(e: SubmitEvent) {
	e.preventDefault();
	isLoading = true;

	try {
		const form = new URLSearchParams({
			username: user.username,
			password: user.password,
		});
		const data = await api.postForm<LoginResponse>("/auth/login", form);
		if (data.access_token) {
			localStorage.setItem("jwt_token", data.access_token);
		}
		await goto("/", { replaceState: true });
	} catch (err) {
		message = err instanceof Error ? err.message : String(err);
	} finally {
		isLoading = false;
	}
}
</script>

<!-- <svelte:head>
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap" rel="stylesheet">
</svelte:head> -->

<style>
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Poppins', sans-serif;
  }
  
  :global(body) {
    overflow: hidden;
    min-height: 100vh;
  }
  
  .login-section {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background: linear-gradient(to bottom, #f1f4f9, #dff1ff);
    position: relative;
    overflow: hidden;
  }
  
  .color {
    position: absolute;
    filter: blur(150px);
    z-index: 1;
  }
  
  .color:nth-child(1) {
    top: -350px;
    width: 600px;
    height: 600px;
    background: #ff359b;
    animation: float1 20s infinite ease-in-out;
  }
  
  .color:nth-child(2) {
    bottom: -150px;
    left: 100px;
    width: 500px;
    height: 500px;
    background: #fffd87;
    animation: float2 25s infinite ease-in-out;
  }
  
  .color:nth-child(3) {
    bottom: 50px;
    right: 100px;
    width: 500px;
    height: 500px;
    background: #00d2ff;
    animation: float3 30s infinite ease-in-out;
  }
  
  @keyframes float1 {
    0%, 100% { transform: translate(0, 0) rotate(0deg); }
    33% { transform: translate(30px, -50px) rotate(120deg); }
    66% { transform: translate(-20px, 20px) rotate(240deg); }
  }
  
  @keyframes float2 {
    0%, 100% { transform: translate(0, 0) rotate(0deg); }
    33% { transform: translate(-40px, 30px) rotate(120deg); }
    66% { transform: translate(20px, -20px) rotate(240deg); }
  }
  
  @keyframes float3 {
    0%, 100% { transform: translate(0, 0) rotate(0deg); }
    33% { transform: translate(20px, 40px) rotate(120deg); }
    66% { transform: translate(-30px, -30px) rotate(240deg); }
  }
  
  .box {
    position: relative;
    z-index: 2;
  }
  
  .square {
    position: absolute;
    backdrop-filter: blur(5px);
    box-shadow: 0 25px 45px rgba(0, 0, 0, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.5);
    border-right: 1px solid rgba(255, 255, 255, 0.2);
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
    background: rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    animation: animate 10s linear infinite;
  }
  
  @keyframes animate {
    0%, 100% {
      transform: translateY(-40px);
    }
    50% {
      transform: translateY(40px);
    }
  }
  
  .square:nth-child(1) {
    top: -50px;
    right: -60px;
    width: 100px;
    height: 100px;
    animation-delay: 0s;
  }
  
  .square:nth-child(2) {
    top: 150px;
    left: -100px;
    width: 120px;
    height: 120px;
    z-index: 2;
    animation-delay: -2s;
  }
  
  .square:nth-child(3) {
    bottom: 50px;
    right: -60px;
    width: 80px;
    height: 80px;
    z-index: 2;
    animation-delay: -4s;
  }
  
  .square:nth-child(4) {
    bottom: -80px;
    left: 100px;
    width: 50px;
    height: 50px;
    animation-delay: -6s;
  }
  
  .square:nth-child(5) {
    top: -90px;
    left: 140px;
    width: 60px;
    height: 60px;
    animation-delay: -8s;
  }
  
  .container {
    position: relative;
    width: 400px;
    min-height: 400px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    display: flex;
    justify-content: center;
    align-items: center;
    backdrop-filter: blur(5px);
    box-shadow: 0 25px 45px rgba(0, 0, 0, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.5);
    border-right: 1px solid rgba(255, 255, 255, 0.2);
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
    z-index: 3;
  }
  
  .form {
    position: relative;
    height: 100%;
    width: 100%;
    padding: 40px;
  }
  
  .form h2 {
    position: relative;
    color: #fff;
    font-size: 24px;
    font-weight: 600;
    letter-spacing: 1px;
    margin-bottom: 40px;
  }
  
  .form h2::before {
    content: '';
    position: absolute;
    left: 0;
    bottom: -10px;
    width: 80px;
    height: 4px;
    background: #fff;
    border-radius: 2px;
  }
  
  .inputBox {
    width: 100%;
    margin-top: 20px;
  }
  
  .inputBox input {
    width: 100%;
    background: rgba(255, 255, 255, 0.2);
    border: none;
    outline: none;
    padding: 10px 20px;
    border-radius: 35px;
    border: 1px solid rgba(255, 255, 255, 0.5);
    border-right: 1px solid rgba(255, 255, 255, 0.2);
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
    font-size: 16px;
    letter-spacing: 1px;
    color: #fff;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
    transition: all 0.3s ease;
  }
  
  .inputBox input:hover {
    background: rgba(255, 255, 255, 0.25);
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
  }
  
  .inputBox input:focus {
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  }
  
  .inputBox input::placeholder {
    color: rgba(255, 255, 255, 0.8);
  }
  
  .inputBox input[type="submit"] {
    background: #fff;
    color: #666;
    max-width: 100px;
    cursor: pointer;
    margin-bottom: 20px;
    font-weight: 600;
    transition: all 0.3s ease;
  }
  
  .inputBox input[type="submit"]:hover {
    background: #f8f8f8;
    transform: translateY(-3px);
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
  }
  
  .inputBox input[type="submit"]:disabled {
    background: rgba(255, 255, 255, 0.5);
    color: rgba(102, 102, 102, 0.5);
    cursor: not-allowed;
    transform: none;
  }
  
  .forget {
    margin-top: 5px;
    color: #fff;
  }
  
  .forget a {
    color: #fff;
    font-weight: 600;
    text-decoration: none;
    transition: color 0.3s ease;
    position: relative;
  }
  
  .forget a:hover {
    color: #fffd87;
  }
  
  .forget a::after {
    content: '';
    position: absolute;
    width: 100%;
    height: 2px;
    background: #fffd87;
    bottom: -2px;
    left: 0;
    transform: scaleX(0);
    transform-origin: right;
    transition: transform 0.3s ease;
  }
  
  .forget a:hover::after {
    transform: scaleX(1);
    transform-origin: left;
  }
  
  
  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  .loading {
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 3px solid rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    border-top-color: #fff;
    animation: spin 1s ease-in-out infinite;
    margin-right: 10px;
    vertical-align: middle;
  }
  
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
</style>

<div class="login-section">
  <div class="color"></div>
  <div class="color"></div>
  <div class="color"></div>
  
  <div class="box">
    <div class="square"></div>
    <div class="square"></div>
    <div class="square"></div>
    <div class="square"></div>
    <div class="square"></div>
    
    <div class="container">
      <div class="form">
        <!-- 登录表单 -->
        <h2>登录表单</h2>
        <form onsubmit={handleSubmit}>
          <div class="inputBox">
            <input 
              type="text" 
              placeholder="用户名或邮箱"
              bind:value={user.username}
              required
              disabled={isLoading}
            >
          </div>
          
          <div class="inputBox">
            <input 
              type="password" 
              placeholder="密码"
              bind:value={user.password}
              required
              disabled={isLoading}
            >
          </div>
          
          <div class="inputBox">
            <input 
              type="submit" 
              value={isLoading ? '登录中...' : '登录'}
              disabled={isLoading || !user.username || !user.password}
            >
            {#if isLoading}
              <span class="loading"></span>
            {/if}
          </div>
          
          <p class="forget"><a href="register">注册</a></p>
        </form>
      </div>
    </div>
  </div>
</div>