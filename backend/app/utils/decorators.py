import os
from functools import wraps
from flask import request, jsonify
import jwt

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
          
        auth_header = request.headers.get('Authorization')

        # 1. 健壮性检查：防止 Header 为空或格式不对导致 split 报错
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"message": "未提供有效凭证"}), 401
            
        token = auth_header.split(' ')[1]

        try:
            # 2. 核心验算：这一步会检查签名是否匹配、Token 是否过期
            payload = jwt.decode(
                token, 
                os.getenv('SECRET_KEY'), 
                algorithms=["HS256"]
            )
            # 3. 进阶检查：判断 Payload 里的 admin 权限（对应你 login 里的设置）
            if not payload.get('admin'):
                return jsonify({"message": "权限不足"}), 403
                
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token 已过期"}), 401
        except jwt.InvalidTokenError:
            # 只要签名不对、被改过、或者根本不是 JWT，都会进这里
            return jsonify({"message": "无效的 Token"}), 401
        except Exception as e:
            return jsonify({"message": f"验证失败: {str(e)}"}), 401
            
        return f(*args, **kwargs)
    return decorated