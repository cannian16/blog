<script lang="ts">
  let { children } = $props(); 
  import { Accordion, Avatar, DropdownMenu } from "bits-ui";
  import NavGroup from '$lib/components/NavGroup.svelte';
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";
  import { api } from "$lib/api/client";

  let user = $state({
    name: "",
    avatar: "",
    isLoaded: false
  });
  interface User {
    username: string;
    avatar_url: string;
    role: string;
  }

  async function checkAuth() {
    try {
      // 请求后端接口：验证 Token 并获取 Profile
      const data = await api.get<User>('/auth/me'); 
      
      // 校验通过，填充用户信息
      user.name = data.username;
      user.avatar = data.avatar_url;
      user.isLoaded = true;
    } catch (err) {
      // 校验失败 
      console.error("鉴权失效:", err);
      localStorage.removeItem('jwt_token');
      goto('/login', { replaceState: true });
    }
  }
  onMount(() => {
    checkAuth();
  });

  function handleLogout() {
    localStorage.removeItem('jwt_token');
    goto('/login', { replaceState: true });
  }
</script>

<div class="flex min-h-screen">
  <aside class="w-64 bg-white border-r border-gray-200 p-4 hidden md:block">
    <h2 class="text-xl font-bold mb-6">博客后台</h2>
    <Accordion.Root type="single">
      <NavGroup title="音乐" value="songs" basePath="/songs" />
      <NavGroup title="工具" value="tools" basePath="/tools" />
      <NavGroup title="技术栈" value="skills" basePath="/skills" />
      <NavGroup title="友链" value="links" basePath="/links" />
    </Accordion.Root>
    <DropdownMenu.Root>
      <DropdownMenu.Trigger class="outline-none">
        <Avatar.Root
          delayMs={200}
          class="h-12 w-12 rounded-full border border-gray-200 transition-transform hover:scale-105 active:scale-95 shadow-sm"
        >
          <div class="flex h-full w-full items-center justify-center overflow-hidden rounded-full border-2 border-transparent">
            <Avatar.Image src={user.avatar} alt={user.name} />
            <Avatar.Fallback class="bg-indigo-500 text-white flex items-center justify-center w-full h-full text-sm">
              {user.name?.slice(0, 2).toUpperCase() || 'AD'}
            </Avatar.Fallback>
          </div>
        </Avatar.Root>
      </DropdownMenu.Trigger>

      <DropdownMenu.Content 
        class="w-48 bg-white rounded-xl border border-gray-100 shadow-xl p-1 mt-2 z-50 focus:outline-none"
        align="end"
      >
        <div class="px-3 py-2 border-b border-gray-50 mb-1">
          <p class="text-xs text-gray-400">当前登录</p>
          <p class="text-sm font-semibold text-gray-700 truncate">{user.name}</p>
        </div>
        <DropdownMenu.Item 
          onclick={handleLogout}
          class="flex items-center px-3 py-2 text-sm text-red-500 rounded-lg hover:bg-red-50 cursor-pointer outline-none transition-colors mt-1 font-medium"
        >
          退出登录
        </DropdownMenu.Item>
      </DropdownMenu.Content>
    </DropdownMenu.Root>
  </aside>

  <main class="flex-1 p-8">
    {@render children()}
  </main>
</div>