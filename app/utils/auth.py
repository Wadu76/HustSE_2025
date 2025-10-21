#JWT 用于身份验证
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
        return f(current_user, *args, **kwargs)
    return decorated