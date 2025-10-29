#app/models/book.py
from datetime import datetime
from app import db

class Book(db.Model):
    #表名：books
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)    #主键 id
    title = db.Column(db.String(100), nullable=False)   #书名
    author = db.Column(db.String(100), nullable=False)  #作者
    course_tag = db.Column(db.String(50), nullable=False)  #课程标签 不能为空
    grade_tag = db.Column(db.String(20))    #年级标签 大一/大二/...
    condition = db.Column(db.String(50), nullable=False)    #新旧程度 1-5
    price = db.Column(db.Float, nullable=False)   #价格,不能为空
    description = db.Column(db.Text)    #描述,可为空
    images = db.Column(db.String(500))    #图片URL,多个图片用逗号分隔即可
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)    #卖家id
    create_time = db.Column(db.DateTime, default=datetime.utcnow)    #发布时间
    status = db.Column(db.SmallInteger, default=1)   #是否售出，1：在售 0：已售出

     #关联卖家（反向引用：User.books -> 该用户发布的所有书籍）
    seller = db.relationship('User', backref=db.backref('books', lazy=True))\
    
    def to_dict(self):
        # 状态文本映射（将数字状态转换为中文描述，前端更易读）
        status_map = {1: '在售', 0: '已售'}
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'course_tag': self.course_tag,
            'condition': self.condition,
            'price': self.price,
            'seller_id': self.seller_id,
            'description': self.description,
            'images': self.images, #将图片URL字符串转换为列表, 新增
            'status': self.status,
            'status_text': status_map.get(self.status, '未知'),  # 显示中文状态
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S'),  # 格式化时间
            'seller_name': self.seller.username if self.seller else '未知卖家',
            'seller_credit': self.seller.credit if self.seller else 'N/A'
        }