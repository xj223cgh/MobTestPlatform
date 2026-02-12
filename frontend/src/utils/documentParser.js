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
      // 验证文件
      if (!file) {
        reject(new Error("文件对象为空"));
        return;
      }

      // 验证文件大小
      if (file.size === 0) {
        reject(new Error("文件大小为0，请检查文件是否有效"));
        return;
      }

      // 验证文件类型
      const fileName = file.name.toLowerCase();
      if (!fileName.endsWith(".docx")) {
        reject(
          new Error(
            "文件格式不正确，请使用 .docx 格式（不支持旧版 .doc 格式）",
          ),
        );
        return;
      }

      console.log(`开始解析DOCX文件: ${file.name}, 大小: ${file.size} 字节`);

      // 读取文件内容
      const arrayBuffer = await file.arrayBuffer();

      // 再次验证 arrayBuffer
      if (!arrayBuffer || arrayBuffer.byteLength === 0) {
        reject(new Error("文件内容读取失败，文件可能已损坏"));
        return;
      }

      console.log(`文件读取成功，ArrayBuffer 大小: ${arrayBuffer.byteLength} 字节`);

      // 使用mammoth库解析DOCX（更可靠的DOCX解析方案）
      const result = await mammoth.extractRawText({
        arrayBuffer: arrayBuffer,
      });

      if (!result || !result.value) {
        reject(new Error("DOCX 文档内容为空"));
        return;
      }

      console.log(`DOCX解析成功，提取文本长度: ${result.value.length} 字符`);
      resolve(result.value);
    } catch (error) {
      console.error("DOCX解析失败:", error);
      
      // 提供更友好的错误提示
      let errorMessage = "DOCX解析失败";
      
      if (error.message.includes("zip") || error.message.includes("central directory")) {
        errorMessage = "文件可能已损坏或不是有效的 DOCX 格式，请尝试：\n1. 确认文件是 .docx 格式（不是 .doc）\n2. 用 Word 重新打开并另存为新文件\n3. 关闭 Word 后再上传文件";
      } else if (error.message.includes("arrayBuffer")) {
        errorMessage = "文件读取失败，请重新选择文件";
      } else {
        errorMessage = `DOCX解析失败: ${error.message}`;
      }
      
      reject(new Error(errorMessage));
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
