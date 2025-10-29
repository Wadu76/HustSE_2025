from flask import Blueprint, request, jsonify
from app.models.user import User
from app import db
#from app.utils.auth import generate_token #导入jwt生成工具
from app.utils.auth import set_login_session
from werkzeug.security import generate_password_hash, check_password_hash 
from app.utils.auth import login_required
#创建用户路由的蓝图 /user
user_bp = Blueprint('user', __name__, url_prefix='/user')

#1. 用户注册接口
@user_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    #校验必填参数
    if not all(k in data for k in ('phone', 'password', 'username')):
        return jsonify({'code': 400, 'msg': '缺少必填的参数，请检查（手机号/密码/用户名）'}), 400

    #校验手机号是否已注册
    if User.query.filter_by(phone=data['phone']).first():
        return jsonify({'code':400, 'msg':'手机号已被注册'})
    
    #校验用户名是否已被用
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'code':400, 'msg':'用户名已被使用'})
    
    #新用户创建
    new_user = User(
        phone=data['phone'],
        username=data['username'],
        identity=data.get('identity', 'buyer'), #可选默认是买家
        major=data.get('major', ''),    #可为空
        grade=data.get('grade', ''),   #可为空
    )
    new_user.set_password(data['password'])    #加密密码

    db.session.add(new_user)
    try:
        db.session.commit()
        return jsonify({
            'code': 200,
            'msg': '注册成功',
            'data': {
                'id': new_user.id,
                'phone': new_user.phone,
                'username': new_user.username,
                'credit': new_user.credit
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'msg': f'注册失败：{str(e)}'}), 500
    
#2. 用户登录接口 -- 生成jwt令牌 
#登录路由
@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    phone = data.get('phone')
    password = data.get('password')
    
    # 查询用户
    user = User.query.filter_by(phone=phone).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'code': 400, 'msg': '手机号或密码错误'}), 400
    
    # 登录成功：将用户ID存入session（替代JWT）
    set_login_session(user.id)
    
    # 返回用户信息（不需要token了）
    return jsonify({
        'code': 200,
        'msg': '登录成功',
        'data': {
            'user': {
                'id': user.id,
                'username': user.username,
                'phone': user.phone
            }
        }
    }), 200

#3. 获取当前用户的信息（需要登录）
@user_bp.route('/info', methods=['GET'])
@login_required
def get_user_info(current_user):
    #current_user' 对象是由 @login_required 装饰器
    #自动从 session 中获取用户ID 并查询数据库后得到的

    return jsonify({
        'code': 200,
        'msg': '获取用户信息成功',
        'data': current_user.to_dict()
    }), 200

#4. 更新当前用户信息（需要登录）
@user_bp.route('/info', methods=['PUT'])
@login_required
def update_user_info(current_user):
    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'msg': '缺少数据'}), 400
    
    #1. 检查用户名（如果要改用户名）
    new_username = data.get('username')
    if new_username and new_username != current_user.username:
        # 检查用户名是否已存在
        if User.query.filter_by(username=new_username).first():
            return jsonify({'code': 400, 'msg': '用户名已存在'}), 400
        current_user.username = new_username

    #2. 更新其他可选字段（以防万一）
    if 'major' in data:
        current_user.major = data.get('major')
    
    if 'grade' in data:
        current_user.grade = data.get('grade')
    
    #3. 提交数据库
    try:
        db.session.commit()
        return jsonify({
            'code': 200,
            'msg': '用户信息更新成功',
            'data': current_user.to_dict() #返回更新后的用户信息
        }), 200
    except Exception as e:
        db.session.rollback() #出错时回滚
        return jsonify({'code': 500, 'msg': f'更新失败：{str(e)}'}), 500
