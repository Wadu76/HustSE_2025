from flask import Blueprint, request, jsonify, current_app
from app.models.book import Book
from app.utils.auth import login_required
from app import db
from werkzeug.utils import secure_filename # 导入安全文件名工具
import os
from datetime import datetime
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
    
    # --- 【修改】我们将所有逻辑放入一个 try/except 块中 ---
    try:
        # 1. 获取文本数据
        title = request.form.get('title')
        course_tag = request.form.get('course_tag')
        condition = request.form.get('condition')
        price = request.form.get('price')

        if not all([title, course_tag, condition, price]):
            return jsonify({'code': 400, 'msg': '缺少必要的文本参数(title, course_tag, condition, price)'}), 400

        # 2. 获取文件数据
        image_file = request.files.get('image')
        image_url = '' # 默认值

        # 3. 处理文件（如果用户上传了）
        if image_file and allowed_file(image_file.filename):
            
            # 3.1 获取扩展名
            original_filename = secure_filename(image_file.filename)
            _, extension = os.path.splitext(original_filename)
            
            # 3.2 (保留) 使用时间戳生成唯一文件名
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
            unique_filename = f"{timestamp}{extension}"

            # 3.3 获取保存目录
            upload_folder = current_app.config['UPLOAD_FOLDER']
            
            # 3.4 【新增】确保目录存在 (关键修复!)
            #     os.makedirs 会创建所有不存在的中间目录
            #     exist_ok=True 使得如果目录已存在，也不会报错
            os.makedirs(upload_folder, exist_ok=True)
            
            # 3.5 创建完整保存路径
            save_path = os.path.join(upload_folder, unique_filename)
            
            # 3.6 保存文件
            image_file.save(save_path)
            
            # 3.7 设置数据库URL
            image_url = f"/static/uploads/{unique_filename}"

        # 4. 创建书籍对象
        new_book = Book(
            title=title,
            author=request.form.get('author', ''), 
            course_tag=course_tag,
            condition=condition,
            price=price,
            description=request.form.get('description', ''),
            images=image_url,  # 存入 '' 或 唯一URL
            seller_id=current_user.id,
            status=1 # 【重要】确保新书的状态是 1 (在售)
        )
        
        # 5. 提交数据库
        db.session.add(new_book)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'msg': '书籍发布成功',
            'data': new_book.to_dict()
        }), 200
        
    except Exception as e:
        # 6. 如果上述任何步骤失败（包括文件保存），回滚数据库
        db.session.rollback()
        # 记录错误，方便调试
        current_app.logger.error(f'发布书籍失败: {str(e)}') 
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
