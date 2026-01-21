import request from "@/utils/request";

// 上传文件
export function uploadFile(file) {
  const formData = new FormData();
  formData.append("file", file);

  return request({
    url: "/files/upload",
    method: "post",
    data: formData,
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
}

// 获取文件内容
export function getFile(filePath) {
  return request({
    url: `/files/${filePath}`,
    method: "get",
  });
}

// 删除文件
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
