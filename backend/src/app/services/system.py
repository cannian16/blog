from typing import Any

import requests

from app.core.config import settings


def trigger_deploy() -> tuple[dict[str, Any], int]:
    token = settings.GITHUB_TOKEN
    repo = settings.GITHUB_REPO
    if not token or not repo:
        return {"status": "error", "message": "服务器配置缺失：未找到 GitHub Token 或 Repo 路径"}, 500

    url = f"https://api.github.com/repos/{repo}/dispatches"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    payload = {
        "event_type": "deploy-command",
        "client_payload": {"ref": "main", "reason": "Admin manually triggered rebuild"},
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code == 204:
            return {"status": "success", "message": "CI/CD 流程已在 GitHub 启动"}, 200
        error = response.json() if response.content else response.text
        return {"status": "error", "code": response.status_code, "error": error}, response.status_code
    except requests.exceptions.Timeout:
        return {"status": "error", "message": "请求 GitHub 超时，请稍后重试"}, 504
    except Exception as exc:
        return {"status": "error", "message": f"系统内部错误: {exc}"}, 500
