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
            st.error("❌ 无法连接到数据库")
            return pd.DataFrame()
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
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

def execute_update(query, params=None):
    """执行更新操作（INSERT, UPDATE, DELETE）"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None or not conn.is_connected():
            st.error("❌ 无法连接到数据库")
            return False
        
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        conn.commit()
        return True
    except mysql.connector.Error as err:
        st.error(f"数据库更新错误: {err}")
        if conn:
            conn.rollback()
        return False
    except Exception as e:
        st.error(f"执行更新时出错: {e}")
        if conn:
            conn.rollback()
        return False
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
        ["📊 平台统计", "👥 用户管理", "📅 会话管理", "⚠️ 争议处理", "💬 支持工单", "⭐ 评分管理", "🎯 管理员评分"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info("💡 提示：点击用户可查看详细信息")
    
    # 根据选择显示不同页面
    if page == "📊 平台统计":
        show_dashboard()
    elif page == "👥 用户管理":
        show_users()
    elif page == "📅 会话管理":
        show_sessions()
    elif page == "⚠️ 争议处理":
        show_disputes()
    elif page == "💬 支持工单":
        show_support_tickets()
    elif page == "⭐ 评分管理":
        show_ratings()
    elif page == "🎯 管理员评分":
        show_admin_rating()

def show_dashboard():
    """显示平台统计"""
    st.title("📊 平台统计")
    
    # 统计卡片
    col1, col2, col3, col4 = st.columns(4)
    
    # 总用户数
    total_users = execute_query("SELECT COUNT(*) as count FROM users")
    col1.metric("总用户数", total_users['count'].iloc[0] if not total_users.empty else 0)
    
    # 学生数
    students = execute_query("SELECT COUNT(DISTINCT userId) as count FROM profiles WHERE userRole = 'student'")
    col2.metric("学生数", students['count'].iloc[0] if not students.empty else 0)
    
    # 教师数
    tutors = execute_query("SELECT COUNT(DISTINCT userId) as count FROM profiles WHERE userRole = 'tutor'")
    col3.metric("教师数", tutors['count'].iloc[0] if not tutors.empty else 0)
    
    # 总会话数
    sessions_count = execute_query("SELECT COUNT(*) as count FROM sessions")
    col4.metric("总会话数", sessions_count['count'].iloc[0] if not sessions_count.empty else 0)
    
    st.markdown("---")
    
    # 会话状态统计
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 会话状态分布")
        session_status = execute_query("""
            SELECT status, COUNT(*) as count 
            FROM sessions 
            GROUP BY status
        """)
        if not session_status.empty:
            st.bar_chart(session_status.set_index('status'))
        else:
            st.info("暂无会话数据")
    
    with col2:
        st.subheader("📅 最近会话统计")
        recent_sessions = execute_query("""
            SELECT DATE(createdAt) as date, COUNT(*) as count
            FROM sessions
            WHERE createdAt >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            GROUP BY DATE(createdAt)
            ORDER BY date DESC
            LIMIT 10
        """)
        if not recent_sessions.empty:
            st.line_chart(recent_sessions.set_index('date'))
        else:
            st.info("暂无会话数据")

def show_users():
    """显示用户管理"""
    st.title("👥 用户管理")
    
    # 搜索框
    search = st.text_input("🔍 搜索用户（姓名或邮箱）", "")
    
    # 筛选
    col1, col2 = st.columns(2)
    with col1:
        role_filter = st.selectbox("角色筛选", ["全部", "学生", "教师", "两者都是"])
    with col2:
        sort_by = st.selectbox("排序方式", ["最新注册", "最近登录", "姓名"])
    
    # 构建查询
    query = "SELECT id, name, email, role, preferredRoles, createdAt, lastSignedIn FROM users WHERE 1=1"
    params = []
    
    if search:
        query += " AND (name LIKE %s OR email LIKE %s)"
        params.extend([f"%{search}%", f"%{search}%"])
    
    if role_filter != "全部":
        role_map = {"学生": "student", "教师": "tutor", "两者都是": "both"}
        query += " AND preferredRoles = %s"
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
        
        # 用户详情查看
        st.markdown("---")
        st.subheader("📋 查看用户详细信息")
        
        user_id = st.number_input("输入用户 ID 查看详情", min_value=1, step=1, key="user_detail_id")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("查看详情", type="primary"):
                show_user_detail(user_id)
        with col2:
            if st.button("🗑️ 删除用户", type="secondary"):
                delete_user(user_id)
    else:
        st.info("没有找到用户")

def show_user_detail(user_id):
    """显示用户详细信息"""
    st.markdown("---")
    st.subheader(f"👤 用户 #{user_id} 详细信息")
    
    # 基本信息
    user_info = execute_query("SELECT * FROM users WHERE id = %s", (user_id,))
    if user_info.empty:
        st.error("用户不存在")
        return
    
    user = user_info.iloc[0]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("姓名", user['name'] or "未设置")
        st.metric("邮箱", user['email'] or "未设置")
    with col2:
        st.metric("角色", user['preferredRoles'] or "未设置")
        st.metric("登录方式", user['loginMethod'] or "未知")
    with col3:
        st.metric("注册时间", str(user['createdAt'])[:10])
        st.metric("最后登录", str(user['lastSignedIn'])[:10])
    
    # 个人资料
    profiles = execute_query("SELECT * FROM profiles WHERE userId = %s", (user_id,))
    if not profiles.empty:
        st.markdown("### 📝 个人资料")
        for idx, profile in profiles.iterrows():
            with st.expander(f"{profile['userRole'].upper()} 资料"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**专业**: {profile['major'] or '未设置'}")
                    st.write(f"**年级**: {profile['year'] or '未设置'}")
                    if profile['userRole'] == 'tutor':
                        st.write(f"**价格范围**: ${profile['priceMin']} - ${profile['priceMax']}")
                with col2:
                    st.write(f"**积分**: {profile['creditPoints']}")
                    st.write(f"**简介**: {profile['bio'] or '无'}")
    
    # 会话统计
    st.markdown("### 📊 会话统计")
    col1, col2, col3, col4 = st.columns(4)
    
    # 作为学生的会话
    student_sessions = execute_query("""
        SELECT 
            COUNT(*) as total,
            COALESCE(SUM(CASE WHEN status = 'CLOSED' THEN 1 ELSE 0 END), 0) as completed,
            COALESCE(SUM(CASE WHEN status = 'CANCELLED' THEN 1 ELSE 0 END), 0) as cancelled,
            COALESCE(SUM(CASE WHEN status = 'DISPUTED' THEN 1 ELSE 0 END), 0) as disputed
        FROM sessions WHERE studentId = %s
    """, (user_id,))
    
    if not student_sessions.empty:
        s = student_sessions.iloc[0]
        col1.metric("学生会话总数", int(s['total']) if s['total'] is not None else 0)
        col2.metric("已完成", int(s['completed']) if s['completed'] is not None else 0)
        col3.metric("已取消", int(s['cancelled']) if s['cancelled'] is not None else 0)
        col4.metric("有争议", int(s['disputed']) if s['disputed'] is not None else 0)
    
    # 作为教师的会话
    tutor_sessions = execute_query("""
        SELECT 
            COUNT(*) as total,
            COALESCE(SUM(CASE WHEN status = 'CLOSED' THEN 1 ELSE 0 END), 0) as completed,
            COALESCE(SUM(CASE WHEN status = 'CANCELLED' THEN 1 ELSE 0 END), 0) as cancelled,
            COALESCE(SUM(CASE WHEN status = 'DISPUTED' THEN 1 ELSE 0 END), 0) as disputed
        FROM sessions WHERE tutorId = %s
    """, (user_id,))
    
    if not tutor_sessions.empty:
        st.markdown("#### 作为教师")
        col1, col2, col3, col4 = st.columns(4)
        t = tutor_sessions.iloc[0]
        col1.metric("教师会话总数", int(t['total']) if t['total'] is not None else 0)
        col2.metric("已完成", int(t['completed']) if t['completed'] is not None else 0)
        col3.metric("已取消", int(t['cancelled']) if t['cancelled'] is not None else 0)
        col4.metric("有争议", int(t['disputed']) if t['disputed'] is not None else 0)
    
    # 评分统计
    st.markdown("### ⭐ 评分统计")
    ratings_received = execute_query("""
        SELECT AVG(score) as avg_score, COUNT(*) as count
        FROM ratings WHERE targetId = %s
    """, (user_id,))
    
    if not ratings_received.empty and ratings_received.iloc[0]['count'] > 0:
        r = ratings_received.iloc[0]
        col1, col2 = st.columns(2)
        col1.metric("平均评分", f"{float(r['avg_score']):.2f} / 5.0")
        col2.metric("评分数量", int(r['count']))
    else:
        st.info("暂无评分")
    
    # 最近会话
    st.markdown("### 📅 最近会话")
    recent_sessions = execute_query("""
        SELECT 
            s.id, s.course, s.status, s.startTime,
            CASE 
                WHEN s.studentId = %s THEN CONCAT('教师: ', tutor.name)
                ELSE CONCAT('学生: ', student.name)
            END as partner
        FROM sessions s
        LEFT JOIN users student ON s.studentId = student.id
        LEFT JOIN users tutor ON s.tutorId = tutor.id
        WHERE s.studentId = %s OR s.tutorId = %s
        ORDER BY s.createdAt DESC
        LIMIT 10
    """, (user_id, user_id, user_id))
    
    if not recent_sessions.empty:
        st.dataframe(recent_sessions, use_container_width=True, hide_index=True)
    else:
        st.info("暂无会话记录")

def delete_user(user_id):
    """删除用户（软删除）"""
    st.markdown("---")
    st.warning(f"⚠️ 确认要删除用户 #{user_id} 吗？")
    st.write("此操作将：")
    st.write("- 将用户角色标记为已删除")
    st.write("- 保留历史数据用于审计")
    st.write("- 用户将无法登录")
    
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        if st.button("✅ 确认删除", type="primary", key=f"confirm_delete_{user_id}"):
            # 软删除：更新用户名为 "已删除用户"
            success = execute_update("""
                UPDATE users 
                SET name = CONCAT('已删除用户_', id),
                    email = CONCAT('deleted_', id, '@deleted.com'),
                    role = 'user'
                WHERE id = %s
            """, (user_id,))
            
            if success:
                st.success(f"✅ 用户 #{user_id} 已删除")
                st.rerun()
            else:
                st.error("删除失败")
    with col2:
        if st.button("❌ 取消", key=f"cancel_delete_{user_id}"):
            st.info("已取消删除操作")

def show_sessions():
    """显示会话管理"""
    st.title("📅 会话管理")
    
    status_filter = st.selectbox(
        "会话状态",
        ["全部", "待确认", "已确认", "待评分", "有争议", "已关闭", "已取消"]
    )
    
    query = """
        SELECT 
            s.id,
            s.status,
            student.name as student_name,
            tutor.name as tutor_name,
            s.course,
            s.startTime,
            s.endTime,
            s.studentCompleted,
            s.tutorCompleted,
            s.createdAt
        FROM sessions s
        LEFT JOIN users student ON s.studentId = student.id
        LEFT JOIN users tutor ON s.tutorId = tutor.id
        WHERE 1=1
    """
    params = []
    
    if status_filter != "全部":
        status_map = {
            "待确认": "PENDING",
            "已确认": "CONFIRMED",
            "待评分": "PENDING_RATING",
            "有争议": "DISPUTED",
            "已关闭": "CLOSED",
            "已取消": "CANCELLED"
        }
        query += " AND s.status = %s"
        params.append(status_map[status_filter])
    
    query += " ORDER BY s.createdAt DESC LIMIT 100"
    
    sessions = execute_query(query, params if params else None)
    
    if not sessions.empty:
        st.dataframe(sessions, use_container_width=True, hide_index=True)
        st.caption(f"显示 {len(sessions)} 个会话")
    else:
        st.info("没有找到会话")

def show_disputes():
    """显示争议处理"""
    st.title("⚠️ 争议处理")
    
    query = """
        SELECT 
            s.id,
            student.name as student_name,
            tutor.name as tutor_name,
            s.course,
            s.startTime,
            s.endTime,
            s.cancelReason,
            s.createdAt
        FROM sessions s
        LEFT JOIN users student ON s.studentId = student.id
        LEFT JOIN users tutor ON s.tutorId = tutor.id
        WHERE s.status = 'DISPUTED'
        ORDER BY s.createdAt DESC
    """
    
    disputes = execute_query(query)
    
    if not disputes.empty:
        st.warning(f"⚠️ 当前有 {len(disputes)} 个争议需要处理")
        st.dataframe(disputes, use_container_width=True, hide_index=True)
    else:
        st.success("✅ 暂无争议会话")

def show_support_tickets():
    """显示支持工单"""
    st.title("💬 支持工单管理")
    
    status_filter = st.selectbox("工单状态", ["全部", "待处理", "处理中", "已解决"])
    
    query = """
        SELECT 
            t.id,
            t.status,
            t.category,
            u.name as user_name,
            u.email,
            u.id as user_id,
            t.subject,
            t.message,
            t.adminResponse,
            t.createdAt,
            t.updatedAt
        FROM tickets t
        LEFT JOIN users u ON t.userId = u.id
        WHERE 1=1
    """
    params = []
    
    if status_filter != "全部":
        status_map = {"待处理": "pending", "处理中": "in_progress", "已解决": "resolved"}
        query += " AND t.status = %s"
        params.append(status_map[status_filter])
    
    query += " ORDER BY t.createdAt DESC LIMIT 100"
    
    tickets = execute_query(query, params if params else None)
    
    if not tickets.empty:
        st.dataframe(tickets, use_container_width=True, hide_index=True)
        st.caption(f"显示 {len(tickets)} 个工单")
        
        # 工单回复功能
        st.markdown("---")
        st.subheader("📝 回复工单")
        
        ticket_id = st.number_input("输入工单 ID", min_value=1, step=1, key="ticket_id")
        
        # 显示工单详情
        ticket_detail = execute_query("SELECT * FROM tickets WHERE id = %s", (ticket_id,))
        if not ticket_detail.empty:
            ticket = ticket_detail.iloc[0]
            
            with st.expander("📋 工单详情", expanded=True):
                st.write(f"**用户**: {ticket['userId']}")
                st.write(f"**类别**: {ticket['category']}")
                st.write(f"**主题**: {ticket['subject']}")
                st.write(f"**内容**: {ticket['message']}")
                st.write(f"**当前状态**: {ticket['status']}")
                if ticket['adminResponse']:
                    st.write(f"**已有回复**: {ticket['adminResponse']}")
            
            # 回复表单
            col1, col2 = st.columns([3, 1])
            with col1:
                admin_response = st.text_area("管理员回复", key=f"response_{ticket_id}")
            with col2:
                new_status = st.selectbox("更新状态", ["pending", "in_progress", "resolved"], 
                                         index=["pending", "in_progress", "resolved"].index(ticket['status']))
            
            if st.button("💾 提交回复", type="primary"):
                if admin_response:
                    success = execute_update("""
                        UPDATE tickets 
                        SET adminResponse = %s, status = %s, updatedAt = NOW()
                        WHERE id = %s
                    """, (admin_response, new_status, ticket_id))
                    
                    if success:
                        st.success("✅ 回复已提交")
                        st.rerun()
                    else:
                        st.error("提交失败")
                else:
                    st.warning("请输入回复内容")
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
            target.name as target_name,
            target.id as target_id,
            s.course,
            r.createdAt
        FROM ratings r
        LEFT JOIN users rater ON r.raterId = rater.id
        LEFT JOIN users target ON r.targetId = target.id
        LEFT JOIN sessions s ON r.sessionId = s.id
        ORDER BY r.createdAt DESC
        LIMIT 100
    """
    
    ratings = execute_query(query)
    
    if not ratings.empty:
        # 平均分统计
        avg_score = ratings['score'].mean()
        st.metric("平均评分", f"{avg_score:.2f} / 5.0")
        
        st.markdown("---")
        
        st.dataframe(ratings, use_container_width=True, hide_index=True)
        st.caption(f"显示 {len(ratings)} 个评分")
    else:
        st.info("暂无评分数据")

