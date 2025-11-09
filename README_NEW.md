# UniTutor Admin Dashboard 🎓

管理员控制面板 - 用于管理 UniTutor 平台的用户、课程、争议和支持工单。

## ✨ 功能特性

- 📊 **平台统计**: 实时查看用户数、课程数、收入统计
- 👥 **用户管理**: 搜索、筛选和管理学生与教师
- 📅 **课程管理**: 查看和管理所有课程状态
- ⚠️ **争议处理**: 处理课程相关的争议
- 💬 **支持工单**: 管理用户提交的支持请求
- ⭐ **评分管理**: 查看和管理用户评分

## 🚀 快速开始

### 在线部署（推荐）

1. **Fork 或上传代码到 GitHub**
2. **访问 [Streamlit Cloud](https://share.streamlit.io/)**
3. **连接你的 GitHub 仓库**
4. **配置环境变量**（见下方）
5. **点击 Deploy**

### 本地运行

```bash
# 克隆仓库
git clone https://github.com/你的用户名/unitutor-admin.git
cd unitutor-admin

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的配置

# 运行应用
streamlit run app.py
```

## 🔧 环境变量配置

### 方法 1: Streamlit Cloud Secrets

在 Streamlit Cloud 的 App Settings > Secrets 中添加：

```toml
DB_HOST = "your_database_host"
DB_PORT = "your_database_port"
DB_USER = "your_database_user"
DB_PASSWORD = "your_database_password"
DB_NAME = "your_database_name"
ADMIN_PASSWORD = "your_admin_password"
```

### 方法 2: 本地 .env 文件

创建 `.env` 文件：

```env
DB_HOST=your_database_host
DB_PORT=your_database_port
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_NAME=your_database_name
ADMIN_PASSWORD=your_admin_password
```

## 🔒 安全提示

- ⚠️ **不要**将 `.env` 或 `secrets.toml` 提交到 Git
- ✅ 使用强密码保护管理员面板
- ✅ 定期更换数据库密码
- ✅ 限制数据库访问 IP

## 📦 依赖项

- `streamlit==1.39.0` - Web 应用框架
- `mysql-connector-python==9.1.0` - MySQL 数据库连接
- `pandas==2.2.3` - 数据处理
- `python-dotenv==1.0.1` - 环境变量管理

## 🐛 问题修复

### ✅ 已修复的问题

- **ModuleNotFoundError**: 更新了 requirements.txt，确保依赖正确安装
- **数据库连接**: 添加了错误处理和连接超时设置
- **环境变量**: 支持通过 .env 文件或 Streamlit Secrets 配置

## 📖 详细文档

查看 [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) 获取完整的部署指南。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可

MIT License

---

**注意**: 这是一个管理员工具，请妥善保管访问链接和密码。
