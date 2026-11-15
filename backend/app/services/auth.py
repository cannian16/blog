import os
from flask import jsonify


def verify_admin(username, password):
    """
    验证管理员身份
    返回: (True, None) 验证通过
    返回: (False, (dict, status_code)) 验证失败
    """
    expected_username = os.getenv("ADMIN_USERNAME")
    expected_password = os.getenv("ADMIN_PASSWORD")
    # 1. 检查环境变量配置
    if not expected_password or not expected_username:
        return False, ({"message": "服务器未配置管理员凭据"}, 500)
    # 2. 校验用户名
    if username != expected_username:
        return False, ({"message": "管理员用户名错误"}, 403)
    # 3. 校验密码
    if password != expected_password:
        return False, ({"message": "管理员密码错误"}, 403)
    return True, None