def show_admin_rating():
    """管理员评分系统 - 50% 权重"""
    st.title("🎯 管理员评分系统")
    
    st.info("💡 管理员评分占用户总评分的 50% 权重，其他用户评分占 50% 权重")
    
    # 创建管理员评分表（如果不存在）
    create_admin_rating_table()
    
    # 用户搜索
    st.subheader("1️⃣ 选择要评分的用户")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        search_user = st.text_input("搜索用户（姓名或邮箱）", key="admin_rating_search")
    with col2:
        user_id_direct = st.number_input("或直接输入用户 ID", min_value=1, step=1, key="admin_rating_user_id")
    
    # 搜索用户
    if search_user:
        users = execute_query("""
            SELECT id, name, email, preferredRoles 
            FROM users 
            WHERE name LIKE %s OR email LIKE %s
            LIMIT 10
        """, (f"%{search_user}%", f"%{search_user}%"))
        
        if not users.empty:
            st.dataframe(users, use_container_width=True, hide_index=True)
    
    # 评分表单
    st.markdown("---")
    st.subheader("2️⃣ 提交管理员评分")
    
    target_user_id = user_id_direct if user_id_direct > 0 else None
    
    if target_user_id:
        # 显示用户当前评分
        user_info = execute_query("SELECT name, email FROM users WHERE id = %s", (target_user_id,))
        if not user_info.empty:
            user = user_info.iloc[0]
            st.write(f"**评分对象**: {user['name']} ({user['email']})")
            
            # 显示当前评分
            current_ratings = get_weighted_rating(target_user_id)
            col1, col2, col3 = st.columns(3)
            col1.metric("用户平均评分", f"{current_ratings['user_avg']:.2f}")
            col2.metric("管理员评分", f"{current_ratings['admin_score']:.2f}" if current_ratings['admin_score'] else "未评分")
            col3.metric("最终加权评分", f"{current_ratings['final_score']:.2f}")
            
            st.markdown("---")
            
            # 评分输入
            col1, col2 = st.columns([1, 2])
            with col1:
                admin_score = st.slider("评分 (1-5)", 1, 5, 3, key="admin_score_slider")
            with col2:
                admin_comment = st.text_area("评价说明（可选）", key="admin_comment")
            
            if st.button("💾 提交管理员评分", type="primary"):
                # 检查是否已有管理员评分
                existing = execute_query("""
                    SELECT id FROM adminRatings WHERE targetUserId = %s
                """, (target_user_id,))
                
                if not existing.empty:
                    # 更新现有评分
                    success = execute_update("""
                        UPDATE adminRatings 
                        SET score = %s, comment = %s, updatedAt = NOW()
                        WHERE targetUserId = %s
                    """, (admin_score, admin_comment, target_user_id))
                else:
                    # 插入新评分
                    success = execute_update("""
                        INSERT INTO adminRatings (targetUserId, score, comment, createdAt, updatedAt)
                        VALUES (%s, %s, %s, NOW(), NOW())
                    """, (target_user_id, admin_score, admin_comment))
                
                if success:
                    st.success("✅ 管理员评分已提交")
                    st.rerun()
                else:
                    st.error("提交失败")
        else:
            st.error("用户不存在")
    else:
        st.info("请选择或输入要评分的用户")
    
    # 显示所有管理员评分
    st.markdown("---")
    st.subheader("📋 所有管理员评分")
    
    admin_ratings = execute_query("""
        SELECT 
            ar.id,
            u.name as user_name,
            u.email,
            ar.score,
            ar.comment,
            ar.createdAt,
            ar.updatedAt
        FROM adminRatings ar
        LEFT JOIN users u ON ar.targetUserId = u.id
        ORDER BY ar.updatedAt DESC
    """)
    
    if not admin_ratings.empty:
        st.dataframe(admin_ratings, use_container_width=True, hide_index=True)
    else:
        st.info("暂无管理员评分")

