# UniTutor Admin Dashboard (Python + Streamlit)

简单、可靠的管理员后台，使用 Python + Streamlit 构建。

## 功能特性

- ✅ 密码保护登录
- ✅ 平台统计（用户数、课程数、收入等）
- ✅ 用户管理（搜索、筛选）
- ✅ 课程管理（查看所有课程）
- ✅ 争议处理（查看有争议的课程）
- ✅ 支持工单（查看用户问题）
- ✅ 评分管理（查看所有评分）

## 本地运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行应用

```bash
streamlit run app.py
```

### 3. 访问

打开浏览器访问：http://localhost:8501

输入密码：`Bigmom@314`

## 部署到 Streamlit Cloud（推荐）

### 优势
- ✅ 完全免费
- ✅ 自动部署
- ✅ 自动 HTTPS
- ✅ 无需配置服务器

### 步骤

#### 1. 上传到 GitHub

1. 访问：https://github.com/new
2. 创建新仓库：`unitutor-admin-python`
3. 设置为 Private
4. 上传所有文件：
   - `app.py`
   - `requirements.txt`
   - `.streamlit/config.toml`
   - `README.md`

#### 2. 部署到 Streamlit Cloud

1. 访问：https://share.streamlit.io
2. 点击 "New app"
3. 连接 GitHub 账号
4. 选择仓库：`unitutor-admin-python`
5. 主文件路径：`app.py`
6. 点击 "Deploy"

#### 3. 配置环境变量（可选）

如果需要修改数据库连接，在 Streamlit Cloud 的 "Advanced settings" 中添加：

```
DB_HOST=tramway.proxy.rlwy.net
DB_PORT=53965
DB_USER=root
DB_PASSWORD=aesZPoeaQuNokWDVsNWPXrxtmnVuOLgF
DB_NAME=railway
```

#### 4. 完成！

部署完成后，你会得到一个公开网址，例如：
`https://unitutor-admin.streamlit.app`

## 部署到 Railway（备选）

### 步骤

1. 上传代码到 GitHub（同上）

2. 在 Railway 创建新项目：
   - 选择 "Deploy from GitHub repo"
   - 选择你的仓库

3. 添加环境变量（同上）

4. Railway 会自动检测到这是 Python 应用并部署

5. 生成域名并访问

## 登录信息

- **密码**：`Bigmom@314`

## 数据库连接

默认连接到 Railway MySQL：
```
Host: tramway.proxy.rlwy.net
Port: 53965
User: root
Password: aesZPoeaQuNokWDVsNWPXrxtmnVuOLgF
Database: railway
```

## 技术栈

- **Python 3.11**
- **Streamlit** - Web 框架
- **mysql-connector-python** - MySQL 驱动
- **pandas** - 数据处理

## 优势

相比 Node.js 版本：
- ✅ **零构建问题** - 不需要编译
- ✅ **部署简单** - 一键部署
- ✅ **代码简洁** - 只有一个文件
- ✅ **稳定可靠** - Python 生态成熟

## 注意事项

- ⚠️ 不要分享数据库密码
- ⚠️ 定期更改管理员密码
- ⚠️ Streamlit Cloud 免费版有使用限制（足够个人使用）

