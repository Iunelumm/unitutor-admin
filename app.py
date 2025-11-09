import streamlit as st
import mysql.connector
from mysql.connector import pooling
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# 页面配置
st.set_page_config(
    page_title="UniTutor Admin Dashboard",
    page_icon="📚",
    layout="wide"
)

# 数据库连接池配置
@st.cache_resource
def init_connection_pool():
    """初始化数据库连接池"""
    try:
        dbconfig = {
            "host": os.getenv("DB_HOST", "tramway.proxy.rlwy.net"),
            "port": int(os.getenv("DB_PORT", "53965")),
            "user": os.getenv("DB_USER", "root"),
            "password": os.getenv("DB_PASSWORD", "aesZPoeaQuNokWDVsNWPXrxtmnVuOLgF"),
            "database": os.getenv("DB_NAME", "railway"),
        }
        
        connection_pool = pooling.MySQLConnectionPool(
            pool_name="admin_pool",
            pool_size=5,
            pool_reset_session=True,
            **dbconfig
        )
        return connection_pool
    except mysql.connector.Error as err:
        st.error(f"数据库连接池初始化失败: {err}")
        return None

def get_db_connection():
    """从连接池获取数据库连接"""
    try:
        pool = init_connection_pool()
        if pool is None:
            return None
        connection = pool.get_connection()
        if connection.is_connected():
            return connection
        else:
            # 如果连接已断开，尝试重新连接
            connection.reconnect(attempts=3, delay=1)
            return connection
    except mysql.connector.Error as err:
        st.error(f"获取数据库连接失败: {err}")
        return None

