from flask import Blueprint, request, jsonify
from app.models.book import Book
from app.utils.auth import token_required
from app import db

#书籍相关蓝图
book_bp = Blueprint('book', __name__, url_prefix='/book')

#1. 发布书籍（需要先登录）
@book_bp.route('/create', methods=['POST'])
@token_required #token_required装饰器，用于验证用户是否登录
def create_book(current_user): #or to say, publish a book
    data = request.get_json()
    required_fields = ['title', 'course_tag', 'condition', 'price']
    for field in required_fields:
        if field not in data:
            return jsonify({'code': 400, 'msg': f'缺少必要参数{field}'}), 400
#用于检查用户输入的基本参数，少一个就提醒一个

#创建书籍记录
    new_book = Book(
        title=data['title'],
        author=data.get('author', ''),
        course_tag=data['course_tag'],
        major_tag=data.get('major_tag', ''),
        grade_tag=data.get('grade_tag', ''),
        condition=data['condition'],
        price=data['price'],
        description=data.get('description', ''),
        images=data.get('images', ''),  #前端传都好分隔的url字符串
        seller_id=current_user.id    #关联当前登录用户，也就是卖家

    )
    db.session.add(new_book)
    try:
        db.session.commit()
        return jsonify({
            'code': 200,
            'msg': '书籍发布成功',
            'data': new_book.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'msg': f'发布失败:{str(e)}'}), 500
    
#2. 多条件检索书籍 （公开的接口）
@book_bp.route('/list', methods=['GET'])
def get_books():
    #获取查询参数（包括课程 专业 年纪筛选以及加个排序）
    course_tag = request.args.get('course_tag')
    major_tag = request.args.get('major_tag')
    grade_tag = request.args.get('grade_tag')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    sort_by = request.args.get('sort_by','create_at') #默认按发布时间排序
    order = request.args.get('order', 'desc')   #升序/降序
    
    #构建查询条件
    query = Book.query.filter_by(status=1)  #只查询在售书籍，卖出的就不包含

    #条件筛选
    if course_tag:
        query = query.filter(Book.course_tag == course_tag)
    if major_tag:
        query = query.filter(Book.major_tag == major_tag)
    if grade_tag:
        query = query.filter(Book.grade_tag == grade_tag)
    if min_price is not None:
        query = query.filter(Book.price >= min_price)
    if max_price is not None:
        query = query.filter(Book.price <= max_price)   #限制价格区间
    
    #排序
    if sort_by == 'price':
        if order == 'asc':
            query = query.order_by(Book.price.asd())
        else:
            query = query.order_by(Book.price.desc())
    else:
        #默认按发布时间排序
        if order == 'asc':
            query = query.order_by(Book.create_time.asc())
        else:
            query = query.order_by(Book.create_time.desc())
    
    #分页（默认每页10条）
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    pagination = query.paginate(page=page, per_page=per_page)

    #构建返回的数据
    books = [book.to_dict() for book in pagination.items]
    return jsonify({
        'code': 200,
        'data': {
            'books': books,
            'total': pagination.total,  # 总条数
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages  # 总页数
        }
    }), 200

#3. 查询书籍详情（公开接口）
@book_bp.route('/<int:book_id>', methods=['GET'])
def get_book_detail(book_id):
    book = Book.query.get(book_id)
    if not book or book.status != 1:
        return jsonify({'code':404, 'msg':'书籍不存在 or 已售出~'})
    return jsonify({
        'code':200,
        'data':book.to_dict()
    }), 200
