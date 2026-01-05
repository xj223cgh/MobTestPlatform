import { sleep } from '$/utils'

export function useMirrorAction() {
  const deviceStore = useDeviceStore()

  const loading = ref(false)

  async function invoke(device, { ...options } = {}) {
    const devices = Array.isArray(device) ? device : [device]

    loading.value = true

    for (let index = 0; index < devices.length; index++) {
      const item = devices[index]
      const deviceId = item?.id || item

      // 移除了preferenceStore依赖，使用空参数
      const args = ''

      const mirroring = window.scrcpy.mirror(deviceId, {
        title: deviceStore.getLabel(deviceId, 'mirror'),
        args,
        ...options,
      })

      await sleep(1 * 1000)

      try {
        await mirroring
      }
      catch (error) {
        console.error('mirror.args', args)
        console.error('mirror.error', error)
      }
    }

    loading.value = false
  }

  return {
    loading,
    invoke,
  }
}

export default useMirrorAction
