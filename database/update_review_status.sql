-- 更新测试套件表和测试用例表的评审状态字段
-- 执行时间：$(date)

USE mobile_test_platform;

-- 1. 为test_suites表添加review_status字段
ALTER TABLE test_suites
ADD COLUMN review_status ENUM('not_submitted', 'pending', 'approved', 'rejected') DEFAULT 'not_submitted' COMMENT '评审状态：未提交、待审核、已通过、已拒绝',
ADD INDEX idx_review_status (review_status);

-- 2. 从test_cases表移除review_status字段
ALTER TABLE test_cases
DROP COLUMN review_status;

-- 查看更新后的表结构
DESCRIBE test_suites;
DESCRIBE test_cases;

-- 提交事务
COMMIT;