import request from "../utils/request";

export const getMindmap = (suiteId) =>
  request({ url: `/mindmap/${suiteId}`, method: "get" });

export const saveMindmap = (suiteId, data) =>
  request({ url: `/mindmap/${suiteId}`, method: "put", data });

export const validateMindmap = (suiteId, data) =>
  request({ url: `/mindmap/${suiteId}/validate`, method: "post", data });

export const updateEditStatus = (suiteId, data) =>
  request({ url: `/mindmap/${suiteId}/status`, method: "put", data });

/** 脑图版本列表（用于回退） */
export const getMindmapVersions = (suiteId) =>
  request({ url: `/mindmap/${suiteId}/versions`, method: "get" });

/** 回退到指定版本，返回该版本的 mindmap_data */
export const rollbackMindmapVersion = (suiteId, versionId) =>
  request({ url: `/mindmap/${suiteId}/rollback`, method: "post", data: { version_id: versionId } });

export const getTags = (projectId) =>
  request({ url: `/mindmap/tags/${projectId}`, method: "get" });

export const createTag = (data) =>
  request({ url: "/mindmap/tags", method: "post", data });

export const deleteTag = (tagId) =>
  request({ url: `/mindmap/tags/${tagId}`, method: "delete" });

export const getMarkers = (projectId) =>
  request({ url: `/mindmap/markers/${projectId}`, method: "get" });

export const createMarker = (data) =>
  request({ url: "/mindmap/markers", method: "post", data });

export const deleteMarker = (markerId) =>
  request({ url: `/mindmap/markers/${markerId}`, method: "delete" });
