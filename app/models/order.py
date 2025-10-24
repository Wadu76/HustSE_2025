from datetime import datetime
import random   #生成随机订单号
from app import db

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)  #订单id 主键
    order_no = db.Column(db.String(32), unique=True, nullable=False)    #唯一订单号，用于查询
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)    #买家id 关联用户表
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)    #卖家id 关联用户表,用户可以是买家也可以是卖家
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)    #书籍id 关联书籍表
    price = db.Column(db.Float, nullable=False)    #交易价格
    status = db.Column(db.SmallInteger, nullable=False)     #订单状态：1-待支付，2-已支付，3-已发货，4-已收货，5-已完成
    create_time = db.Column(db.DateTime, default=datetime.now)  #订单创建时间

    #关联关系，方便查询
    #买家：通过buyer_id 关联User模型，反向引用为buyer_orders (用户作为买家的所有订单)
    buyer = db.relationship('User', foreign_keys=[buyer_id], backref=db.backref('buyer_orders', lazy=True))
    #卖家：通过seller_id 关联User模型，反向引用为seller_orders (用户作为卖家的所有订单)
    seller = db.relationship('User', foreign_keys=[seller_id], backref=db.backref('seller_orders', lazy=True))
    #shu籍：通过book_id 关联Book模型，反向引用为orders (书籍的所有订单)
    book = db.relationship('Book', backref=db.backref('orders', lazy=True))

    def to_dict(self):
        #将模型对象转换为字典，用于接口返回
        return{
            'id': self.id,
            'order_no': self.order_no,
            'buyer_id': self.buyer_id,
            'buyer_name': self.buyer.username,      #关联查询买家用户名
            'seller_id': self.seller_id,
            'seller_name': self.seller.username,    #关联查询买家用户名
            'book_id': self.book_id,
            'book_title': self.book.title,         #关联查询书籍标题
            'price': self.price,
            'status': self.status,
            #状态文本
            'status_text': self.get_status_text(),
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M')
        }
    
    def get_status_text(self):
        #将状态码转换为文本描述
        status_map = {
            1: '待支付',
            2: '已支付',
            3: '已发货',
            4: '已收货',
            5: '已完成'
        }
        return status_map.get(self.status, '未知状态')