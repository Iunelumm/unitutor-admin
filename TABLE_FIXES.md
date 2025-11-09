# 数据库表名修复说明

## 问题总结

管理员面板中使用了**错误的表名**，导致查询失败。

## 错误对照表

| 错误的表名 ❌ | 正确的表名 ✅ | 说明 |
|--------------|--------------|------|
| `tutorProfiles` | `profiles` | 学生和教师共用一个表，通过 `userRole` 字段区分 |
| `courses` | `sessions` | 辅导会话/课程预约 |
| `supportTickets` | `tickets` | 支持工单 |

## 已修复的查询

### 1. 平台统计 - 教师数量

**修复前** ❌:
```sql
SELECT COUNT(*) as count FROM tutorProfiles
```

**修复后** ✅:
```sql
SELECT COUNT(DISTINCT userId) as count 
FROM profiles 
WHERE userRole = 'tutor'
```

### 2. 平台统计 - 课程数量

**修复前** ❌:
```sql
SELECT COUNT(*) as count FROM courses
```

**修复后** ✅:
```sql
SELECT COUNT(*) as count FROM sessions
```

### 3. 课程状态分布

**修复前** ❌:
```sql
SELECT status, COUNT(*) as count 
FROM courses 
GROUP BY status
```

**修复后** ✅:
```sql
SELECT status, COUNT(*) as count 
FROM sessions 
GROUP BY status
```

### 4. 课程管理查询

**修复前** ❌:
```sql
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
```

**修复后** ✅:
```sql
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
```

### 5. 争议处理

**修复前** ❌:
```sql
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
```

**修复后** ✅:
```sql
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
```

### 6. 支持工单

**修复前** ❌:
```sql
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
```

**修复后** ✅:
```sql
SELECT 
    t.id,
    t.status,
    t.category,
    u.name as user_name,
    u.email,
    t.subject,
    t.message,
    t.adminResponse,
    t.createdAt,
    t.updatedAt
FROM tickets t
LEFT JOIN users u ON t.userId = u.id
```

### 7. 评分管理

**修复前** ❌:
```sql
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
```

**修复后** ✅:
```sql
SELECT 
    r.id,
    r.score,
    r.comment,
    r.visibility,
    rater.name as rater_name,
    target.name as target_name,
    s.course,
    r.createdAt
FROM ratings r
LEFT JOIN users rater ON r.raterId = rater.id
LEFT JOIN users target ON r.targetId = target.id
LEFT JOIN sessions s ON r.sessionId = s.id
```

## 字段名修复

### sessions 表字段

| 错误字段 ❌ | 正确字段 ✅ |
|------------|------------|
| `subject` | `course` |
| `duration` | `endTime - startTime` |
| `price` | 不存在此字段 |
| `disputeReason` | `cancelReason` |

### ratings 表字段

| 错误字段 ❌ | 正确字段 ✅ |
|------------|------------|
| `ratedUserId` | `targetId` |
| `courseId` | `sessionId` |

### tickets 表字段

| 错误字段 ❌ | 正确字段 ✅ |
|------------|------------|
| 表名 `supportTickets` | `tickets` |

## 状态值修复

### sessions.status

**正确的值**（全大写）:
- `PENDING` - 待确认
- `CONFIRMED` - 已确认
- `PENDING_RATING` - 待评分
- `DISPUTED` - 有争议
- `CLOSED` - 已关闭
- `CANCELLED` - 已取消

**错误的值** ❌:
- ~~`pending`~~ → `PENDING`
- ~~`confirmed`~~ → `CONFIRMED`
- ~~`completed`~~ → `CLOSED`
- ~~`cancelled`~~ → `CANCELLED`
- ~~`disputed`~~ → `DISPUTED`

### tickets.status

**正确的值**（全小写）:
- `pending` - 待处理
- `in_progress` - 处理中
- `resolved` - 已解决

## 新增功能

修复后的管理员面板新增了：

1. **👤 个人资料** 页面
   - 查看所有学生和教师的详细资料
   - 按角色筛选
   - 显示专业、年级、价格范围等信息

2. **改进的会话管理**
   - 显示完成状态（studentCompleted, tutorCompleted）
   - 更准确的状态筛选
   - 显示开始和结束时间

3. **更详细的工单信息**
   - 显示工单类别
   - 显示管理员回复
   - 显示更新时间

## 验证方法

### 在 Railway 数据库中运行

```sql
-- 1. 验证表是否存在
SHOW TABLES;

-- 应该看到:
-- users
-- profiles
-- sessions
-- ratings
-- tickets
-- chatMessages

-- 2. 验证 profiles 表结构
DESCRIBE profiles;

-- 应该有 userRole 字段 (ENUM: 'student', 'tutor')

-- 3. 验证 sessions 表结构
DESCRIBE sessions;

-- 应该有 course, startTime, endTime, status 等字段

-- 4. 测试查询
SELECT COUNT(*) FROM profiles WHERE userRole = 'tutor';
SELECT COUNT(*) FROM sessions;
SELECT COUNT(*) FROM tickets;
```

## 部署后测试

1. 登录管理员面板
2. 访问"平台统计"页面，应该能看到数据
3. 访问"会话管理"页面，检查会话列表
4. 访问"支持工单"页面，检查工单列表
5. 访问"个人资料"页面（新增），查看用户资料

## 常见错误排查

### 错误: Table 'railway.tutorProfiles' doesn't exist
**原因**: 使用了错误的表名
**解决**: 使用 `profiles` 并添加 `WHERE userRole = 'tutor'`

### 错误: Unknown column 'c.subject'
**原因**: sessions 表中字段名是 `course` 不是 `subject`
**解决**: 使用 `s.course`

### 错误: Unknown column 'ratedUserId'
**原因**: ratings 表中字段名是 `targetId`
**解决**: 使用 `r.targetId`

---

**所有修复已应用到最新的 app.py 文件中！**
