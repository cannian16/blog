from flask import Blueprint, request, jsonify
from app.utils.decorators import token_required
import requests
import os

system_bp = Blueprint('system', __name__, url_prefix='/system')

@system_bp.route('/deploy', methods=['POST'])
@token_required
def trigger_deploy():
    token = os.getenv('GITHUB_TOKEN')
    repo = os.getenv('GITHUB_REPO')
    url = f"https://api.github.com/repos/{repo}/dispatches"

    if not token or not repo:
        return jsonify({
            "status": "error", 
            "message": "服务器配置缺失：未找到 GitHub Token 或 Repo 路径"
        }), 500
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    payload = {
        "event_type": "deploy-command",
        "client_payload": {
            "ref": "main",
            "reason": "Admin manually triggered rebuild"
        }
    }

    try:
        # 增加 timeout 防止 GitHub 接口响应慢卡死 Flask 线程
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        # 204 是 GitHub Repository Dispatch 的标准成功响应
        if response.status_code == 204:
            return jsonify({"status": "success", "message": "CI/CD 流程已在 GitHub 启动"}), 200
        
        # 处理非 204 的情况
        return jsonify({
            "status": "error", 
            "code": response.status_code,
            "error": response.json() if response.content else response.text
        }), response.status_code

    except requests.exceptions.Timeout:
        return jsonify({"status": "error", "message": "请求 GitHub 超时，请稍后重试"}), 504
    except Exception as e:
        return jsonify({"status": "error", "message": f"系统内部错误: {str(e)}"}), 500