-- 更新测试套件表，添加评审人ID字段
-- 执行时间：$(date)

USE mobile_test_platform;

-- 为测试套件表添加评审人ID字段
ALTER TABLE test_suites
ADD COLUMN reviewer_id INT COMMENT '评审人ID，用于用例集评审',
ADD FOREIGN KEY (reviewer_id) REFERENCES users(id) ON DELETE SET NULL,
ADD INDEX idx_reviewer_id (reviewer_id);

-- 查看更新后的表结构
DESCRIBE test_suites;

-- 提交事务
COMMIT;