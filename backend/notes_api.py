"""
ProteinHub Notes API
提供笔记Feed流、点赞、收藏、评论等功能
"""

from flask import Blueprint, request, jsonify, g
from sqlalchemy import desc, func
from datetime import datetime
import json

# 导入模型 (在app.py中初始化后注入)
notes_bp = Blueprint('notes', __name__, url_prefix='/api/notes')


def get_db_session():
    """获取数据库会话"""
    from flask import current_app
    return current_app.config['db_session']()


def get_current_user_id():
    """从JWT token获取当前用户ID (简化版)"""
    # 实际实现中应该从g.current_user获取
    # 这里为了演示，支持通过header传入user-id
    return request.headers.get('X-User-Id', type=int)


@notes_bp.route('/feed', methods=['GET'])
def get_feed():
    """
    获取笔记Feed流
    
    Query参数:
        page: 页码 (默认1)
        per_page: 每页数量 (默认10, 最大50)
        sort: 排序方式 (newest, popular)
    
    Returns:
        {
            "success": true,
            "data": {
                "notes": [...],
                "total": 100,
                "page": 1,
                "per_page": 10,
                "has_more": true
            }
        }
    """
    try:
        Session = get_db_session()
        
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 50)
        sort = request.args.get('sort', 'newest')
        
        from models import Note, User, Like, Favorite
        
        # 构建查询
        query = Session.query(Note).filter(Note.status == 'published')
        
        # 排序
        if sort == 'popular':
            # 按点赞数+收藏数排序
            query = query.outerjoin(Like).group_by(Note.id).order_by(
                desc(func.count(Like.id))
            )
        else:
            # 默认按时间倒序
            query = query.order_by(desc(Note.created_at))
        
        # 分页
        total = query.count()
        notes = query.offset((page - 1) * per_page).limit(per_page).all()
        
        # 获取当前用户的点赞/收藏状态
        current_user_id = get_current_user_id()
        user_likes = set()
        user_favorites = set()
        
        if current_user_id:
            user_likes = {l.note_id for l in Session.query(Like).filter_by(user_id=current_user_id).all()}
            user_favorites = {f.note_id for f in Session.query(Favorite).filter_by(user_id=current_user_id).all()}
        
        # 序列化结果
        result = []
        for note in notes:
            note_dict = note.to_dict(include_author=True)
            note_dict['is_liked'] = note.id in user_likes
            note_dict['is_favorited'] = note.id in user_favorites
            result.append(note_dict)
        
        Session.close()
        
        return jsonify({
            'success': True,
            'data': {
                'notes': result,
                'total': total,
                'page': page,
                'per_page': per_page,
                'has_more': (page * per_page) < total
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@notes_bp.route('/<int:note_id>', methods=['GET'])
def get_note_detail(note_id):
    """
    获取笔记详情
    
    Args:
        note_id: 笔记ID
    
    Returns:
        {
            "success": true,
            "data": { ...note details... }
        }
    """
    try:
        Session = get_db_session()
        from models import Note, Like, Favorite
        
        note = Session.query(Note).filter_by(id=note_id, status='published').first()
        
        if not note:
            Session.close()
            return jsonify({
                'success': False,
                'error': 'Note not found'
            }), 404
        
        # 增加浏览次数
        note.view_count += 1
        Session.commit()
        
        # 获取当前用户的点赞/收藏状态
        current_user_id = get_current_user_id()
        is_liked = False
        is_favorited = False
        
        if current_user_id:
            is_liked = Session.query(Like).filter_by(user_id=current_user_id, note_id=note_id).first() is not None
            is_favorited = Session.query(Favorite).filter_by(user_id=current_user_id, note_id=note_id).first() is not None
        
        note_dict = note.to_dict(include_author=True)
        note_dict['is_liked'] = is_liked
        note_dict['is_favorited'] = is_favorited
        
        Session.close()
        
        return jsonify({
            'success': True,
            'data': note_dict
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@notes_bp.route('/<int:note_id>/like', methods=['POST'])
def like_note(note_id):
    """
    点赞/取消点赞笔记
    
    Args:
        note_id: 笔记ID
    
    Returns:
        {
            "success": true,
            "data": {
                "is_liked": true,
                "likes_count": 42
            }
        }
    """
    try:
        Session = get_db_session()
        from models import Note, Like
        
        user_id = get_current_user_id()
        if not user_id:
            Session.close()
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        note = Session.query(Note).filter_by(id=note_id).first()
        if not note:
            Session.close()
            return jsonify({
                'success': False,
                'error': 'Note not found'
            }), 404
        
        # 检查是否已点赞
        existing_like = Session.query(Like).filter_by(user_id=user_id, note_id=note_id).first()
        
        if existing_like:
            # 取消点赞
            Session.delete(existing_like)
            is_liked = False
        else:
            # 添加点赞
            new_like = Like(user_id=user_id, note_id=note_id)
            Session.add(new_like)
            is_liked = True
        
        Session.commit()
        
        # 获取最新的点赞数
        likes_count = Session.query(Like).filter_by(note_id=note_id).count()
        
        Session.close()
        
        return jsonify({
            'success': True,
            'data': {
                'is_liked': is_liked,
                'likes_count': likes_count
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@notes_bp.route('/<int:note_id>/favorite', methods=['POST'])
def favorite_note(note_id):
    """
    收藏/取消收藏笔记
    
    Args:
        note_id: 笔记ID
    
    Returns:
        {
            "success": true,
            "data": {
                "is_favorited": true,
                "favorites_count": 15
            }
        }
    """
    try:
        Session = get_db_session()
        from models import Note, Favorite
        
        user_id = get_current_user_id()
        if not user_id:
            Session.close()
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        note = Session.query(Note).filter_by(id=note_id).first()
        if not note:
            Session.close()
            return jsonify({
                'success': False,
                'error': 'Note not found'
            }), 404
        
        # 检查是否已收藏
        existing_favorite = Session.query(Favorite).filter_by(user_id=user_id, note_id=note_id).first()
        
        if existing_favorite:
            # 取消收藏
            Session.delete(existing_favorite)
            is_favorited = False
        else:
            # 添加收藏
            new_favorite = Favorite(user_id=user_id, note_id=note_id)
            Session.add(new_favorite)
            is_favorited = True
        
        Session.commit()
        
        # 获取最新的收藏数
        favorites_count = Session.query(Favorite).filter_by(note_id=note_id).count()
        
        Session.close()
        
        return jsonify({
            'success': True,
            'data': {
                'is_favorited': is_favorited,
                'favorites_count': favorites_count
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@notes_bp.route('/<int:note_id>/comments', methods=['GET'])
def get_comments(note_id):
    """
    获取笔记评论列表
    
    Args:
        note_id: 笔记ID
    
    Query参数:
        page: 页码
        per_page: 每页数量
    
    Returns:
        {
            "success": true,
            "data": {
                "comments": [...],
                "total": 20
            }
        }
    """
    try:
        Session = get_db_session()
        from models import Note, Comment
        
        # 检查笔记是否存在
        note = Session.query(Note).filter_by(id=note_id).first()
        if not note:
            Session.close()
            return jsonify({
                'success': False,
                'error': 'Note not found'
            }), 404
        
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 50)
        
        # 获取顶级评论（非回复）
        query = Session.query(Comment).filter_by(
            note_id=note_id,
            parent_id=None
        ).order_by(desc(Comment.created_at))
        
        total = query.count()
        comments = query.offset((page - 1) * per_page).limit(per_page).all()
        
        # 获取每个评论的回复
        result = []
        for comment in comments:
            comment_dict = comment.to_dict(include_user=True)
            
            # 获取回复（限制数量）
            replies = Session.query(Comment).filter_by(parent_id=comment.id).order_by(
                Comment.created_at
            ).limit(5).all()
            
            comment_dict['replies'] = [r.to_dict(include_user=True) for r in replies]
            comment_dict['replies_count'] = Session.query(Comment).filter_by(parent_id=comment.id).count()
            
            result.append(comment_dict)
        
        Session.close()
        
        return jsonify({
            'success': True,
            'data': {
                'comments': result,
                'total': total,
                'page': page,
                'per_page': per_page
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@notes_bp.route('/<int:note_id>/comments', methods=['POST'])
def create_comment(note_id):
    """
    发表评论
    
    Args:
        note_id: 笔记ID
    
    Request Body:
        {
            "content": "评论内容",
            "parent_id": null  // 可选，回复的评论ID
        }
    
    Returns:
        {
            "success": true,
            "data": { ...comment... }
        }
    """
    try:
        Session = get_db_session()
        from models import Note, Comment
        
        user_id = get_current_user_id()
        if not user_id:
            Session.close()
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        # 检查笔记是否存在
        note = Session.query(Note).filter_by(id=note_id).first()
        if not note:
            Session.close()
            return jsonify({
                'success': False,
                'error': 'Note not found'
            }), 404
        
        data = request.get_json()
        if not data or not data.get('content'):
            Session.close()
            return jsonify({
                'success': False,
                'error': 'Content is required'
            }), 400
        
        content = data.get('content', '').strip()
        if len(content) < 1 or len(content) > 1000:
            Session.close()
            return jsonify({
                'success': False,
                'error': 'Content length must be between 1 and 1000 characters'
            }), 400
        
        # 创建评论
        new_comment = Comment(
            user_id=user_id,
            note_id=note_id,
            parent_id=data.get('parent_id'),
            content=content
        )
        
        Session.add(new_comment)
        Session.commit()
        
        # 刷新获取完整数据
        Session.refresh(new_comment)
        result = new_comment.to_dict(include_user=True)
        
        Session.close()
        
        return jsonify({
            'success': True,
            'data': result
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
