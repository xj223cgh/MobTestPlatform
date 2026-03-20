/** 文件 API：上传与下载。 */
import request from "@/utils/request";

export function uploadFile(file) {
  const formData = new FormData();
  formData.append("file", file);

  return request({
    url: "/files/upload",
    method: "post",
    data: formData,
  });
}

export function getFile(filePath) {
  return request({
    url: `/files/${filePath}`,
    method: "get",
  });
}

export function deleteFile(filePath) {
  return request({
    url: `/files/${filePath}`,
    method: "delete",
  });
}

export default {
  uploadFile,
  getFile,
  deleteFile,
};
