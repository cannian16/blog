<script lang="ts">
    interface Link {
        id: number;
        name: string;
        url: string;
        icon: string;
        description: string;
    }
    import { onMount } from 'svelte';
    import { api } from '$lib/api/client';
    import LinkModal from '$lib/components/links/LinkModal.svelte';
    let links = $state<Link[]>([]);
    let isLoading = $state(true);
    let message = $state("");

    // 1. 查：初始化获取数据
    onMount(async () => {
        try {
            links = await api.get<Link[]>('/links/get');
        } catch (err) {
            alert('获取失败: ' + err);
        } finally {
            isLoading = false;
        }
    });
    async function deleteLink(id: number) {
        if (!confirm('确定删除这个链接吗？')) return;
        try {
			const response = await api.post('/links/delete', {id});
            console.log('删除成功:', response);
            links = links.filter(l => l.id !== id);
		} catch (err) {
			message = "发生错误: " + err;
		} finally {
			isLoading = false;
		}
    }
</script>

<div class="p-6 bg-gray-50 min-h-screen">
    <div class="max-w-4xl mx-auto">
        <header class="flex justify-between items-center mb-8">
            <h1 class="text-2xl font-bold text-gray-800">友链管理</h1>
            <button class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition">
                + 新增链接
            </button>
        </header>

        {#if isLoading}
            <p class="text-center text-gray-500">加载中...</p>
        {:else}
            <div class="grid grid-cols-1 gap-4">
                <div class="grid grid-cols-[120px_180px_200px_1fr_100px] gap-4 p-3 bg-gray-100 text-xs font-bold text-gray-500 uppercase tracking-wider rounded-t-lg">
                    <div>名称</div>
                    <div>链接地址</div>
                    <div>图标路径</div>
                    <div>描述</div>
                    <div class="text-right">操作</div>
                </div>
                {#each links as link (link.id)}
                    <div class="group grid grid-cols-[120px_180px_200px_1fr_100px] items-center gap-x-6 p-3 bg-white border-b border-gray-100 hover:bg-indigo-50/30 transition text-sm">
                    
                        <div class="font-bold text-gray-800 truncate" title={link.name}>
                            {link.name}
                        </div>
                    
                        <div class="text-blue-500 truncate font-mono text-xs" title={link.url}>
                            <a href={link.url}>{link.url}</a>
                        </div>
                    
                        <div class="text-gray-400 truncate text-xs italic" title={link.icon}>
                            <a href={link.icon}>{link.icon}</a>
                        </div>
                    
                        <div class="text-gray-500 truncate" title={link.description}>
                            {link.description || '暂无描述'}
                        </div>
                    
                        <div class="flex justify-end gap-4 opacity-0 group-hover:opacity-100 transition shrink-0">
                            <button class="text-indigo-600 hover:font-bold transition-all">编辑</button>
                            <button 
                                onclick={() => deleteLink(link.id)} 
                                class="text-red-500 hover:font-bold transition-all"
                            >
                                删除
                            </button>
                        </div>
                    </div>
                {/each}
            </div>
        {/if}
    </div>
</div>