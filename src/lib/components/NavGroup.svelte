<script lang="ts">
import { Accordion } from "bits-ui";
import { page } from "$app/state"; // 用于判断当前页面是否激活

// 定义传入的属性
let {
	title,
	value,
	basePath,
	items = [],
} = $props<{
	title: string;
	value: string; // Accordion 的唯一标识
	basePath: string; // 基础路径，比如 "/music"
	items?: { label: string; suffix: string; color?: string }[];
}>();

const defaultItems = [
	{ label: "查看", suffix: "/get", color: "text-gray-600" },
	{ label: "新增", suffix: "/add", color: "text-gray-600" },
	{ label: "更新", suffix: "/update", color: "text-gray-600" },
	{ label: "删除", suffix: "/delete", color: "text-red-500" },
];

const displayItems = $derived(items.length > 0 ? items : defaultItems);
</script>

<Accordion.Item {value} class="border-b last:border-b-0">
  <Accordion.Header>
    <Accordion.Trigger class="flex w-full items-center justify-between p-4 font-medium hover:bg-gray-50 transition-colors text-gray-700">
      <span>{title}</span>
    </Accordion.Trigger>
  </Accordion.Header>
  
  <Accordion.Content class="bg-gray-50/50 px-4 pb-3">
    <nav class="flex flex-col gap-1 pt-2">
      {#each displayItems as item}
        {@const fullPath = `${basePath}${item.suffix}`}
        {@const isActive = page.url.pathname === fullPath}
        
        <a 
          href={fullPath} 
          class="flex items-center gap-2 p-2 text-sm rounded transition-all 
            {item.color ?? 'text-gray-600'} 
            {isActive ? 'bg-orange-100 font-semibold' : 'hover:bg-orange-50'}"
        >
          <span>{item.label}</span>
        </a>
      {/each}
    </nav>
  </Accordion.Content>
</Accordion.Item>