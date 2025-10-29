from flask import Blueprint, request, jsonify, current_app
from app.models.book import Book
from app.utils.auth import login_required
from app import db
from werkzeug.utils import secure_filename # 导入安全文件名工具
import os
#书籍相关蓝图
book_bp = Blueprint('book', __name__, url_prefix='/book')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#1. 发布书籍（支持图片上传）
@book_bp.route('/create', methods=['POST'])
@login_required 
def create_book(current_user): 
    # 1. 不再使用 request.get_json()
    #    因为文件上传时，数据在 request.form (文本) 和 request.files (文件) 中
    
    # 2. 从 request.form 获取文本数据
    title = request.form.get('title')
    course_tag = request.form.get('course_tag')
    condition = request.form.get('condition')
    price = request.form.get('price')

    # 3. 校验必填的 *文本* 字段
    if not all([title, course_tag, condition, price]):
        return jsonify({'code': 400, 'msg': '缺少必要的文本参数(title, course_tag, condition, price)'}), 400

    # 4. 处理文件上传
    image_file = request.files.get('image') # 'image' 是前端 input<type=file> 的 name
    image_url = '' # 默认图片 URL 为空

    if image_file and allowed_file(image_file.filename):
        # 5. 生成安全的文件名，防止黑客攻击
        filename = secure_filename(image_file.filename)
        
        # 6. 生成文件的保存路径
        #    current_app.config['UPLOAD_FOLDER'] 会读取 config.py 中的设置
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        # 7. 保存文件到服务器
        image_file.save(save_path)
        
        # 8. 【关键】生成用于 *访问* 文件的 URL
        #    我们只在数据库中存储相对路径 (URL)，而不是 C:\... 这样的绝对路径
        image_url = f"/static/uploads/{filename}"

    # 9. 创建书籍记录
    new_book = Book(
        title=title,
        author=request.form.get('author', ''), # 获取可选字段
        course_tag=course_tag,
        condition=condition,
        price=price,
        description=request.form.get('description', ''),
        images=image_url,  # 【修改】存入我们生成的 image_url
        seller_id=current_user.id
    )
    
    db.session.add(new_book)
    try:
        db.session.commit()
        return jsonify({
            'code': 200,
            'msg': '书籍发布成功',
            'data': new_book.to_dict() # to_dict() 也会返回新的 image_url
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'msg': f'发布失败:{str(e)}'}), 500
#2. 多条件检索书籍 （公开的接口）
@book_bp.route('/list', methods=['GET'])
def get_books():

    search = request.args.get('search')#为了搜索栏，获取搜索词
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
    if search:
        #使用 .like() 和 % 通配符来实现模糊查询
        query = query.filter(Book.title.like(f"%{search}%"))
    
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
