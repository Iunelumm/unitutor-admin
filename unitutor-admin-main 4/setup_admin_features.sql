-- UniTutor 管理员功能 - 数据库设置脚本
-- 运行此脚本以手动创建管理员评分表（可选，应用会自动创建）

-- 1. 创建管理员评分表
CREATE TABLE IF NOT EXISTS adminRatings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    targetUserId INT NOT NULL COMMENT '被评分用户ID',
    score INT NOT NULL COMMENT '评分 1-5',
    comment TEXT COMMENT '评价说明',
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY unique_target (targetUserId),
    FOREIGN KEY (targetUserId) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='管理员评分表';

-- 2. 为 tickets 表添加索引（如果还没有）
CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status);
CREATE INDEX IF NOT EXISTS idx_tickets_userId ON tickets(userId);

-- 3. 为 sessions 表添加索引（如果还没有）
CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status);
CREATE INDEX IF NOT EXISTS idx_sessions_studentId ON sessions(studentId);
CREATE INDEX IF NOT EXISTS idx_sessions_tutorId ON sessions(tutorId);

-- 4. 为 ratings 表添加索引（如果还没有）
CREATE INDEX IF NOT EXISTS idx_ratings_targetId ON ratings(targetId);
CREATE INDEX IF NOT EXISTS idx_ratings_raterId ON ratings(raterId);

-- 5. 为 profiles 表添加索引（如果还没有）
CREATE INDEX IF NOT EXISTS idx_profiles_userId ON profiles(userId);
CREATE INDEX IF NOT EXISTS idx_profiles_userRole ON profiles(userRole);

-- 6. 查看所有表
SHOW TABLES;

-- 7. 验证 adminRatings 表结构
DESCRIBE adminRatings;

-- 8. 统计数据
SELECT 
    'users' as table_name, 
    COUNT(*) as count 
FROM users
UNION ALL
SELECT 'profiles', COUNT(*) FROM profiles
UNION ALL
SELECT 'sessions', COUNT(*) FROM sessions
UNION ALL
SELECT 'ratings', COUNT(*) FROM ratings
UNION ALL
SELECT 'tickets', COUNT(*) FROM tickets
UNION ALL
SELECT 'adminRatings', COUNT(*) FROM adminRatings;

-- 完成！
SELECT '✅ 数据库设置完成' as status;
