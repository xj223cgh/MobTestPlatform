export const deviceStatus = [
  {
    label: '已连接',
    value: 'emulator',
    tagType: 'success',
  },
  {
    label: '已连接',
    value: 'device',
    tagType: 'success',
  },
  {
    label: '未授权',
    value: 'unauthorized',
    tagType: 'danger',
  },
  {
    label: '离线',
    value: 'offline',
    tagType: 'info',
  },
  {
    label: '授权中',
    value: 'authorizing',
    tagType: 'warning',
  },
]

// 获取设备状态标签类型
export function getStatusTagType(status) {
  const statusInfo = deviceStatus.find(item => item.value === status)
  return statusInfo?.tagType || 'info'
}

// 获取设备状态文本
export function getStatusText(status) {
  const statusInfo = deviceStatus.find(item => item.value === status)
  return statusInfo?.label || status
}
