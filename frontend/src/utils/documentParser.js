// 文档解析工具

// 静态导入，避免Vite动态导入问题
import mammoth from "mammoth";
// pdfjs-dist使用命名导出，不是默认导出
import * as pdfjsLib from "pdfjs-dist";

/**
 * 解析文本文件内容
 * @param {File} file - 上传的文本文件
 * @returns {Promise<string>} - 解析后的文本内容
 */
export const parseTextFile = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      resolve(e.target.result);
    };
    reader.onerror = (error) => {
      reject(error);
    };
    reader.readAsText(file);
  });
};

/**
 * 解析PDF文件内容
 * @param {File} file - 上传的PDF文件
 * @returns {Promise<string>} - 解析后的文本内容
 */
export const parsePdfFile = (file) => {
  return new Promise(async (resolve, reject) => {
    try {
      // 读取文件内容
      const arrayBuffer = await file.arrayBuffer();

      // 加载PDF文档（现代版本的pdfjs-dist不需要显式配置worker）
      const pdfDocument = await pdfjsLib.getDocument({
        data: arrayBuffer,
        useSystemFonts: true,
        // 自动检测worker，不需要显式配置
      }).promise;

      // 提取所有页面的文本
      let textContent = "";
      for (let i = 1; i <= pdfDocument.numPages; i++) {
        const page = await pdfDocument.getPage(i);
        const content = await page.getTextContent();
        const pageText = content.items.map((item) => item.str).join(" ");
        textContent += pageText + "\n";
      }

      resolve(textContent);
    } catch (error) {
      console.error("PDF解析失败:", error);
      reject(new Error(`PDF解析失败: ${error.message}`));
    }
  });
};

/**
 * 解析DOCX文件内容
 * @param {File} file - 上传的DOCX文件
 * @returns {Promise<string>} - 解析后的文本内容
 */
export const parseDocxFile = (file) => {
  return new Promise(async (resolve, reject) => {
    try {
      // 读取文件内容
      const arrayBuffer = await file.arrayBuffer();

      // 使用mammoth库解析DOCX（更可靠的DOCX解析方案）
      const result = await mammoth.extractRawText({
        arrayBuffer: arrayBuffer,
      });

      resolve(result.value);
    } catch (error) {
      console.error("DOCX解析失败:", error);
      reject(new Error(`DOCX解析失败: ${error.message}`));
    }
  });
};

/**
 * 根据文件类型选择对应的解析器
 * @param {File} file - 上传的文件
 * @returns {Promise<string>} - 解析后的文本内容
 */
export const parseDocument = async (file) => {
  if (!file) {
    return "";
  }

  const fileName = file.name.toLowerCase();

  if (fileName.endsWith(".txt")) {
    return parseTextFile(file);
  } else if (fileName.endsWith(".pdf")) {
    return parsePdfFile(file);
  } else if (fileName.endsWith(".docx")) {
    return parseDocxFile(file);
  } else {
    throw new Error(`不支持的文件格式：${file.name}`);
  }
};

/**
 * 提取文档中的关键信息
 * @param {string} content - 文档内容
 * @returns {Object} - 提取的关键信息
 */
export const extractKeyInfo = (content) => {
  // 简化实现，实际项目中可以使用NLP或正则表达式提取关键信息
  const keyInfo = {
    functionalPoints: [], // 功能点
    dataFormats: [], // 数据格式
    businessRules: [], // 业务规则
    constraints: [], // 约束条件
  };

  // 简单的关键词提取示例
  const functionalKeywords = ["功能", "特性", "模块", "功能点", "需求"];
  const lines = content.split("\n");

  lines.forEach((line) => {
    const trimmedLine = line.trim();
    if (trimmedLine.length === 0) return;

    // 提取功能点
    if (functionalKeywords.some((keyword) => trimmedLine.includes(keyword))) {
      keyInfo.functionalPoints.push(trimmedLine);
    }
  });

  return keyInfo;
};
