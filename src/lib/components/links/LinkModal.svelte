<script lang="ts">
	import { fade, scale } from 'svelte/transition';

	// 定义组件属性
	let { 
		show = $bindable(false), 
		onsubmit, 
		initialData = null 
	} = $props();

	// 内部表单状态
	let formData = $state({
		name: '',
		url: '',
		icon: '',
		description: ''
	});

	let isSubmitting = $state(false);

	// 当 initialData 改变时（比如点击编辑），同步到本地表单
	$effect(() => {
		if (initialData) {
			formData = { ...initialData };
		} else {
			formData = { name: '', url: '', icon: '', description: '' };
		}
	});

	async function handleSubmit(e: Event) {
		e.preventDefault();
		isSubmitting = true;
		try {
			// 调用父组件传进来的提交逻辑
			await onsubmit(formData);
			show = false; // 成功后关闭
		} catch (err) {
			console.error(err);
		} finally {
			isSubmitting = false;
		}
	}
</script>

{#if show}
	<div 
		class="fixed inset-0 bg-black/40 z-[100] flex items-center justify-center p-4 backdrop-blur-sm"
		onclick={() => (show = false)}
		transition:fade={{ duration: 150 }}
	>
		<div 
			class="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden"
			onclick={(e) => e.stopPropagation()}
			transition:scale={{ duration: 200, start: 0.95 }}
		>
			<div class="p-6 border-b border-gray-50 flex justify-between items-center bg-gray-50/50">
				<h3 class="text-lg font-bold text-gray-800">{initialData ? '编辑友链' : '新增友链'}</h3>
				<button onclick={() => (show = false)} class="text-gray-400 hover:text-gray-600">
					<svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
					</svg>
				</button>
			</div>

			<form onsubmit={handleSubmit} class="p-6 space-y-4">
				<div class="space-y-1">
					<label class="text-sm font-semibold text-gray-600">站点名称</label>
					<input bind:value={formData.name} type="text" placeholder="站点名称" class="w-full px-4 py-2 border rounded-lg outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition" required />
				</div>

				<div class="space-y-1">
					<label class="text-sm font-semibold text-gray-600">URL 地址</label>
					<input bind:value={formData.url} type="url" placeholder="https://..." class="w-full px-4 py-2 border rounded-lg outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition font-mono text-sm" required />
				</div>

				<div class="space-y-1">
					<label class="text-sm font-semibold text-gray-600">图标链接</label>
					<input bind:value={formData.icon} type="text" placeholder="图片 URL 或路径" class="w-full px-4 py-2 border rounded-lg outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition" />
				</div>

				<div class="space-y-1">
					<label class="text-sm font-semibold text-gray-600">描述</label>
					<textarea bind:value={formData.description} placeholder="简单介绍一下..." rows="3" class="w-full px-4 py-2 border rounded-lg outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition"></textarea>
				</div>

				<div class="pt-4 flex gap-3">
					<button type="button" onclick={() => (show = false)} class="flex-1 px-4 py-2.5 border border-gray-200 text-gray-600 rounded-xl hover:bg-gray-50 transition">取消</button>
					<button type="submit" disabled={isSubmitting} class="flex-1 px-4 py-2.5 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition font-bold shadow-lg shadow-indigo-200 flex justify-center items-center">
						{#if isSubmitting}
							<div class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
						{:else}
							确定提交
						{/if}
					</button>
				</div>
			</form>
		</div>
	</div>
{/if}