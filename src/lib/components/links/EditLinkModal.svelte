<script lang="ts">
    import { fade, scale } from 'svelte/transition';
    import { api } from '$lib/api/client';

    // props: link 为当前选中的那条记录数据
    let { open = $bindable(false), link, onDone } = $props();

    // 本地编辑状态，防止直接修改父组件列表数据导致意外渲染
    let formData = $state({ id: 0, name: '', url: '', icon: '', description: '' });
    let isSubmitting = $state(false);

    // 关键：当父组件传入的 link 变化时，同步给本地 formData
    $effect(() => {
        if (link) formData = { ...link };
    });

    async function handleUpdate(e: Event) {
        e.preventDefault();
        isSubmitting = true;
        try {
            await api.post('/links/update', formData);
            open = false;
            onDone();
        } catch (err) {
            alert("修改失败: " + err);
        } finally {
            isSubmitting = false;
        }
    }
</script>

{#if open}
    <div class="fixed inset-0 bg-black/40 z-100 flex items-center justify-center p-4 backdrop-blur-sm" 
         onclick={() => open = false} 
         onkeydown={(e) => e.key === 'Escape' && (open = false)}
         role="button"
         tabindex="-1"
         transition:fade>
        
        <form class="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6 space-y-4"
              onsubmit={handleUpdate}  
              onclick={e => e.stopPropagation()} 
              role="presentation"
              transition:scale>
            <h3 class="text-lg font-bold">📝 编辑友链 #{formData.id}</h3>
            
            <input bind:value={formData.name} placeholder="站点名称" class="w-full border p-2 rounded" required />
            <input bind:value={formData.url} type="url" placeholder="URL 地址" class="w-full border p-2 rounded" required />
            <input bind:value={formData.icon} placeholder="图标路径" class="w-full border p-2 rounded" />
            <textarea bind:value={formData.description} placeholder="描述" class="w-full border p-2 rounded"></textarea>

            <div class="flex gap-2 pt-4">
                <button type="button" onclick={() => open = false} class="flex-1 border p-2 rounded">取消</button>
                <button type="submit" disabled={isSubmitting} class="flex-1 bg-green-600 text-white p-2 rounded font-bold">
                    {isSubmitting ? '保存中...' : '保存修改'}
                </button>
            </div>
        </form>
    </div>
{/if}