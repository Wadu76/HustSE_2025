#本脚本统一管理项目的配置信息
import os
from dotenv import load_dotenv #加载.env文件中的配置信息

load_dotenv()  #加载.env文件中的配置信息以让python读到数据库uri

class Config:
    #从env获取数据库地址
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')

    #查询得知开发阶段不需要SQLAlchemy跟踪修改功能，避免额外内存消耗
    SQLALCHEMY_TRACK_MODIFICATIONS = False