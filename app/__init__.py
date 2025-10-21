from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.config import Config

#初始化数据库对象，全局可用
db = SQLAlchemy()
#初始化迁移对象，全局可用,用于同步模型到数据库表
migrate = Migrate()
def create_app():
    app = Flask(__name__)   #Flask实例

    #加载config
    app.config.from_object(Config)

    #初始化数据库
    db.init_app(app)
    migrate.init_app(app,db)

    #导入User模型
    from app.models.user import User
    #设置路由
    @app.route('/')
    def index():
        return "二手书交易平台后端正式启动"

    return app
#运行代码放到run.py中统一执行

