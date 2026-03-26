import { PUBLIC_API_BASE_URL } from '$env/static/public';
import { browser } from '$app/environment';

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
    // 自动补全基础路径
    const url = `${PUBLIC_API_BASE_URL}${path}`;

    // 默认加上 JSON 头
    const headers = new Headers(options.headers);
    if (options.body && !headers.has('Content-Type')) {
        headers.set('Content-Type', 'application/json');
    }
    //加jwt
    if (browser) {
        const token = localStorage.getItem('jwt_token');
        if (token && !headers.has('Authorization')) {
            headers.set('Authorization', `Bearer ${token}`);
        }
    }

    const response = await fetch(url, { ...options, headers });

    // 如果状态码不是 2xx，抛出错误
    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API Error (${response.status}): ${errorText || '未知错误'}`);
    }

    // 针对 204 No Content (常用于删除) 做个兼容
    if (response.status === 204) return {} as T;
    
    return response.json() as T;
}

export const api = {
    get: <T>(path: string) => request<T>(path, { method: 'GET' }),
    post: <T>(path: string, body: any) => request<T>(path, { method: 'POST', body: JSON.stringify(body) }),
    put: <T>(path: string, body: any) => request<T>(path, { method: 'PUT', body: JSON.stringify(body) }),
    delete: <T>(path: string) => request<T>(path, { method: 'DELETE' }),
};