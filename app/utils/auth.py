'''#JWT 用于身份验证
from flask import current_app
import jwt
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from functools import wraps
from app.models.user import User

#生成JWT令牌
def generate_token(user_id):
    payload = {
        'exp': datetime.utcnow() + timedelta(days=7),  #7天过期
        'iat': datetime.utcnow(),
        'sub': user_id
    }
    return jwt.encode(
        payload,
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )

#JWT验证装饰器（保护需要登录的接口）
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        #从请求头获取token（格式：Authorization: Bearer <token>）
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'code': 401, 'msg': '请先登录'}), 401
        
        try:
            #解码token
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            current_user_id = payload['sub']
            current_user = User.query.get(current_user_id)
            if not current_user:
                return jsonify({'code': 401, 'msg': '用户不存在'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'code': 401, 'msg': '登录已过期，请重新登录'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'code': 401, 'msg': '无效的token'}), 401
        
        #将当前用户传递给被装饰的函数
        current_user = User.query.get(current_user_id)
        return f(current_user, *args, **kwargs)
    return decorated'''
#app/utils/auth.py（全新内容）
from flask import session, jsonify, request
from functools import wraps
from app.models.user import User

#登录成功后，将用户ID存入session
def set_login_session(user_id):
    session['user_id'] = user_id  # 简单存储用户ID，视为“登录状态”

#验证是否登录（装饰器）
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        #从session中获取用户ID，没有则视为未登录
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'code': 401, 'msg': '请先登录'}), 401
        
        #检查用户是否存在
        current_user = User.query.get(user_id)
        if not current_user:
            return jsonify({'code': 401, 'msg': '用户不存在'}), 401
        
        #将当前用户传给接口函数
        return f(current_user, *args, **kwargs)
    return decorated