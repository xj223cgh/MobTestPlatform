// 测试用例生成提示词模板
export const testCasePromptTemplates = {
  // 基础测试用例生成
  basic: `# 测试用例生成

## 需求
所属项目：{projectName}
所属迭代：{iterationName}
所属需求：{requirementName}
需求描述：{requirementDesc}
需求文档：{documentContent}

## 要求
1. 分析需求，使用等价类划分、边界值分析、场景法、因果图、错误推断法等方法设计用例，尽可能生成有效的测试用例，覆盖正常、边界、异常和反向等场景
2. 每个用例包含：
   - case_name：测试场景
   - priority：P0-P4
   - test_scenario：测试场景
   - preconditions：前置条件（换行分隔）
   - steps：测试步骤
   - expected_result：预期结果
   - test_data：测试数据

3. 输出严格JSON格式，仅test_cases数组
4. 不添加额外内容
5. 覆盖范围：具体根据需求和测试目标决策（如功能、性能、兼容、安全、稳定性、交叉冲突、边界场景、异常场景、正/逆向场景等等）

## 示例
{
  "test_cases": [
    {
      "case_name": "登录-正确账号密码",
      "priority": "P0",
      "test_scenario": "验证正确登录",
      "preconditions": "1. 系统正常\n2. 用户已注册",
      "steps": [
        "1. 打开登录页",
        "2. 输入user/pass",
        "3. 点击登录"
      ],
      "expected_result": "成功登录跳首页",
      "actual_result": "",
      "status": "pending",
      "test_data": "user: test, pass: Test123"
    }
  ]
}`,

  // 功能测试专用提示词
  functional: `# 功能测试用例生成

## 需求
所属项目：{projectName}
所属迭代：{iterationName}
所属需求：{requirementName}
需求描述：{requirementDesc}
需求文档：{documentContent}

## 生成要求
1. 分析需求，使用等价类划分、边界值分析、场景法、因果图、错误推断法等方法设计用例，尽可能生成有效的测试用例，覆盖正常、边界、异常和反向等场景
2. 每个用例包含：
   - case_name：清晰测试场景
   - priority：P0-P4（必填）
   - status：''、'pass'、'fail'、'blocked'、'not_applicable'（默认''）
   - preconditions：前置条件（换行分隔）
   - steps：测试步骤（换行分隔）
   - expected_result：预期结果
   - test_data：测试数据
   - case_description：用例描述

3. 输出严格JSON格式，仅包含test_cases数组，无其他内容
4. 所有必填字段必须有值
5. 不要输出数据库自动生成字段（id、created_at等）
6、覆盖范围：具体根据需求和测试目标决策

## 示例
{
  "test_cases": [
    {
      "case_name": "登录-正确账号密码",
      "priority": "P0",
      "status": "",
      "preconditions": "1. 系统正常\n2. 用户已注册",
      "steps": "1. 打开登录页\n2. 输入user/pass\n3. 点击登录",
      "expected_result": "成功登录跳首页",
      "actual_result": "",
      "test_data": "user: test, pass: Test123",
      "case_description": "验证核心登录流程"
    }
  ]
}`,
};

// 构建提示词
export const buildTestCasePrompt = (templateKey, params) => {
  let template =
    testCasePromptTemplates[templateKey] || testCasePromptTemplates.basic;

  // 替换模板中的变量
  Object.entries(params).forEach(([key, value]) => {
    // 确保值不为undefined或null
    const replaceValue = value || "";
    // 使用正则表达式替换所有匹配项
    const regex = new RegExp(`\\{${key}\\}`, "g");
    template = template.replace(regex, replaceValue);
  });

  return template;
};
