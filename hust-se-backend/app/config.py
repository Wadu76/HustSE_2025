import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # 1. 【新增】你必须设置一个秘钥！
    #    Flask session 依赖这个秘钥来加密 cookie。
    #    请把它改成一个别人猜不到的随机字符串。
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-very-hard-to-guess-secret-key-12345'

    # ... 你已有的 SQLALCHEMY_DATABASE_URI ...
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    
    UPLOAD_FOLDER = os.path.join(basedir, 'static/uploads')
