<template>
  <el-popover
    placement="bottom-start"
    :width="250"
    trigger="click"
    @show="onShow"
  >
    <template #reference>
      <el-tag effect="light" class="cursor-pointer">
        <div class="flex items-center space-x-1">
          <span>{{ device.remark || device.name || '未命名设备' }}</span>
          <el-icon><EditPen /></el-icon>
        </div>
      </el-tag>
    </template>

    <el-input
      ref="elInput"
      v-model="localRemark"
      class=""
      placeholder="请输入设备备注"
      clearable
      @change="onInputChange"
    ></el-input>
  </el-popover>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import deviceApi from '@/api/device'

const props = defineProps({
  device: {
    type: Object,
    default: () => ({}),
  },
})

const emit = defineEmits(['update:device'])

const elInput = ref(null)
const localRemark = ref(props.device.remark || '')

// 监听设备remark变化，更新本地值
watch(() => props.device.remark, (newVal) => {
  localRemark.value = newVal || ''
})

async function onShow() {
  // 延迟聚焦，确保input已渲染
  setTimeout(() => {
    elInput.value?.focus()
  }, 100)
}

async function onInputChange() {
  try {
    // 直接更新本地状态，因为ADB设备列表没有对应的数据库ID
    emit('update:device', {
      ...props.device,
      remark: localRemark.value
    })
    
    ElMessage.success('备注更新成功')
  } catch (error) {
    console.warn('更新备注失败:', error)
    ElMessage.error('更新备注失败')
  }
}
</script>

<style lang="scss" scoped>
:deep() .el-tag {
  cursor: pointer;
}
</style>
