from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.config import Config
from flask_cors import CORS

#初始化数据库对象，全局可用
db = SQLAlchemy()
#初始化迁移对象，全局可用,用于同步模型到数据库表
migrate = Migrate()
def create_app(config_class=Config):
    app = Flask(__name__)   #Flask实例
    CORS(app, origins=["http://localhost:5173"], supports_credentials=True)

    #加载config
    app.config.from_object(config_class)
    CORS(app, supports_credentials=True, origins=["http://localhost:5173"]) #允许跨域请求
    #初始化数据库
    db.init_app(app)
    migrate.init_app(app,db)

    #导入User模型
    from app.models.user import User
    #导入Book模型
    from app.models.book import Book
    #导入Order模型
    from app.models.order import Order

    #注册路由蓝图
    from app.routes.user_routes import user_bp
    from app.routes.book_routes import book_bp
    from app.routes.order_routes import order_bp
    app.register_blueprint(user_bp) 
    app.register_blueprint(book_bp)
    app.register_blueprint(order_bp)
   
    #设置路由
    @app.route('/')
    def index():
        return "二手书交易平台后端正式启动"

    return app
#运行代码放到run.py中统一执行

