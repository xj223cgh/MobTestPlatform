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
          <span>{{ device.name || "未命名设备" }}</span>
          <el-icon><EditPen /></el-icon>
        </div>
      </el-tag>
    </template>

    <el-input
      ref="elInput"
      v-model="localRemark"
      class=""
      placeholder="请输入设备名称"
      clearable
      @change="onInputChange"
    />
  </el-popover>
</template>

<script setup>
import { ref, watch } from "vue";
import { ElMessage } from "element-plus";
import deviceApi from "@/api/device";

const props = defineProps({
  device: {
    type: Object,
    default: () => ({}),
  },
});

const emit = defineEmits(["update:device"]);

const elInput = ref(null);
const localRemark = ref(props.device.name || "");

// 监听设备name变化，更新本地值
watch(
  () => props.device.name,
  (newVal) => {
    localRemark.value = newVal || "";
  },
);

async function onShow() {
  // 延迟聚焦，确保input已渲染
  setTimeout(() => {
    elInput.value?.focus();
  }, 100);
}

async function onInputChange() {
  try {
    // 如果设备有数据库ID，则更新数据库中的设备名称
    if (props.device.db_id) {
      await deviceApi.updateDevice(props.device.db_id, {
        device_name: localRemark.value || props.device.name || "未命名设备",
      });
      ElMessage.success("设备名称更新成功");
    } else {
      // 如果设备没有数据库ID，则创建新的设备记录
      const response = await deviceApi.createDevice({
        device_name: localRemark.value || props.device.name || "未命名设备",
        device_model: props.device.name || "Unknown",
        os_type: "android",
        os_version: "Unknown",
        device_id: props.device.id,
        status: props.device.status === "device" ? "online" : "offline",
      });

      // 更新设备的db_id
      emit("update:device", {
        ...props.device,
        db_id: response.data.device.id,
        name: localRemark.value || props.device.name || "未命名设备",
      });

      ElMessage.success("设备名称保存成功");
      return;
    }

    // 更新本地状态
    emit("update:device", {
      ...props.device,
      name: localRemark.value || props.device.name || "未命名设备",
    });
  } catch (error) {
    console.warn("更新设备名称失败:", error);
    ElMessage.error(
      "更新设备名称失败：" + (error.response?.data?.message || error.message),
    );
  }
}
</script>

<style lang="scss" scoped>
:deep() .el-tag {
  cursor: pointer;
}
</style>
