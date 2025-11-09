# UniTutor 数据库结构文档

## 数据库表概览

你的 Railway MySQL 数据库包含以下 6 个表：

| 表名 | 用途 | 主要字段 |
|------|------|----------|
| `users` | 用户账户 | id, openId, name, email, role, preferredRoles |
| `profiles` | 学生/教师资料 | id, userId, userRole, major, courses, priceMin, priceMax |
| `sessions` | 辅导会话 | id, studentId, tutorId, course, startTime, status |
| `ratings` | 评分评价 | id, sessionId, raterId, targetId, score, comment |
| `tickets` | 支持工单 | id, userId, category, subject, message, status |
| `chatMessages` | 聊天消息 | id, sessionId, senderId, message |

---

## 详细表结构

### 1. users - 用户表

存储所有用户的基本账户信息。

**字段说明**:
- `id` (INT) - 主键，自增
- `openId` (VARCHAR 64) - OAuth 唯一标识，唯一索引
- `name` (TEXT) - 用户姓名
- `email` (VARCHAR 320) - 邮箱地址
- `loginMethod` (VARCHAR 64) - 登录方式（如 "google"）
- `role` (ENUM) - 系统角色：'user' 或 'admin'
- `preferredRoles` (VARCHAR 20) - 用户偏好角色：'student', 'tutor', 'both'
- `createdAt` (TIMESTAMP) - 创建时间
- `updatedAt` (TIMESTAMP) - 更新时间
- `lastSignedIn` (TIMESTAMP) - 最后登录时间

**常用查询**:
```sql
-- 统计总用户数
SELECT COUNT(*) FROM users;

-- 查找管理员
SELECT * FROM users WHERE role = 'admin';

-- 最近注册的用户
SELECT * FROM users ORDER BY createdAt DESC LIMIT 10;
```

---

### 2. profiles - 个人资料表

存储学生和教师的详细资料。

**字段说明**:
- `id` (INT) - 主键，自增
- `userId` (INT) - 外键，关联 users.id
- `userRole` (ENUM) - 'student' 或 'tutor'
- `age` (INT) - 年龄
- `year` (VARCHAR 50) - 年级（如 "Freshman"）
- `major` (VARCHAR 255) - 专业
- `bio` (TEXT) - 个人简介
- `priceMin` (INT) - 最低价格（仅教师）
- `priceMax` (INT) - 最高价格（仅教师）
- `courses` (JSON) - 课程列表，格式：["ECON 10A", "CHEM 109A"]
- `availability` (JSON) - 可用时间段
- `creditPoints` (INT) - 积分，默认 0
- `contactInfo` (TEXT) - 联系方式
- `createdAt` (TIMESTAMP) - 创建时间
- `updatedAt` (TIMESTAMP) - 更新时间

**常用查询**:
```sql
-- 统计教师数量
SELECT COUNT(DISTINCT userId) FROM profiles WHERE userRole = 'tutor';

-- 查找特定专业的学生
SELECT p.*, u.name, u.email 
FROM profiles p 
JOIN users u ON p.userId = u.id 
WHERE p.userRole = 'student' AND p.major LIKE '%Computer Science%';

-- 查找教授某课程的教师
SELECT p.*, u.name 
FROM profiles p 
JOIN users u ON p.userId = u.id 
WHERE p.userRole = 'tutor' 
AND JSON_CONTAINS(p.courses, '"ECON 10A"');
```

---

### 3. sessions - 会话表

存储辅导会话（课程预约）信息。

**字段说明**:
- `id` (INT) - 主键，自增
- `studentId` (INT) - 外键，关联 users.id（学生）
- `tutorId` (INT) - 外键，关联 users.id（教师）
- `course` (VARCHAR 255) - 课程名称
- `startTime` (TIMESTAMP) - 开始时间
- `endTime` (TIMESTAMP) - 结束时间
- `status` (ENUM) - 状态：
  - `PENDING` - 待确认
  - `CONFIRMED` - 已确认
  - `PENDING_RATING` - 待评分
  - `DISPUTED` - 有争议
  - `CLOSED` - 已关闭
  - `CANCELLED` - 已取消
