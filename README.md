## 这是个二手书交易平台网站的完整代码 ##
 启动前后端服务即可使用，后端所需库已在后端文件夹的requirement中列出。

# 项目启动说明

## 启动步骤

### 1. 启动后端服务
```bash
# 进入后端目录
cd backend

# 创建并激活虚拟环境（如果尚未创建）
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动Flask服务
flask run


# 打开新的管理员权限终端

# 进入前端目录
cd frontend

# 安装依赖（首次运行）
npm install

# 启动开发服务器
npm run dev
