from flask import Blueprint, request, jsonify
from app.models import Post
from app.extensions import db
from app.utils.decorators import token_required
from app.utils.validators import validate_required

posts_bp = Blueprint('posts', __name__, url_prefix='/posts')
@posts_bp.route('/get', methods=['GET'])
def get_posts():
    """获取文章列表"""
    posts = Post.query.order_by(Post.published.desc()).all()
    return jsonify([post.to_dict() for post in posts])

@posts_bp.route('/add', methods=['POST'])
@token_required
def create_post():
    """创建新文章"""
    data = request.get_json()
    # 验证必填字段
    validate_required(data, ['id', 'title', 'content'])
    id = data.get('id').strip()
    title = data.get('title').strip()
    description = data.get('description', '').strip()
    image = data.get('image', '').strip()
    tags = data.get('tags', [])
    category = data.get('category', '').strip()
    content = data.get('content').strip()

    new_post = Post(
        id=id,
        title=title,
        description=description,
        image=image,
        tags=tags,
        category=category,
        content=content
    )
    
    db.session.add(new_post)
    db.session.commit()

    return jsonify(new_post.to_dict()), 201

@posts_bp.route('/delete', methods=['POST'])
@token_required
def delete_post():
    """删除文章"""
    data = request.get_json()
    # 验证必填字段
    validate_required(data, ['id'])
    post_id = data.get('id')
    post = Post.query.get_or_404(post_id)
    if not post:
        return jsonify({"error": "文章不存在"}), 404
    db.session.delete(post)
    db.session.commit()

    return jsonify({"message": "文章已删除"})

@posts_bp.route('/update', methods=['POST'])
@token_required
def update_post():
    """更新文章"""
    #获取请求数据
    data = request.get_json()
    #验证必填字段
    validate_required(data, ['id'])
    #提取文章ID
    post_id = data.get('id')
    #查询文章并更新数据
    post = Post.query.get_or_404(post_id)
    if not post:
        return jsonify({"error": "文章不存在"}), 404

    post.title = data.get('title', post.title).strip()
    post.description = data.get('description', post.description).strip()
    post.image = data.get('image', post.image).strip()
    post.tags = data.get('tags', post.tags)
    post.category = data.get('category', post.category).strip()
    post.content = data.get('content', post.content).strip()

    db.session.commit()

    return jsonify(post.to_dict())