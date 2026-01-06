export const deviceStatus = [
  {
    label: '在线',
    value: 'online',
    tagType: 'success',
  },
  {
    label: '离线',
    value: 'offline',
    tagType: 'info',
  },
  {
    label: '忙碌',
    value: 'busy',
    tagType: 'warning',
  },
  {
    label: '维护中',
    value: 'maintenance',
    tagType: 'danger',
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
