import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig, loadEnv } from 'vite';

export default defineConfig(({ mode }) => {
	// 第三个参数为空字符串，表示读取所有环境变量（包括非 VITE_ 前缀的）
	const env = loadEnv(mode, '.', '');
	const apiTarget = env.API_PROXY_TARGET;

	return {
		plugins: [tailwindcss(), sveltekit()],
		server: {
			port: 4321,
			strictPort: true,
			proxy: apiTarget
				? {
						'/api': {
							target: apiTarget,
							changeOrigin: true,
							// 后端路由没有 /api 前缀，代理解除该前缀
							rewrite: (path) => path.replace(/^\/api/, ''),
						},
					}
				: undefined,
		},
	};
});
