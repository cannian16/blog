<script lang="ts">
interface Skill {
	id: number;
	name: string;
	url: string;
	logo: string;
}

import { onMount } from "svelte";
import { api } from "$lib/api/client";
import AddSkillModal from "$lib/components/dashboard/skills/AddSkillModal.svelte";

let isAddOpen = $state(false);

import EditSkillModal from "$lib/components/dashboard/skills/EditSkillModal.svelte";

let isEditOpen = $state(false);
let editingSkill = $state<Skill | null>(null);
let skills = $state<Skill[]>([]);
let isLoading = $state(true);
let message = $state("");

function startEdit(skill: Skill) {
	editingSkill = skill;
	isEditOpen = true;
}

// 1. 查：初始化获取数据
onMount(async () => {
	try {
		skills = await api.get<Skill[]>("/skills/get");
	} catch (err) {
		alert(`获取失败: ${err}`);
	} finally {
		isLoading = false;
	}
});
async function deleteSkill(id: number) {
	if (!confirm("确定删除这个链接吗？")) return;
	try {
		const response = await api.post("/skills/delete", { id });
		console.log("删除成功:", response);
		skills = skills.filter((l) => l.id !== id);
	} catch (err) {
		message = `发生错误: ${err}`;
	} finally {
		isLoading = false;
	}
}

async function refresh() {
	skills = await api.get("/skills/get");
}
</script>

<div class="p-6 bg-gray-50 min-h-screen">
    <div class="max-w-5xl mx-auto"> <header class="flex justify-between items-center mb-8">
            <h1 class="text-2xl font-bold text-gray-800">技术栈管理</h1>
            <button onclick={() => isAddOpen = true} class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition">
                + 新增项目
            </button>
            <AddSkillModal bind:open={isAddOpen} onDone={refresh} />
        </header>

        {#if isLoading}
            <p class="text-center text-gray-500 pt-10">加载中...</p>
        {:else}
            <div class="flex flex-col bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                <div class="grid grid-cols-[40px_120px_1fr_1fr_100px] gap-4 p-4 bg-gray-50 text-xs font-bold text-gray-500 uppercase tracking-wider border-b border-gray-200">
                    <div>ID</div>
                    <div>名称</div>
                    <div>官网</div>
                    <div>图标链接</div>
                    <div class="text-right">操作</div>
                </div>

                {#each skills as skill (skill.id)}
                    <div class="group grid grid-cols-[40px_120px_1fr_1fr_100px] items-center gap-4 p-4 hover:bg-indigo-50/30 transition text-sm border-b border-gray-100 last:border-0">
                        
                        <div class="text-gray-400 font-mono text-xs">
                            #{skill.id}
                        </div>

                        <div class="font-bold text-gray-800 truncate" title={skill.name}>
                            {skill.name}
                        </div>
                    
                        <div class="text-blue-500 truncate font-mono text-xs" title={skill.url}>
                            <a href={skill.url} target="_blank" rel="noopener noreferrer" class="hover:underline">{skill.url}</a>
                        </div>
                    
                        <div class="text-gray-400 truncate text-xs italic" title={skill.logo}>
                            <a href={skill.logo} target="_blank" rel="noopener noreferrer" class="hover:underline opacity-70">{skill.logo}</a>
                        </div>

                        <div class="flex justify-end gap-4 opacity-0 group-hover:opacity-100 transition shrink-0">
                            <button onclick={() => startEdit(skill)} class="text-indigo-600 hover:font-bold transition-all">编辑</button>
                            <EditSkillModal bind:open={isEditOpen} skill={editingSkill} onDone={refresh} />
                            <button 
                                onclick={() => deleteSkill(skill.id)} 
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