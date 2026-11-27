import { browser } from "$app/environment";
import { PUBLIC_API_BASE_URL } from "$env/static/public";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
	// 自动补全基础路径
	const url = `${PUBLIC_API_BASE_URL}${path}`;

	// 默认加上 JSON 头
	const headers = new Headers(options.headers);
	if (options.body && !headers.has("Content-Type")) {
		headers.set("Content-Type", "application/json");
	}
	//加jwt
	if (browser) {
		const token = localStorage.getItem("jwt_token");
		if (token && !headers.has("Authorization")) {
			headers.set("Authorization", `Bearer ${token}`);
		}
	}

	const response = await fetch(url, { ...options, headers });

	// 如果状态码不是 2xx，抛出错误
	if (!response.ok) {
		const errorText = await response.text();
		let detail = errorText;
		try {
			const body = JSON.parse(errorText);
			if (typeof body?.detail === "string") {
				detail = body.detail;
			} else if (Array.isArray(body?.detail)) {
				detail = body.detail
					.map((item: { msg?: string }) => item.msg ?? JSON.stringify(item))
					.join("; ");
			}
		} catch {
			// 非 JSON 错误体，保留原始文本
		}
		throw new Error(`API Error (${response.status}): ${detail || "未知错误"}`);
	}

	// 针对 204 No Content (常用于删除) 做个兼容
	if (response.status === 204) return {} as T;

	return response.json() as T;
}

export const api = {
	get: <T>(path: string) => request<T>(path, { method: "GET" }),
	post: <T>(path: string, body: unknown) =>
		request<T>(path, { method: "POST", body: JSON.stringify(body) }),
	postForm: <T>(path: string, body: URLSearchParams) =>
		request<T>(path, {
			method: "POST",
			body,
			headers: { "Content-Type": "application/x-www-form-urlencoded" },
		}),
	patch: <T>(path: string, body: unknown) =>
		request<T>(path, { method: "PATCH", body: JSON.stringify(body) }),
	put: <T>(path: string, body: unknown) =>
		request<T>(path, { method: "PUT", body: JSON.stringify(body) }),
	delete: <T>(path: string) => request<T>(path, { method: "DELETE" }),
};