def check_password():
    """密码验证"""
    def password_entered():
        admin_password = os.getenv("ADMIN_PASSWORD", "Bigmom@314")
        if st.session_state["password"] == admin_password:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input(
            "请输入管理员密码", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        st.text_input(
            "请输入管理员密码", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        st.error("❌ 密码错误")
        return False
    else:
        return True

def execute_query(query, params=None):
    """执行查询并返回结果"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None or not conn.is_connected():
            st.error("❌ 无法连接到数据库，请检查数据库配置")
            return pd.DataFrame()
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        
        # 获取所有结果
        results = cursor.fetchall()
        df = pd.DataFrame(results)
        
        return df
    except mysql.connector.Error as err:
        st.error(f"数据库查询错误: {err}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"执行查询时出错: {e}")
        return pd.DataFrame()
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def main():
    """主应用"""
    
    # 密码验证
    if not check_password():
        return
    
    # 侧边栏导航
    st.sidebar.title("📚 UniTutor Admin")
    st.sidebar.markdown("---")
    
    page = st.sidebar.radio(
        "导航",
        ["📊 平台统计", "👥 用户管理", "📅 课程管理", "⚠️ 争议处理", "💬 支持工单", "⭐ 评分管理"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info("💡 提示：点击表格可以查看详细信息")
    
    # 根据选择显示不同页面
    if page == "📊 平台统计":
        show_dashboard()
    elif page == "👥 用户管理":
        show_users()
    elif page == "📅 课程管理":
        show_courses()
    elif page == "⚠️ 争议处理":
        show_disputes()
    elif page == "💬 支持工单":
        show_support_tickets()
    elif page == "⭐ 评分管理":
        show_ratings()

def show_dashboard():
    """显示平台统计"""
    st.title("📊 平台统计")
    
    # 统计卡片
    col1, col2, col3, col4 = st.columns(4)
    
    # 总用户数
    total_users = execute_query("SELECT COUNT(*) as count FROM users")
    col1.metric("总用户数", total_users['count'].iloc[0] if not total_users.empty else 0)
    
    # 学生数
    students = execute_query("SELECT COUNT(*) as count FROM users WHERE role = 'user'")
    col2.metric("学生数", students['count'].iloc[0] if not students.empty else 0)
    
    # 教师数
    tutors = execute_query("SELECT COUNT(*) as count FROM tutorProfiles")
    col3.metric("教师数", tutors['count'].iloc[0] if not tutors.empty else 0)
    
    # 总课程数
    courses = execute_query("SELECT COUNT(*) as count FROM courses")
    col4.metric("总课程数", courses['count'].iloc[0] if not courses.empty else 0)
    
    st.markdown("---")
    
    # 课程状态统计
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 课程状态分布")
        course_status = execute_query("""
            SELECT status, COUNT(*) as count 
            FROM courses 
            GROUP BY status
        """)
        if not course_status.empty:
            st.bar_chart(course_status.set_index('status'))
        else:
            st.info("暂无课程数据")
    
    with col2:
        st.subheader("💰 最近收入统计")
        recent_income = execute_query("""
            SELECT DATE(createdAt) as date, SUM(price) as total
            FROM courses
            WHERE status = 'completed'
            AND createdAt >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            GROUP BY DATE(createdAt)
            ORDER BY date DESC
            LIMIT 10
        """)
        if not recent_income.empty:
            st.line_chart(recent_income.set_index('date'))
        else:
            st.info("暂无收入数据")

def show_users():
    """显示用户管理"""
    st.title("👥 用户管理")
    
    # 搜索框
    search = st.text_input("🔍 搜索用户（姓名或邮箱）", "")
    
    # 筛选
    col1, col2 = st.columns(2)
    with col1:
        role_filter = st.selectbox("角色筛选", ["全部", "学生", "教师", "管理员"])
    with col2:
        sort_by = st.selectbox("排序方式", ["最新注册", "最近登录", "姓名"])
    
    # 构建查询
    query = "SELECT id, name, email, role, loginMethod, createdAt, lastSignedIn FROM users WHERE 1=1"
    params = []
    
    if search:
        query += " AND (name LIKE %s OR email LIKE %s)"
        params.extend([f"%{search}%", f"%{search}%"])
    
    if role_filter != "全部":
        role_map = {"学生": "user", "教师": "user", "管理员": "admin"}
        query += " AND role = %s"
        params.append(role_map[role_filter])
    
    # 排序
    if sort_by == "最新注册":
        query += " ORDER BY createdAt DESC"
    elif sort_by == "最近登录":
        query += " ORDER BY lastSignedIn DESC"
    else:
        query += " ORDER BY name"
    
    query += " LIMIT 100"
    
    # 执行查询
    users = execute_query(query, params if params else None)
    
    if not users.empty:
        st.dataframe(
            users,
            use_container_width=True,
            hide_index=True
        )
        st.caption(f"显示 {len(users)} 个用户")
    else:
        st.info("没有找到用户")

def show_courses():
    """显示课程管理"""
    st.title("📅 课程管理")
    
    # 状态筛选
    status_filter = st.selectbox(
        "课程状态",
        ["全部", "待确认", "已确认", "已完成", "已取消", "有争议"]
    )
    
    # 构建查询
    query = """
        SELECT 
            c.id,
            c.status,
            s.name as student_name,
            t.name as tutor_name,
            c.subject,
            c.startTime,
            c.duration,
            c.price,
            c.createdAt
        FROM courses c
        LEFT JOIN users s ON c.studentId = s.id
        LEFT JOIN users t ON c.tutorId = t.id
        WHERE 1=1
    """
    params = []
    
    if status_filter != "全部":
        status_map = {
            "待确认": "pending",
            "已确认": "confirmed",
            "已完成": "completed",
            "已取消": "cancelled",
            "有争议": "disputed"
        }
        query += " AND c.status = %s"
        params.append(status_map[status_filter])
    
    query += " ORDER BY c.createdAt DESC LIMIT 100"
    
    # 执行查询
    courses = execute_query(query, params if params else None)
    
    if not courses.empty:
        st.dataframe(
            courses,
            use_container_width=True,
            hide_index=True
        )
        st.caption(f"显示 {len(courses)} 个课程")
    else:
        st.info("没有找到课程")

def show_disputes():
    """显示争议处理"""
    st.title("⚠️ 争议处理")
    
    query = """
        SELECT 
            c.id,
            s.name as student_name,
            t.name as tutor_name,
            c.subject,
            c.startTime,
            c.price,
            c.disputeReason,
            c.createdAt
        FROM courses c
        LEFT JOIN users s ON c.studentId = s.id
        LEFT JOIN users t ON c.tutorId = t.id
        WHERE c.status = 'disputed'
        ORDER BY c.createdAt DESC
    """
    
    disputes = execute_query(query)
    
    if not disputes.empty:
        st.warning(f"⚠️ 当前有 {len(disputes)} 个争议需要处理")
        st.dataframe(
            disputes,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success("✅ 暂无争议课程")

def show_support_tickets():
    """显示支持工单"""
    st.title("💬 支持工单")
    
    # 状态筛选
    status_filter = st.selectbox("工单状态", ["全部", "待处理", "处理中", "已解决"])
    
    query = """
        SELECT 
            st.id,
            st.status,
            u.name as user_name,
            u.email,
            st.subject,
            st.message,
            st.createdAt
        FROM supportTickets st
        LEFT JOIN users u ON st.userId = u.id
        WHERE 1=1
    """
    params = []
    
    if status_filter != "全部":
        status_map = {"待处理": "open", "处理中": "in_progress", "已解决": "resolved"}
        query += " AND st.status = %s"
        params.append(status_map[status_filter])
    
    query += " ORDER BY st.createdAt DESC LIMIT 100"
    
    tickets = execute_query(query, params if params else None)
    
    if not tickets.empty:
        st.dataframe(
            tickets,
            use_container_width=True,
            hide_index=True
        )
        st.caption(f"显示 {len(tickets)} 个工单")
    else:
        st.info("没有找到工单")

def show_ratings():
    """显示评分管理"""
    st.title("⭐ 评分管理")
    
    query = """
        SELECT 
            r.id,
            r.score,
            r.comment,
            r.visibility,
            rater.name as rater_name,
            rated.name as rated_name,
            c.subject,
            r.createdAt
        FROM ratings r
        LEFT JOIN users rater ON r.raterId = rater.id
        LEFT JOIN users rated ON r.ratedUserId = rated.id
        LEFT JOIN courses c ON r.courseId = c.id
        ORDER BY r.createdAt DESC
        LIMIT 100
    """
    
    ratings = execute_query(query)
    
    if not ratings.empty:
        # 平均分统计
        avg_score = ratings['score'].mean()
        st.metric("平均评分", f"{avg_score:.2f} / 5.0")
        
        st.markdown("---")
        
        st.dataframe(
            ratings,
            use_container_width=True,
            hide_index=True
        )
        st.caption(f"显示 {len(ratings)} 个评分")
    else:
        st.info("暂无评分数据")

if __name__ == "__main__":
    main()
