#app/modles/user.py：用户表模型,数据库的users表
from datetime import datetime #时间库
from werkzeug.security import generate_password_hash, check_password_hash #密码加密
from app import db #引入数据库实例

class User(db.Model):
    #表名 users
    __tablename__ = 'users'

    #字段定义部分
    id = db.Column(db.Integer, primary_key=True)    #主键ID
    phone = db.Column(db.String(11), unique=True) #手机号,唯一不重复
    #password = db.Column(db.String(100)) #密码
    #password_hash = db.Column(db.String(128), nullable=False) #加密后的密码，不能为空
    password_hash = db.Column(db.String(256), nullable=False) #加密后的密码，不能为空
    #增加为256，留足冗余，因为生成的哈希值会超过128
    username = db.Column(db.String(50)) #用户名
    identity = db.Column(db.String(20), default='buyer') #用户身份，默认为买家
    major = db.Column(db.String(20))    #专业,可选
    grade = db.Column(db.String(20))    #年级,可选
    credit = db.Column(db.Integer, default = 100) #信用分，默认100
    create_time = db.Column(db.DateTime, default=datetime.now) #创建时间，默认为当前时间
    #now() 加了 () 会导致默认值固定为服务器启动的时间。
    #密码加密
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        #generate_password_hash():把明文密码加密成哈希值

    #密码验证
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        #check_password_hash():检查密码是否正确

    def to_dict(self):
        #返回用户信息字典
        return {
            
        }