- `studentCompleted` (BOOLEAN) - 学生是否标记完成
- `tutorCompleted` (BOOLEAN) - 教师是否标记完成
- `studentRated` (BOOLEAN) - 学生是否已评分
- `tutorRated` (BOOLEAN) - 教师是否已评分
- `cancelled` (BOOLEAN) - 是否已取消
- `cancelledBy` (INT) - 取消者 ID
- `cancelReason` (TEXT) - 取消原因
- `cancellationRated` (BOOLEAN) - 取消是否已评分
- `createdAt` (TIMESTAMP) - 创建时间
- `updatedAt` (TIMESTAMP) - 更新时间

**常用查询**:
```sql
-- 统计各状态会话数
SELECT status, COUNT(*) as count FROM sessions GROUP BY status;

-- 查找争议会话
SELECT s.*, 
       student.name as student_name, 
       tutor.name as tutor_name
FROM sessions s
JOIN users student ON s.studentId = student.id
JOIN users tutor ON s.tutorId = tutor.id
WHERE s.status = 'DISPUTED';

-- 最近30天的会话
SELECT * FROM sessions 
WHERE createdAt >= DATE_SUB(NOW(), INTERVAL 30 DAY)
ORDER BY createdAt DESC;
```

---

### 4. ratings - 评分表

存储用户之间的评分和评价。

**字段说明**:
- `id` (INT) - 主键，自增
- `sessionId` (INT) - 外键，关联 sessions.id
- `raterId` (INT) - 外键，评分者 ID
- `targetId` (INT) - 外键，被评分者 ID
- `score` (INT) - 评分（1-5）
- `comment` (TEXT) - 评价内容
- `visibility` (ENUM) - 'public' 或 'private'
- `createdAt` (TIMESTAMP) - 创建时间

**常用查询**:
```sql
-- 计算平均评分
SELECT AVG(score) as avg_score FROM ratings;

-- 查找某用户收到的评分
SELECT r.*, rater.name as rater_name 
FROM ratings r
JOIN users rater ON r.raterId = rater.id
WHERE r.targetId = 123;

-- 最近的公开评价
SELECT r.*, 
       rater.name as rater_name, 
       target.name as target_name,
       s.course
FROM ratings r
JOIN users rater ON r.raterId = rater.id
JOIN users target ON r.targetId = target.id
JOIN sessions s ON r.sessionId = s.id
WHERE r.visibility = 'public'
ORDER BY r.createdAt DESC;
```

---

### 5. tickets - 支持工单表

存储用户提交的支持请求。

**字段说明**:
- `id` (INT) - 主键，自增
- `userId` (INT) - 外键，关联 users.id
- `category` (ENUM) - 类别：
  - `account` - 账户问题
  - `matching` - 匹配问题
  - `cancellation` - 取消问题
  - `ratings` - 评分问题
  - `rules` - 规则问题
  - `technical` - 技术问题
- `subject` (VARCHAR 255) - 主题
- `message` (TEXT) - 详细描述
- `status` (ENUM) - 状态：'pending', 'in_progress', 'resolved'
- `adminResponse` (TEXT) - 管理员回复
- `createdAt` (TIMESTAMP) - 创建时间
- `updatedAt` (TIMESTAMP) - 更新时间

**常用查询**:
```sql
-- 待处理的工单
SELECT t.*, u.name, u.email 
FROM tickets t
JOIN users u ON t.userId = u.id
WHERE t.status = 'pending'
ORDER BY t.createdAt ASC;

-- 按类别统计工单
SELECT category, COUNT(*) as count 
FROM tickets 
GROUP BY category;
```

---

### 6. chatMessages - 聊天消息表

存储会话中的聊天记录。

**字段说明**:
- `id` (INT) - 主键，自增
- `sessionId` (INT) - 外键，关联 sessions.id
- `senderId` (INT) - 外键，发送者 ID
- `message` (TEXT) - 消息内容
- `sanitized` (BOOLEAN) - 是否已过滤，默认 false
- `createdAt` (TIMESTAMP) - 创建时间

