from flask import Blueprint, request, jsonify
from app.models import User
from app import db
from app.utils.auth import generate_token #导入jwt生成工具

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
    #登录必要参数校验
    if not all (k in data for k in ('phone', 'password')):  
        #若是用户名也是必填且唯一的话就可以加进来，但是用的是手机号注册那就只用手机号罢了
        return jsonify({'code': 400, 'msg': '缺少参数,请检查'})
    
    #查询登陆的用户
    user = User.query.filter_by(phone=data['phone']).first()
    if not user or not user.check_password(data['password']):
        return jsonify({'code': 400, 'msg': '用户名(手机号)或密码错误'})

    #生成jwt令牌
    token = generate_token(user.id)
    return jsonify({
        'code': 200,
        'msg': '登录成功',
        'data': {
            'token': token,
            'user':{
                'id': user.id,
                'username': user.username,
                'phone': user.phone,
                'identity': user.identity,
                'credit': user.credit
            }
        }
    }), 200