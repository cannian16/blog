<script lang="ts">
  import { Button, AlertDialog } from "bits-ui";
  import { api } from "$lib/api/client";
  import { Toaster, toast } from 'svelte-sonner'

  let isLoading = $state(false);
  let isDialogOpen = $state(false);
  async function handleDeploy() {
    // 1. 防止重复提交
    if (isLoading) return;
    isLoading = true;
    try {
      const response = await api.post("/system/deploy", {});
      isDialogOpen = false;
      toast.success("指令已送达", {
        description: "GitHub Actions 正在拼命构建中..."
      });
    } catch (error:any) {
      toast.error("启动失败", {
        description: error.message
      });
    } finally {
      isLoading = false;
    }
  }
</script>

<Toaster richColors position="top-right" />

<AlertDialog.Root bind:open={isDialogOpen}>
  <AlertDialog.Trigger
    disabled={isLoading}
    class="inline-flex h-12 items-center justify-center whitespace-nowrap rounded-xl bg-zinc-900 px-6 text-[15px] font-semibold text-zinc-50 shadow-sm transition-all hover:bg-zinc-800 active:scale-[0.98] disabled:opacity-50"
  >
    {isLoading ? "请求中..." : "部署"}
  </AlertDialog.Trigger>

  <AlertDialog.Portal>
    <AlertDialog.Overlay
      class="fixed inset-0 z-50 bg-black/60 backdrop-blur-[2px] data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0"
    />
    
    <AlertDialog.Content
      class="fixed left-[50%] top-[50%] z-50 grid w-full max-w-[calc(100%-2rem)] translate-x-[-50%] translate-y-[-50%] gap-6 rounded-2xl border border-zinc-200 bg-white p-8 shadow-2xl outline-none sm:max-w-lg data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95"
    >
      <div class="flex flex-col gap-2 text-left">
        <AlertDialog.Title class="text-xl font-bold tracking-tight text-zinc-900">
          确认你的操作
        </AlertDialog.Title>
        <AlertDialog.Description class="text-sm leading-relaxed text-zinc-500">
          这个行为无法被撤销，确认要重新构建博客吗
        </AlertDialog.Description>
      </div>

      <div class="flex w-full items-center justify-end gap-3 mt-2">
        <AlertDialog.Cancel
          class="inline-flex h-11 flex-1 items-center justify-center rounded-xl bg-zinc-100 text-[15px] font-medium text-zinc-600 transition-all hover:bg-zinc-200 active:scale-[0.98] sm:flex-none sm:px-6"
        >
          我再想想
        </AlertDialog.Cancel>

        <AlertDialog.Action
          onclick={(e) => {
            e.preventDefault();
            handleDeploy();
          }}
          class="inline-flex h-11 flex-1 items-center justify-center rounded-xl bg-indigo-600 text-[15px] font-semibold text-white shadow-sm transition-all hover:bg-indigo-700 active:scale-[0.98] disabled:opacity-50 sm:flex-none sm:px-8"
        >
          {isLoading ? "发送中..." : "确定执行"}
        </AlertDialog.Action>
      </div>
    </AlertDialog.Content>
  </AlertDialog.Portal>
</AlertDialog.Root>