def create_admin_rating_table():
    """创建管理员评分表"""
    execute_update("""
        CREATE TABLE IF NOT EXISTS adminRatings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            targetUserId INT NOT NULL,
            score INT NOT NULL,
            comment TEXT,
            createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY unique_target (targetUserId)
        )
    """)

def get_weighted_rating(user_id):
    """计算加权评分：管理员评分 50% + 用户评分 50%"""
    # 获取用户平均评分
    user_ratings = execute_query("""
        SELECT AVG(score) as avg_score, COUNT(*) as count
        FROM ratings WHERE targetId = %s
    """, (user_id,))
    
    user_avg = float(user_ratings.iloc[0]['avg_score']) if not user_ratings.empty and user_ratings.iloc[0]['avg_score'] else 0
    
    # 获取管理员评分
    admin_rating = execute_query("""
        SELECT score FROM adminRatings WHERE targetUserId = %s
    """, (user_id,))
    
    admin_score = float(admin_rating.iloc[0]['score']) if not admin_rating.empty else None
    
    # 计算最终评分
    if admin_score is not None:
        final_score = (admin_score * 0.5) + (user_avg * 0.5)
    else:
        final_score = user_avg
    
    return {
        'user_avg': user_avg,
        'admin_score': admin_score,
        'final_score': final_score
    }

if __name__ == "__main__":
    main()
