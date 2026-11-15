<script lang="ts">
import { fade, scale } from "svelte/transition";
import { api } from "$lib/api/client";

// props: open 用于控制显示，onDone 用于通知父组件刷新列表
let { open = $bindable(false), onDone } = $props();

// 状态永远初始化为空
let formData = $state({ name: "", url: "", icon: "", description: "" });
let isSubmitting = $state(false);

async function handleAdd(e: Event) {
	e.preventDefault();
	isSubmitting = true;
	try {
		await api.post("/links/add", formData);
		// 提交成功：重置表单 -> 关闭弹窗 -> 刷新列表
		formData = { name: "", url: "", icon: "", description: "" };
		open = false;
		onDone();
	} catch (err) {
		alert(`新增失败: ${err}`);
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
              onsubmit={handleAdd} 
              onclick={e => e.stopPropagation()} 
              role="presentation"
              transition:scale>
            <h3 class="text-lg font-bold">✨ 新增友链</h3>
            
            <input bind:value={formData.name} placeholder="站点名称" class="w-full border p-2 rounded" required />
            <input bind:value={formData.url} type="url" placeholder="URL 地址" class="w-full border p-2 rounded" required />
            <input bind:value={formData.icon} placeholder="图标路径" class="w-full border p-2 rounded" />
            <textarea bind:value={formData.description} placeholder="描述" class="w-full border p-2 rounded"></textarea>

            <div class="flex gap-2 pt-4">
                <button type="button" onclick={() => open = false} class="flex-1 border p-2 rounded">取消</button>
                <button type="submit" disabled={isSubmitting} class="flex-1 bg-indigo-600 text-white p-2 rounded font-bold">
                    {isSubmitting ? '提交中...' : '确定创建'}
                </button>
            </div>
        </form>
    </div>
{/if}