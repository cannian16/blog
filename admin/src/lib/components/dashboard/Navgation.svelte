<script lang="ts">
import { Accordion } from "bits-ui";
import { page } from "$app/state";
</script>

<Accordion.Root type="single">
  <Accordion.Item value="content" class="border-b last:border-b-0">
    <Accordion.Header>
      <Accordion.Trigger class="flex w-full items-center justify-between p-4 font-medium hover:bg-gray-50 transition-colors text-gray-700">
        <span>内容管理</span>
      </Accordion.Trigger>
    </Accordion.Header>
    <Accordion.Content class="bg-gray-50/50 px-4 pb-3">
      <nav class="flex flex-col gap-1 pt-2">
        <a 
          href=/links
          class="flex items-center gap-2 p-2 text-sm rounded transition-all text-gray-600
            {page.url.pathname === '/links' ? 'bg-orange-100 font-semibold' : 'hover:bg-orange-50'}"
        >
          <span>友链</span>
        </a>
        <a 
          href=/songs
          class="flex items-center gap-2 p-2 text-sm rounded transition-all text-gray-600
            {page.url.pathname === '/songs' ? 'bg-orange-100 font-semibold' : 'hover:bg-orange-50'}"
        >
          <span>音乐</span>
        </a>
      </nav>
    </Accordion.Content>
  </Accordion.Item>
  <Accordion.Item value="about" class="border-b last:border-b-0">
    <Accordion.Header>
      <Accordion.Trigger class="flex w-full items-center justify-between p-4 font-medium hover:bg-gray-50 transition-colors text-gray-700">
        <span>关于界面</span>
      </Accordion.Trigger>
    </Accordion.Header>
    <Accordion.Content class="bg-gray-50/50 px-4 pb-3">
      <nav class="flex flex-col gap-1 pt-2">
          <a 
            href=/skills
            class="flex items-center gap-2 p-2 text-sm rounded transition-all text-gray-600
              {page.url.pathname === '/skills' ? 'bg-orange-100 font-semibold' : 'hover:bg-orange-50'}"
          >
            <span>技术栈</span>
          </a>
      </nav>
    </Accordion.Content>
  </Accordion.Item>
</Accordion.Root>