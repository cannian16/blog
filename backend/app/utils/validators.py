from flask import abort, jsonify, make_response

def validate_required(data, required_fields):
    """
    通用必填项检查
    :param data: request.get_json() 拿到的字典
    :param required_fields: 必填字段列表，例如 ['id', 'title', 'content']
    """
    if not data:
        # 直接抛出 400 错误，中断后续逻辑
        abort(make_response(jsonify({"error": "请求体不能为空"}), 400))
    
    missing = []
    for field in required_fields:
        # 检查键是否存在，且 strip 后是否有内容
        value = data.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            missing.append(field)
    
    if missing:
        error_msg = f"缺少必填字段或内容为空: {', '.join(missing)}"
        abort(make_response(jsonify({"error": error_msg}), 400))
    
    return True