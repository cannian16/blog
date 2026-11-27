from app.core.config import settings


def verify_admin(username: str | None, password: str | None) -> tuple[bool, tuple[dict, int] | None]:
    if not settings.ADMIN_PASSWORD or not settings.ADMIN_USERNAME:
        return False, ({"message": "服务器未配置管理员凭据"}, 500)
    if username != settings.ADMIN_USERNAME:
        return False, ({"message": "管理员用户名错误"}, 403)
    if password != settings.ADMIN_PASSWORD:
        return False, ({"message": "管理员密码错误"}, 403)
    return True, None
