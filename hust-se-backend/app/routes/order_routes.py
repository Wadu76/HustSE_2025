from flask import Blueprint, request, jsonify
from app.models.order import Order
from app.models.book import Book  # 导入书籍模型，用于校验书籍状态
from app.models.user import User  # 导入用户模型，用于校验用户状态
from app.utils.auth import login_required  # 导入登录验证装饰器
from app import db
import random
from datetime import datetime

#创建订单路由蓝图（前缀为/order）
order_bp = Blueprint('order', __name__, url_prefix='/order')


#1. 创建订单（买家操作，需登录）
@order_bp.route('/create', methods=['POST'])
@login_required #验证登录，current_user为当前登录用户（买家）
def create_order(current_user):
    data = request.get_json()
    #校验必要参数：必须传入书籍ID
    if 'book_id' not in data:
        return jsonify({'code': 400, 'msg': '缺少必要参数：book_id'}), 400 #返回400错误，400表示请求参数错误
    
    book_id = data['book_id']
    #1. 查询书籍是否存在且在售
    book = Book.query.filter_by(id=book_id, status=1).first()  # status=1表示在售
    if not book:
        return jsonify({'code': 404, 'msg': '书籍不存在或已售出'}), 404     #返回404错误，404表示资源不存在
    
    #2. 校验买家不能购买自己的书
    if book.seller_id == current_user.id:
        return jsonify({'code': 400, 'msg': '想买自己的书？驳回！'}), 400
    
    #3. 生成唯一订单号（时间戳+买家ID+4位随机数，确保不重复）
    timestamp = int(datetime.now().timestamp())  #时间戳
    random_num = random.randint(1000, 9999)  #4位随机数
    order_no = f"{timestamp}{current_user.id}{random_num}"
    
    #4. 创建订单记录
    new_order = Order(
        order_no=order_no,
        buyer_id=current_user.id,  #买家ID为当前登录用户
        seller_id=book.seller_id,  #卖家ID为书籍的发布者
        book_id=book_id,
        price=book.price  #交易价格为书籍当前售价
    )
    
    #5. 订单创建后，将书籍状态改为“已售出”（避免重复下单）
    book.status = 0  #0表示已售出
    
    #6. 提交数据库事务
    db.session.add(new_order)
    try:
        db.session.commit()
        return jsonify({
            'code': 200,
            'msg': '订单创建成功',
            'data': new_order.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()  #出错时回滚
        return jsonify({'code': 500, 'msg': f'创建订单失败：{str(e)}'}), 500


#2. 查询个人订单列表（区分买家/卖家视角，需登录）
@order_bp.route('/list', methods=['GET'])
@login_required
def get_order_list(current_user):
    #通过query参数区分视角：role=buyer（买家）或role=seller（卖家），默认买家
    role = request.args.get('role', 'buyer')
    
    #根据角色查询对应的订单
    if role == 'buyer':
        #买家视角：查询当前用户作为买家的所有订单
        orders = Order.query.filter_by(buyer_id=current_user.id).order_by(Order.create_time.desc()).all()
    else:
        #卖家视角：查询当前用户作为卖家的所有订单
        orders = Order.query.filter_by(seller_id=current_user.id).order_by(Order.create_time.desc()).all()
    
    #转换为字典列表返回
    return jsonify({
        'code': 200,
        'data': {
            'orders': [order.to_dict() for order in orders],
            'total': len(orders)  #订单总数
        }
    }), 200

#4. 查询订单详情（需登录，且只能查看自己的订单）
@order_bp.route('/<int:order_id>', methods=['GET'])     #GET /order/1 会查询ID为1的订单
@login_required         #登陆验证装饰器，先检查session中有没有userid
def get_order_detail(current_user, order_id):
    #1. 按主键ID查询订单
    order = Order.query.get(order_id) 

    #2. 校验订单是否存在
    if not order:
        return jsonify({'code': 404, 'msg': '订单不存在'}), 404
    
    #3. 校验当前登录用户是否是该订单的买家 or 卖家
    if order.buyer_id != current_user.id:
        #若不是则禁止访问
        return jsonify({'code': 403, 'msg': '无权访问该订单详情'}), 403
        
    #4. 上述校验通过后，返回如下详情：
    return jsonify({
        'code': 200, 
        'data': order.to_dict()
    }), 200

#3. 更新订单状态（如支付、发货、确认收货等，需权限校验）
@order_bp.route('/<int:order_id>/update', methods=['POST'])
@login_required
def update_order_status(current_user, order_id):
    data = request.get_json()
    #校验必要参数：必须传入新状态
    if 'status' not in data:
        return jsonify({'code': 400, 'msg': '缺少必要参数：status'}), 400
    
    new_status = data['status']
    #1. 查询订单是否存在
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'code': 404, 'msg': '订单不存在'}), 404
    
    #2. 权限校验：不同状态只能由特定角色操作
    #状态流转规则：1→2（买家支付）→3（卖家发货）→4（买家确认收货）→5（系统自动完成，或手动）
    if new_status == 2:
        #待支付→已支付：只能由买家操作
        if order.buyer_id != current_user.id:
            return jsonify({'code': 403, 'msg': '无权限操作此订单'}), 403
    elif new_status == 3:
        #已支付→已发货：只能由卖家操作
        if order.seller_id != current_user.id:
            return jsonify({'code': 403, 'msg': '无权限操作此订单'}), 403
    elif new_status == 4:
        #已发货→已收货：只能由买家操作
        if order.buyer_id != current_user.id:
            return jsonify({'code': 403, 'msg': '无权限操作此订单'}), 403
    elif new_status == 5:
        #已收货→已完成：可由买家或卖家操作（或系统自动）
        if order.buyer_id != current_user.id and order.seller_id != current_user.id:
            return jsonify({'code': 403, 'msg': '无权限操作此订单'}), 403
    else:
        #不支持的状态码
        return jsonify({'code': 400, 'msg': '无效的状态值'}), 400
    
    #3. 校验状态流转合法性（防止跳级，如直接从待支付→已收货）
    valid_transitions = {
        1: [2],         #待支付→只能到已支付
        2: [3],         #已支付→只能到已发货
        3: [4],         #已发货→只能到已收货
        4: [5],         #已收货→只能到已完成
        5: []           #已完成→无后续状态
    }
    if new_status not in valid_transitions[order.status]:
        return jsonify({'code': 400, 'msg': f'不支持从{order.get_status_text()}转为{Order(status=new_status).get_status_text()}'}), 400
    
    #4. 更新订单状态
    try:
        #A. 更新订单状态
        order.status = new_status
        
        #B. 新添加的信用分逻辑
        #查询卖家
        seller = User.query.get(order.seller_id)
        
        if seller: #确保卖家存在
            if new_status == 2:
                #状态 2: 已支付 (等待发货) -> 扣减卖家30信用分
                #状态 3: 已发货 (等待交付) -> 扣减卖家30信用分
                seller.credit -= 30
            elif new_status == 4:
                #状态 4: 已收货 (订单完成) -> 返还卖家30信用分
                seller.credit += 30
        
        #C. 提交数据库
        db.session.commit() #commit会同时保存 order 和 seller 的改动
        
        return jsonify({
            'code': 200,
            'msg': '订单状态更新成功',
            'data': order.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'msg': f'更新失败：{str(e)}'}), 500