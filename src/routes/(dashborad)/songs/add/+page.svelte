<script lang="ts">
    import { api } from '$lib/api/client';
	// 定义响应式数据状态
	let song = $state({
		title: "",
		artist: "",
		url: "",
		cover: ""
	});

	let loading = $state(false);
	let message = $state("");

	// 提交逻辑
	async function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		loading = true;
		
		try {
			const response = await api.post('/songs/add', song);
            console.log('提交成功:', response);
            message = "保存成功！";
            song = { title: "", artist: "", url: "", cover: "" };
		} catch (err) {
			message = "发生错误: " + err;
		} finally {
			loading = false;
		}
	}
</script>

<form onsubmit={handleSubmit} class="max-w-2xl space-y-6 bg-white p-8 rounded-xl shadow-sm border border-gray-100">
	<h2 class="text-xl font-bold text-gray-800 mb-4">歌曲信息录入</h2>

	<div class="grid grid-cols-1 gap-6">
		<label class="block">
			<span class="text-gray-700 text-sm font-medium">歌曲名称</span>
			<input type="text" bind:value={song.title} class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-orange-500 focus:ring-orange-500"  required />
		</label>

		<label class="block">
			<span class="text-gray-700 text-sm font-medium">艺术家</span>
			<input type="text" bind:value={song.artist} class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-orange-500 focus:ring-orange-500"  />
		</label>

		<label class="block">
			<span class="text-gray-700 text-sm font-medium">音频 URL </span>
			<input type="url" bind:value={song.url} class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-orange-500 focus:ring-orange-500"  />
		</label>

		<div class="flex gap-4 items-end">
			<label class="flex-1">
				<span class="text-gray-700 text-sm font-medium">封面图片 URL</span>
				<input type="url" bind:value={song.cover} class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-orange-500 focus:ring-orange-500" />
			</label>
			{#if song.cover}
				<img src={song.cover} alt="预览" class="w-16 h-16 object-cover rounded border" />
			{/if}
		</div>
	</div>

	<div class="flex items-center gap-4 pt-4">
		<button type="submit" disabled={loading} class="px-6 py-2 bg-orange-600 text-white rounded-lg font-medium hover:bg-orange-700 disabled:opacity-50 transition-all">
			{loading ? '保存中...' : '立即提交'}
		</button>
		
		{#if message}
			<span class="text-sm font-medium {message.includes('成功') ? 'text-green-600' : 'text-red-500'}">
				{message}
			</span>
		{/if}
	</div>
</form>