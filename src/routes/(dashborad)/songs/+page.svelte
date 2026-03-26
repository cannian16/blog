<script lang="ts">
interface Song {
	id: number;
	title: string;
	url: string;
	cover: string;
	artist: string;
}

import { onMount } from "svelte";
import { api } from "$lib/api/client";
import AddSongModal from "$lib/components/dashboard/songs/AddSongModal.svelte";

let isAddOpen = $state(false);

import EditSongModal from "$lib/components/dashboard/songs/EditSongModal.svelte";

let isEditOpen = $state(false);
let editingSong = $state<Song | null>(null);
let songs = $state<Song[]>([]);
let isLoading = $state(true);
let message = $state("");

function startEdit(song: Song) {
	editingSong = song;
	isEditOpen = true;
}

// 1. 查：初始化获取数据
onMount(async () => {
	try {
		songs = await api.get<Song[]>("/songs/get");
	} catch (err) {
		alert(`获取失败: ${err}`);
	} finally {
		isLoading = false;
	}
});
async function deleteSong(id: number) {
	if (!confirm("确定删除这个链接吗？")) return;
	try {
		const response = await api.post("/songs/delete", { id });
		console.log("删除成功:", response);
		songs = songs.filter((l) => l.id !== id);
	} catch (err) {
		message = `发生错误: ${err}`;
	} finally {
		isLoading = false;
	}
}

async function refresh() {
	songs = await api.get("/songs/get");
}
</script>

<div class="p-6 bg-gray-50 min-h-screen">
    <div class="max-w-5xl mx-auto"> <header class="flex justify-between items-center mb-8">
            <h1 class="text-2xl font-bold text-gray-800">音乐管理</h1>
            <button onclick={() => isAddOpen = true} class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition">
                + 新增音乐
            </button>
            <AddSongModal bind:open={isAddOpen} onDone={refresh} />
        </header>

        {#if isLoading}
            <p class="text-center text-gray-500 pt-10">加载中...</p>
        {:else}
            <div class="flex flex-col bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                <div class="grid grid-cols-[40px_1fr_1fr_1fr_1fr_100px] gap-4 p-4 bg-gray-50 text-xs font-bold text-gray-500 uppercase tracking-wider border-b border-gray-200">
                    <div>ID</div>
                    <div>音乐名</div>
                    <div>音源链接</div>
                    <div>海报链接</div>
                    <div>作者</div>
                    <div class="text-right">操作</div>
                </div>

                {#each songs as song (song.id)}
                    <div class="group grid grid-cols-[40px_1fr_1fr_1fr_1fr_100px] items-center gap-4 p-4 hover:bg-indigo-50/30 transition text-sm border-b border-gray-100 last:border-0">
                        
                        <div class="text-gray-400 font-mono text-xs">
                            #{song.id}
                        </div>

                        <div class="font-bold text-gray-800 truncate" title={song.title}>
                            {song.title}
                        </div>
                    
                        <div class="text-blue-500 truncate font-mono text-xs" title={song.url}>
                            <a href={song.url} target="_blank" rel="noopener noreferrer" class="hover:underline">{song.url}</a>
                        </div>
                    
                        <div class="text-gray-400 truncate text-xs italic" title={song.cover}>
                            <a href={song.cover} target="_blank" rel="noopener noreferrer" class="hover:underline opacity-70">{song.cover}</a>
                        </div>
                    
                        <div class="text-gray-500 truncate" title={song.artist}>
                            {song.artist || '暂无描述'}
                        </div>
                    
                        <div class="flex justify-end gap-4 opacity-0 group-hover:opacity-100 transition shrink-0">
                            <button onclick={() => startEdit(song)} class="text-indigo-600 hover:font-bold transition-all">编辑</button>
                            <EditSongModal bind:open={isEditOpen} song={editingSong} onDone={refresh} />
                            <button 
                                onclick={() => deleteSong(song.id)} 
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