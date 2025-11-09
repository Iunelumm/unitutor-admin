# UniTutor Admin Panel - 部署指南

## 问题修复说明

### 原问题
`ModuleNotFoundError: This app has encountered an error` - 由于 `mysql.connector` 模块找不到

### 根本原因
`requirements.txt` 中的包名 `mysql-connector-python` 与代码中的 `import mysql.connector` 不匹配，导致 Streamlit Cloud 无法正确安装依赖。

### 修复内容
1. ✅ 更新 `requirements.txt` 到最新稳定版本
2. ✅ 添加 `python-dotenv` 支持环境变量
3. ✅ 优化数据库连接错误处理
4. ✅ 添加 Streamlit 配置文件
5. ✅ 添加 `.gitignore` 防止敏感信息泄露
6. ✅ 创建环境变量模板文件

---

## 部署到 Streamlit Cloud

### 步骤 1: 准备代码

```bash
# 进入管理员面板目录
cd unitutor-admin-main

# 初始化 Git 仓库（如果还没有）
git init

# 添加所有文件
git add .

# 提交更改
git commit -m "Fix dependencies and add deployment configuration"
```

### 步骤 2: 推送到 GitHub

```bash
# 创建新的 GitHub 仓库（在 GitHub 网站上创建）
# 然后关联远程仓库
git remote add origin https://github.com/你的用户名/unitutor-admin.git

# 推送代码
git branch -M main
git push -u origin main
```

### 步骤 3: 部署到 Streamlit Cloud

1. 访问 [Streamlit Cloud](https://share.streamlit.io/)
2. 使用 GitHub 账号登录
3. 点击 "New app"
4. 选择你的仓库 `unitutor-admin`
5. 设置：
   - **Main file path**: `app.py`
   - **Python version**: 3.11

### 步骤 4: 配置环境变量

在 Streamlit Cloud 的 App settings 中，点击 "Secrets"，添加以下内容：

```toml
# Database Configuration
DB_HOST = "tramway.proxy.rlwy.net"
DB_PORT = "53965"
DB_USER = "root"
DB_PASSWORD = "aesZPoeaQuNokWDVsNWPXrxtmnVuOLgF"
DB_NAME = "railway"

# Admin Password
ADMIN_PASSWORD = "Bigmom@314"
```

⚠️ **重要**: 建议修改默认密码以提高安全性！

### 步骤 5: 部署完成

点击 "Deploy" 按钮，等待 2-3 分钟，你的管理员面板就会上线！

---

## 本地测试

如果想在本地测试：

```bash
# 安装依赖
pip install -r requirements.txt

# 创建 .env 文件
cp .env.example .env

# 编辑 .env 文件，填入你的数据库信息
nano .env

# 运行应用
streamlit run app.py
```

访问 http://localhost:8501 查看效果。

---

## 安全建议

### 1. 修改默认密码
在 Streamlit Cloud 的 Secrets 中修改 `ADMIN_PASSWORD`

### 2. 使用环境变量
不要在代码中硬编码敏感信息，始终使用环境变量

### 3. 限制访问
- Streamlit Cloud 的应用默认是公开的
- 使用强密码保护管理员面板
- 考虑使用 Streamlit 的身份验证功能

### 4. 数据库安全
- 确保数据库只允许来自 Streamlit Cloud 的连接
- 定期更换数据库密码
- 使用只读账户（如果只需要查询功能）

---

## 常见问题

### Q1: 部署后仍然报错？
**A**: 检查 Streamlit Cloud 的 Secrets 配置是否正确，确保所有环境变量都已设置。

### Q2: 数据库连接失败？
**A**: 
- 检查数据库主机地址和端口是否正确
- 确认数据库允许外部连接
- 检查防火墙设置

### Q3: 如何更新应用？
**A**: 
```bash
# 修改代码后
git add .
git commit -m "Update admin panel"
git push origin main
```
Streamlit Cloud 会自动检测更新并重新部署。

### Q4: 如何查看日志？
**A**: 在 Streamlit Cloud 的应用页面，点击右下角的 "Manage app" > "Logs"

---

## 技术栈

- **Frontend**: Streamlit 1.39.0
- **Database**: MySQL (via mysql-connector-python 9.1.0)
- **Data Processing**: Pandas 2.2.3
- **Environment**: Python 3.11

---

## 支持

如有问题，请检查：
1. Streamlit Cloud 的日志
2. 数据库连接状态
3. 环境变量配置

## 更新日志

### v1.1 (2024-11-08)
- ✅ 修复依赖问题
- ✅ 添加环境变量支持
- ✅ 优化错误处理
- ✅ 添加配置文件

### v1.0 (初始版本)
- 基础管理功能
- 用户管理
- 课程管理
- 争议处理
