import { generateTestCases } from "@/api/ai";
import { buildTestCasePrompt } from "@/prompts/testCase";
import { parseDocument } from "@/utils/documentParser";
import { createTestCase, getTestCasesBySuite } from "@/api/testCase";
import { createTestSuite, getTestSuiteDetail } from "@/api/testSuite";

/**
 * 生成测试用例服务
 * @param {Object} params - 生成参数
 * @param {number} params.projectId - 项目ID
 * @param {number} params.iterationId - 迭代ID
 * @param {number} params.requirementId - 需求ID
 * @param {string} params.projectName - 项目名称
 * @param {string} params.iterationName - 迭代名称
 * @param {string} params.requirementName - 需求名称
 * @param {string} params.description - 用例集描述
 * @param {File} params.file - 上传的需求文档
 * @returns {Promise<Array>} - 生成的测试用例列表
 */
export const generateTestCaseService = async (params) => {
  try {
    console.log("[AI生成用例] 开始执行，参数:", {
      projectId: params.projectId,
      iterationId: params.iterationId,
      requirementId: params.requirementId,
      hasFile: !!params.file,
      hasDescription: !!params.description,
    });

    // 1. 解析上传的文档（如果有）
    console.log("[AI生成用例] 步骤1: 开始解析文档");
    let documentContent = "";
    if (params.file) {
      console.log(
        "[AI生成用例] 开始解析文件:",
        params.file.name,
        params.file.type,
      );
      documentContent = await parseDocument(params.file);
      console.log(
        "[AI生成用例] 文档解析完成，内容长度:",
        documentContent.length,
      );
    } else {
      console.log("[AI生成用例] 没有上传文档，跳过解析");
    }

    // 辅助函数：估算token数量
    function estimateTokenCount(text) {
      if (!text) return 0;
      // 英文：按空格分割计算，中文：按字符计算，混合：综合计算
      const chineseChars = (text.match(/[\u4e00-\u9fa5]/g) || []).length;
      const englishWords = (text.match(/[a-zA-Z0-9]+/g) || []).length;
      const punctuation = (text.match(/[^a-zA-Z0-9\u4e00-\u9fa5\s]/g) || [])
        .length;
      // 估算公式：中文字符 + 英文单词 + 标点符号/4
      return chineseChars + englishWords + Math.ceil(punctuation / 4);
    }

    // 2. 构建AI提示词 - 仅使用功能测试模板
    console.log("[AI生成用例] 步骤2: 开始构建提示词");
    const prompt = buildTestCasePrompt("functional", {
      projectName: params.projectName || "",
      iterationName: params.iterationName || "",
      requirementName: params.requirementName || "",
      requirementDesc: params.description || "",
      documentContent: documentContent,
    });
    const promptTokenCount = estimateTokenCount(prompt);
    console.log(
      "[AI生成用例] 提示词构建完成，长度:",
      prompt.length,
      " 估算token数:",
      promptTokenCount,
    );

    // 3. 调用AI接口生成测试用例
    console.log("[AI生成用例] 步骤3: 开始调用AI接口");
    const response = await generateTestCases(prompt);
    console.log("[AI生成用例] AI接口调用成功，响应状态:", response.status);

    // 4. 解析AI返回结果
    console.log("[AI生成用例] 步骤4: 开始解析AI返回结果");
    const aiResponse = response.choices[0]?.message?.content;
    if (!aiResponse) {
      throw new Error("AI未返回有效结果");
    }
    console.log("[AI生成用例] AI返回内容长度:", aiResponse.length);
    console.log(
      "[AI生成用例] AI返回内容预览:",
      aiResponse.substring(0, 200) + (aiResponse.length > 200 ? "..." : ""),
    );

    // 增强的JSON解析逻辑，处理可能的格式问题
    let parsedResponse;
    try {
      // 预处理：移除可能的前缀或后缀，只保留JSON部分
      let cleanResponse = aiResponse.trim();

      // 移除可能的markdown代码块标记
      if (cleanResponse.startsWith("```json")) {
        cleanResponse = cleanResponse.slice(7);
      }
      if (cleanResponse.endsWith("```")) {
        cleanResponse = cleanResponse.slice(0, -3);
      }
      cleanResponse = cleanResponse.trim();

      // 尝试解析JSON
      parsedResponse = JSON.parse(cleanResponse);
    } catch (parseError) {
      console.error("[AI生成用例] JSON解析失败，原始内容:", aiResponse);
      console.error("[AI生成用例] 解析错误详情:", parseError);

      // 尝试修复常见的JSON格式问题
      try {
        // 移除可能的末尾逗号
        let fixedResponse = aiResponse.replace(/,\s*([\]}])/g, "$1");
        parsedResponse = JSON.parse(fixedResponse);
        console.log("[AI生成用例] JSON修复后解析成功");
      } catch (fixedParseError) {
        throw new Error(`AI返回结果JSON解析失败: ${parseError.message}`);
      }
    }

    const aiGeneratedCases = parsedResponse.test_cases || [];
    console.log("[AI生成用例] AI返回用例数量:", aiGeneratedCases.length);

    // 5. 格式化用例数据，适配系统数据结构
    console.log("[AI生成用例] 步骤5: 开始格式化用例数据");
    const formattedCases = aiGeneratedCases.map((caseItem, index) => {
      console.log(
        `[AI生成用例] 格式化第${index + 1}个用例:`,
        caseItem.case_name || "未命名用例",
      );

      // 确保优先级为有效值
      const validPriorities = ["P0", "P1", "P2", "P3", "P4"];
      const priority = validPriorities.includes(caseItem.priority)
        ? caseItem.priority
        : "P1";

      // 确保状态为有效值
      const validStatuses = ["", "pass", "fail", "blocked", "not_applicable"];
      const status = validStatuses.includes(caseItem.status)
        ? caseItem.status
        : "";

      // 确保steps为字符串格式（数据库中存储为Text类型）
      let steps = caseItem.steps || "";
      if (Array.isArray(steps)) {
        steps = steps.join("\n");
      }

      // 确保所有必填字段都有值
      const caseName = caseItem.case_name || `测试用例_${index + 1}`;
      const preconditions =
        caseItem.preconditions || "1. 系统正常运行\n2. 网络连接正常";
      const expectedResult =
        caseItem.expected_result || "系统按照预期执行，无异常报错";
      const testData = caseItem.test_data || "无特殊测试数据";
      const caseDescription =
        caseItem.case_description ||
        caseItem.description ||
        `${caseName} - 自动生成的功能测试用例`;

      const formattedCase = {
        // AI生成的字段，直接映射到数据库字段
        case_name: caseName,
        priority: priority,
        status: status,
        preconditions: preconditions,
        steps: steps || "1. 打开相关页面\n2. 按照操作流程执行\n3. 验证执行结果",
        expected_result: expectedResult,
        actual_result: caseItem.actual_result || "",
        test_data: testData,
        case_description: caseDescription,

        // 系统关联字段（由前端/后端赋值）
        project_id: params.projectId,
        iteration_id: params.iterationId,
        version_requirement_id: params.requirementId,
        suite_id: null, // 生成后需要用户选择或系统分配
      };

      console.log(
        `[AI生成用例] 第${index + 1}个用例格式化完成，字段完整性检查:`,
        {
          hasCaseName: !!formattedCase.case_name,
          hasPriority: !!formattedCase.priority,
          hasPreconditions: !!formattedCase.preconditions,
          hasSteps: !!formattedCase.steps,
          hasExpectedResult: !!formattedCase.expected_result,
          hasTestData: !!formattedCase.test_data,
          hasDescription: !!formattedCase.case_description,
        },
      );
      return formattedCase;
    });

    console.log(
      "[AI生成用例] 所有用例格式化完成，共",
      formattedCases.length,
      "个用例",
    );
    console.log("[AI生成用例] 执行完成，返回用例数量:", formattedCases.length);

    return formattedCases;
  } catch (error) {
    console.error("[AI生成用例] 执行失败:", error);
    throw error;
  }
};

