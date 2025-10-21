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
    seller_id = db.Column(db.Integer, db.Foreignkey('users.id'), nullable=False)    #卖家id
    create_time = db.Column(db.Datetime, default=datetime.utcnow)    #发布时间
    status = db.Column(db.Boolean, default=True)    #是否售出，1：在售 0：已售出

     #关联卖家（反向引用：User.books -> 该用户发布的所有书籍）
    seller = db.relationship('User', backref=db.backref('books', lazy=True))\
    
def to_dict(self):
        """将模型转换为字典，用于接口返回"""
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'course_tag': self.course_tag,
            'major_tag': self.major_tag,
            'grade_tag': self.grade_tag,
            'condition': self.condition,
            'price': self.price,
            'description': self.description,
            'images': self.images.split(',') if self.images else [],
            'seller_id': self.seller_id,
            'seller_name': self.seller.username,  #关联查询卖家用户名
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M'),
            'status': self.status
        }