**常用查询**:
```sql
-- 查看某会话的聊天记录
SELECT cm.*, u.name as sender_name
FROM chatMessages cm
JOIN users u ON cm.senderId = u.id
WHERE cm.sessionId = 123
ORDER BY cm.createdAt ASC;
```

---

## 表关系图

```
users (用户)
  ├─→ profiles (1对多: 一个用户可以有多个资料)
  ├─→ sessions (1对多: 作为学生或教师)
  ├─→ ratings (1对多: 作为评分者或被评分者)
  ├─→ tickets (1对多: 提交工单)
  └─→ chatMessages (1对多: 发送消息)

sessions (会话)
  ├─→ ratings (1对多: 一个会话可以有多个评分)
  └─→ chatMessages (1对多: 一个会话有多条消息)
```

---

## 管理员面板使用的查询

### 平台统计
```sql
-- 总用户数
SELECT COUNT(*) FROM users;

-- 学生数
SELECT COUNT(DISTINCT userId) FROM profiles WHERE userRole = 'student';

-- 教师数
SELECT COUNT(DISTINCT userId) FROM profiles WHERE userRole = 'tutor';

-- 总会话数
SELECT COUNT(*) FROM sessions;

-- 会话状态分布
SELECT status, COUNT(*) FROM sessions GROUP BY status;
```

### 用户管理
```sql
-- 搜索用户
SELECT id, name, email, role, preferredRoles, createdAt, lastSignedIn 
FROM users 
WHERE name LIKE '%keyword%' OR email LIKE '%keyword%'
ORDER BY createdAt DESC;
```

### 会话管理
```sql
-- 查看所有会话
SELECT s.id, s.status, 
       student.name as student_name,
       tutor.name as tutor_name,
       s.course, s.startTime, s.endTime
FROM sessions s
JOIN users student ON s.studentId = student.id
JOIN users tutor ON s.tutorId = tutor.id
ORDER BY s.createdAt DESC;
```

---

## 注意事项

### ⚠️ 常见错误

1. **表名错误**
   - ❌ `tutorProfiles` → ✅ `profiles`
   - ❌ `courses` → ✅ `sessions`
   - ❌ `supportTickets` → ✅ `tickets`

2. **字段名大小写**
   - 字段名区分大小写（如 `userId` 不是 `userid`）

3. **ENUM 值**
   - status 值必须大写：`PENDING`, `CONFIRMED` 等
   - userRole 值小写：`student`, `tutor`

### 💡 优化建议

1. **添加索引**（如果还没有）
```sql
CREATE INDEX idx_sessions_status ON sessions(status);
CREATE INDEX idx_profiles_userRole ON profiles(userRole);
CREATE INDEX idx_tickets_status ON tickets(status);
```

2. **定期清理**
   - 删除过期的已关闭会话
   - 归档旧的聊天消息

3. **数据备份**
   - 定期备份 Railway 数据库
   - 在 Railway Dashboard 中设置自动备份

---

## 验证脚本

运行以下 SQL 验证数据库结构：

```sql
-- 显示所有表
SHOW TABLES;

-- 查看每个表的结构
DESCRIBE users;
DESCRIBE profiles;
DESCRIBE sessions;
DESCRIBE ratings;
DESCRIBE tickets;
DESCRIBE chatMessages;

-- 统计每个表的记录数
SELECT 'users' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'profiles', COUNT(*) FROM profiles
UNION ALL
SELECT 'sessions', COUNT(*) FROM sessions
UNION ALL
SELECT 'ratings', COUNT(*) FROM ratings
UNION ALL
SELECT 'tickets', COUNT(*) FROM tickets
UNION ALL
SELECT 'chatMessages', COUNT(*) FROM chatMessages;
```

---

**最后更新**: 2024-11-08
**数据库**: Railway MySQL
**应用**: UniTutor 平台