/**
 * 生成符合规范的测试用例编号
 * @param {number} startIndex - 起始编号索引
 * @param {string} prefix - 编号前缀（如 "IOS-1.0.0-登录"）
 * @returns {string} - 生成的用例编号
 */
const generateCaseNumber = (startIndex, prefix) => {
  const number = startIndex.toString().padStart(3, "0");
  return `${prefix}${number}`;
};

/**
 * 生成符合规范的测试用例名称
 * @param {string} caseNumber - 用例编号
 * @returns {string} - 生成的用例名称
 */
const generateCaseName = (caseNumber) => {
  return `测试用例_${caseNumber}`;
};

/**
 * 批量保存生成的测试用例
 * @param {Array} cases - 生成的测试用例列表
 * @param {number} suiteId - 目标用例集ID
 * @param {Object} params - 生成参数
 * @returns {Promise<Array>} - 保存成功的用例列表
 */
export const saveGeneratedCases = async (cases, suiteId, params) => {
  try {
    console.log("[AI保存用例] 开始执行，参数:", {
      casesCount: cases.length,
      suiteId: suiteId,
      hasParams: !!params,
    });

    // 1. 检查suiteId对应的套件类型
    console.log("[AI保存用例] 步骤1: 检查套件类型");
    let finalSuiteId = suiteId;
    let isNewSuiteCreated = false;

    try {
      // 获取套件详情
      const suiteDetail = await getTestSuiteDetail(suiteId);
      console.log("[AI保存用例] 套件详情:", {
        id: suiteDetail?.data?.id,
        name: suiteDetail?.data?.suite_name,
        type: suiteDetail?.data?.type,
      });

      // 如果是文件夹类型，创建一个新的用例集
      if (suiteDetail?.data?.type === "folder") {
        console.log("[AI保存用例] 检测到文件夹类型，开始创建新用例集");

        // 准备用例集名称（使用前端传递的suite_name参数）
        const suiteName =
          params.suite_name ||
          `${params.requirementName || "AI生成用例集"}_${new Date().toLocaleDateString().replace(/\//g, "-")}`;

        // 创建新用例集
        const newSuiteData = {
          suite_name: suiteName,
          type: "suite",
          project_id: params.projectId,
          parent_id: suiteId,
          description:
            params.description ||
            `AI生成的用例集，包含${cases.length}个测试用例`,
        };

        const newSuiteResponse = await createTestSuite(newSuiteData);
        finalSuiteId = newSuiteResponse.data.id;
        isNewSuiteCreated = true;

        console.log("[AI保存用例] 新用例集创建成功:", {
          id: finalSuiteId,
          name: suiteName,
        });
      } else {
        console.log("[AI保存用例] 已存在用例集，直接使用");
      }
    } catch (error) {
      console.error("[AI保存用例] 检查套件类型失败，使用原始suiteId:", error);
      // 如果获取套件详情失败，直接使用原始suiteId
      finalSuiteId = suiteId;
    }

    // 2. 获取当前用例集中最大的用例编号，用于生成新编号
    console.log("[AI保存用例] 步骤2: 获取当前用例集中的最大编号");
    let maxIndex = 0;
    try {
      // 获取当前用例集中的所有用例
      const response = await getTestCasesBySuite(finalSuiteId, {
        page: 1,
        page_size: 10000, // 假设用例集不会超过10000个用例
      });

      console.log(
        "[AI保存用例] 获取现有用例成功，返回数据:",
        response?.data?.total || 0,
        "个用例",
      );

      // 提取用例编号，找到最大的数字部分
      const existingCases = response?.data?.items || [];
      if (existingCases.length > 0) {
        const maxNumber = existingCases
          .map((c) => {
            // 提取编号中的数字部分，如 "IOS-1.0.0-登录001" → "001" → 1
            const match = c.case_number?.match(/\d{3}$/);
            return match ? parseInt(match[0]) : 0;
          })
          .reduce((max, num) => Math.max(max, num), 0);
        maxIndex = maxNumber;
        console.log("[AI保存用例] 找到最大用例编号数字部分:", maxIndex);
      } else {
        console.log("[AI保存用例] 当前用例集为空，从0开始编号");
      }
    } catch (error) {
      console.error("[AI保存用例] 获取现有用例失败，从0开始编号:", error);
      maxIndex = 0;
    }

    // 2. 准备用例编号前缀（根据项目、迭代、需求生成，格式：XXX-XXX-XXX）
    console.log("[AI保存用例] 步骤2: 准备用例编号前缀");
    // 项目缩写：取项目名称首字母或关键部分，最多3个字符
    const projectShortName = (
      params.projectName?.replace(/[^a-zA-Z0-9]/g, "").toUpperCase() || "PROJ"
    ).slice(0, 3);

    // 迭代版本：从迭代名称中提取版本号，如 V1.0.0 → 1.0.0
    const iterationVersion =
      params.iterationName?.match(/\d+\.\d+\.\d+/)?.[0] || "1.0.0";

    // 需求缩写：取需求名称首字母或关键部分，最多3个字符
    const requirementShortName = (
      params.requirementName?.replace(/[^a-zA-Z0-9]/g, "").toUpperCase() ||
      "REQ"
    ).slice(0, 3);

    // 生成前缀：XXX-XXX-XXX 格式
    const caseNumberPrefix = `${projectShortName}-${iterationVersion}-${requirementShortName}`;
    console.log("[AI保存用例] 生成用例编号前缀:", caseNumberPrefix);

    // 3. 批量保存测试用例到数据库
    console.log(
      "[AI保存用例] 步骤3: 开始批量保存测试用例，共",
      cases.length,
      "个用例",
    );
    const savedCases = [];
    for (let i = 0; i < cases.length; i++) {
      console.log(`[AI保存用例] 保存第${i + 1}/${cases.length}个用例`);

      const caseItem = cases[i];
      const currentIndex = maxIndex + i + 1;

      // 生成用例编号
      const caseNumber = generateCaseNumber(currentIndex, caseNumberPrefix);

      // 使用AI生成的有描述性的用例名称，确保名称完整且有意义
      const caseName =
        caseItem.case_name ||
        caseItem.case_description?.substring(0, 50) ||
        `测试用例_${caseNumber}`;

      console.log(
        `[AI保存用例] 生成用例编号: ${caseNumber}, 名称: ${caseName}`,
      );

      // 构建完整的用例数据
      const caseData = {
        ...caseItem,
        suite_id: finalSuiteId,
        case_number: caseNumber,
        case_name: caseName, // 使用AI生成的有描述性名称
      };

      // 调用API保存用例
      const savedCase = await createTestCase(caseData);
      console.log(
        `[AI保存用例] 第${i + 1}个用例保存成功，返回ID:`,
        savedCase?.data?.id || "未知",
      );

      savedCases.push(savedCase.data);
    }

    console.log(
      "[AI保存用例] 所有用例保存完成，共保存",
      savedCases.length,
      "个用例",
    );

    return {
      savedCases: savedCases,
      suiteId: finalSuiteId,
      isNewSuiteCreated: isNewSuiteCreated,
    };
  } catch (error) {
    console.error("[AI保存用例] 执行失败:", error);
    throw new Error(`批量保存测试用例失败: ${error.message}`);
  }
};
