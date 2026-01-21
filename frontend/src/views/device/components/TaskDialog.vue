<template>
  <div>
    <el-dialog
      v-model="visible"
      width="900px"
      :close-on-click-modal="false"
      @closed="handleClosed"
    >
      <template #header>
        <div
          style="
            display: flex;
            justify-content: space-between;
            align-items: center;
            width: 100%;
          "
        >
          <span>快速执行脚本</span>
          <el-button
            type="text"
            size="default"
            :icon="Refresh"
            title="刷新设备列表"
            style="
              margin-right: 8px;
              padding: 0;
              width: 32px;
              height: 32px;
              display: flex;
              align-items: center;
              justify-content: center;
            "
            @click="refreshDevices"
          />
        </div>
      </template>
      <el-form
        ref="scriptFormRef"
        v-loading="loading"
        :model="scriptForm"
        :rules="scriptRules"
        label-width="100px"
      >
        <el-form-item label="任务类型" prop="taskType">
          <el-radio-group
            v-model="scriptForm.taskType"
            @change="handleScriptTaskTypeChange"
          >
            <el-radio label="script"> 脚本执行 </el-radio>
            <el-radio label="install"> 安装应用 </el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item
          v-if="scriptForm.taskType === 'script'"
          label="脚本文件"
          prop="filePath"
        >
          <div class="file-input-wrapper">
            <el-input
              v-model="scriptForm.filePath"
              placeholder="请选择脚本文件"
              readonly
            />
            <el-button type="primary" @click="selectFile"> 选择文件 </el-button>
          </div>
        </el-form-item>

        <el-form-item
          v-if="
            scriptForm.taskType === 'script' &&
            scriptForm.scriptType === 'shell'
          "
          label="完整执行命令"
        >
          <el-input
            v-model="scriptForm.command"
            type="textarea"
            :rows="4"
            :placeholder="`请输入完整执行命令，格式示例：
1. Python脚本: python -m test.py --arg1 value1 --arg2 value2
2. Shell脚本: ./test.sh arg1 arg2 arg3
3. 无参数直接运行脚本: python test.py`"
          />
        </el-form-item>

        <el-form-item
          v-if="
            scriptForm.taskType === 'script' &&
            scriptForm.scriptType === 'python'
          "
          label="完整执行命令"
        >
          <el-input
            v-model="scriptForm.command"
            type="textarea"
            :rows="4"
            :placeholder="`请输入完整执行命令，格式示例：
1. Python脚本: python -m test.py --arg1 value1 --arg2 value2
2. Shell脚本: ./test.sh arg1 arg2 arg3
3. 无参数直接运行脚本: python test.py`"
          />
        </el-form-item>

        <el-form-item
          v-if="scriptForm.taskType === 'install'"
          label="APK 文件"
          prop="filePath"
        >
          <div class="file-input-wrapper">
            <el-input
              v-model="scriptForm.filePath"
              placeholder="请选择 APK 文件"
              readonly
            />
            <el-button type="primary" @click="selectFile"> 选择文件 </el-button>
          </div>
        </el-form-item>

        <el-form-item label="执行设备" prop="deviceIds">
          <el-select
            v-model="scriptForm.deviceIds"
            multiple
            :placeholder="
              props.devices.length > 0 ? '请选择执行设备' : '暂无可用设备'
            "
          >
            <el-option
              v-for="device in props.devices"
              :key="device.db_id"
              :label="`${device.device_id || device.id} (${device.status === 'online' ? '在线' : '离线'})`"
              :value="device.db_id"
              :disabled="device.status !== 'online'"
            />
            <el-option
              v-if="props.devices.length === 0"
              label="暂无可用设备"
              value=""
              disabled
            />
          </el-select>
        </el-form-item>

        <el-form-item label="执行方式">
          <el-radio-group
            v-model="scriptForm.executionMode"
            @change="handleExecutionModeChange"
          >
            <el-radio label="immediate"> 立即执行 </el-radio>
            <el-radio label="scheduled"> 定时执行 </el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 定时执行相关参数 -->
        <template v-if="scriptForm.executionMode === 'scheduled'">
          <el-form-item label="任务名称" prop="taskName" :required="true">
            <el-input
              v-model="scriptForm.taskName"
              placeholder="请输入任务名称"
            />
          </el-form-item>

          <el-form-item label="执行时间" prop="scheduledTime" :required="true">
            <el-date-picker
              v-model="scriptForm.scheduledTime"
              type="datetime"
              placeholder="选择执行时间"
              :disabled-date="disabledDate"
              :disabled-hours="disabledHours"
              :disabled-minutes="disabledMinutes"
              :disabled-seconds="disabledSeconds"
              format="YYYY-MM-DD HH:mm:ss"
              value-format="YYYY-MM-DD HH:mm:ss"
            />
          </el-form-item>

          <el-form-item label="任务描述" prop="taskDescription">
            <el-input
              v-model="scriptForm.taskDescription"
              type="textarea"
              :rows="2"
              placeholder="请输入任务描述"
            />
          </el-form-item>

          <el-form-item label="优先级" prop="priority">
            <el-select v-model="scriptForm.priority" placeholder="请选择优先级">
              <el-option label="高" value="high" />
              <el-option label="中" value="medium" />
              <el-option label="低" value="low" />
            </el-select>
          </el-form-item>

          <el-form-item label="相关文档" prop="documentationUrl">
            <el-input
              v-model="scriptForm.documentationUrl"
              type="textarea"
              :rows="3"
              placeholder="请输入相关文档链接，每行一个"
            />
          </el-form-item>
        </template>
      </el-form>

      <template #footer>
        <el-button @click="handleClose"> 取消 </el-button>
        <el-button
          type="primary"
          :loading="submitting"
          @click="handleSubmitScript"
        >
          {{ scriptForm.executionMode === "scheduled" ? "保存" : "执行" }}
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="resultVisible"
      title="任务执行结果"
      width="800px"
      :close-on-click-modal="false"
    >
      <div v-if="resultData">
        <div v-if="resultData.single">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="退出码">
              {{ resultData.single.exit_code }}
            </el-descriptions-item>
            <el-descriptions-item label="消息">
              {{ resultData.single.message || "无" }}
            </el-descriptions-item>
          </el-descriptions>

          <div v-if="resultData.single.stdout" class="result-section">
            <h4>标准输出:</h4>
            <pre class="result-output">{{ resultData.single.stdout }}</pre>
          </div>

          <div v-if="resultData.single.stderr" class="result-section">
            <h4>标准错误:</h4>
            <pre class="result-output error">{{
              resultData.single.stderr
            }}</pre>
          </div>
        </div>

        <div v-if="resultData.batch">
          <el-table :data="resultData.batch" border>
            <el-table-column prop="device_id" label="设备ID" width="120" />
            <el-table-column prop="success" label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="row.success ? 'success' : 'danger'">
                  {{ row.success ? "成功" : "失败" }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="message" label="消息" width="200" />
            <el-table-column label="输出">
              <template #default="{ row }">
                <pre class="table-output">{{ row.output || "无输出" }}</pre>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <template #footer>
        <el-button type="primary" @click="resultVisible = false">
          关闭
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue";
import { ElMessage } from "element-plus";
import { Refresh } from "@element-plus/icons-vue";
import deviceApi from "@/api/device";
import { uploadFile } from "@/api/files";

const props = defineProps({
  devices: {
    type: Array,
    default: () => [],
  },
});

const emit = defineEmits(["refresh-devices"]);

const visible = ref(false);
const loading = ref(false);
const submitting = ref(false);
const resultVisible = ref(false);
const resultData = ref(null);
const scriptFormRef = ref(null);
const selectedFile = ref(null);

const scriptForm = reactive({
  taskType: "script",
  scriptType: "",
  filePath: "",
  fileContent: "",
  command: "",
  deviceIds: [],
  executionMode: "immediate",
  scheduledTime: "",
  // 定时执行相关参数
  taskName: "",
  taskDescription: "",
  priority: "medium",
  documentationUrl: "",
});

const scriptRules = {
  filePath: [{ required: true, message: "请选择文件", trigger: "change" }],
  deviceIds: [{ required: true, message: "请选择执行设备", trigger: "change" }],
  taskName: [
    {
      validator: (rule, value, callback) => {
        if (scriptForm.executionMode === "scheduled" && !value.trim()) {
          callback(new Error("请输入任务名称"));
        } else {
          callback();
        }
      },
      trigger: ["blur", "change"],
    },
  ],
  priority: [
    {
      validator: (rule, value, callback) => {
        if (scriptForm.executionMode === "scheduled" && !value) {
          callback(new Error("请选择优先级"));
        } else {
          callback();
        }
      },
      trigger: "change",
    },
  ],
  scheduledTime: [
    {
      validator: (rule, value, callback) => {
        if (scriptForm.executionMode === "scheduled" && !value) {
          callback(new Error("请选择执行时间"));
        } else {
          callback();
        }
      },
      trigger: "change",
    },
  ],
};

const handleScriptTaskTypeChange = () => {
  scriptForm.filePath = "";
  scriptForm.fileContent = "";
  scriptForm.command = "";
  scriptForm.scriptType = "";
};

const handleExecutionModeChange = () => {
  if (scriptForm.executionMode === "immediate") {
    scriptForm.scheduledTime = "";
    scriptForm.taskName = "";
    scriptForm.taskDescription = "";
    scriptForm.priority = "medium";
    scriptForm.documentationUrl = "";
  }
};

const disabledDate = (time) => {
  return time.getTime() < Date.now() - 8.64e7;
};

const disabledHours = () => {
  const now = new Date();
  const currentHour = now.getHours();
  if (scriptForm.scheduledTime) {
    const selectedDate = new Date(scriptForm.scheduledTime);
    if (selectedDate.toDateString() === now.toDateString()) {
      return Array.from({ length: currentHour }, (_, i) => i);
    }
  }
  return [];
};

const disabledMinutes = (hour) => {
  const now = new Date();
  const currentHour = now.getHours();
  const currentMinute = now.getMinutes();
  if (scriptForm.scheduledTime) {
    const selectedDate = new Date(scriptForm.scheduledTime);
    if (
      selectedDate.toDateString() === now.toDateString() &&
      hour === currentHour
    ) {
      return Array.from({ length: currentMinute }, (_, i) => i);
    }
  }
  return [];
};

const disabledSeconds = (hour, minute) => {
  const now = new Date();
  const currentHour = now.getHours();
  const currentMinute = now.getMinutes();
  const currentSecond = now.getSeconds();
  if (scriptForm.scheduledTime) {
    const selectedDate = new Date(scriptForm.scheduledTime);
    if (
      selectedDate.toDateString() === now.toDateString() &&
      hour === currentHour &&
      minute === currentMinute
    ) {
      return Array.from({ length: currentSecond }, (_, i) => i);
    }
  }
  return [];
};

const getFileType = (fileName) => {
  const ext = fileName.split(".").pop().toLowerCase();
  if (ext === "sh") return "shell";
  if (ext === "py") return "python";
  if (ext === "apk") return "install";
  return "shell";
};

const selectFile = () => {
  const input = document.createElement("input");
  input.type = "file";

  if (scriptForm.taskType === "script") {
    input.accept = ".sh,.py";
  } else if (scriptForm.taskType === "install") {
    input.accept = ".apk";
  }

  input.onchange = (e) => {
    const file = e.target.files[0];
    if (file) {
      scriptForm.filePath = file.name;
      selectedFile.value = file;

      if (scriptForm.taskType === "script") {
        const scriptType = getFileType(file.name);
        scriptForm.scriptType = scriptType;
        ElMessage.success(`已选择文件: ${file.name} (${scriptType})`);
      } else {
        ElMessage.success(`已选择文件: ${file.name}`);
      }
    }
  };

  input.click();
};

const handleSubmitScript = async () => {
  try {
    await scriptFormRef.value.validate();

    if (props.devices.length === 0) {
      ElMessage.warning("暂无可用设备，请先连接设备");
      return;
    }

    if (!scriptForm.deviceIds || scriptForm.deviceIds.length === 0) {
      ElMessage.warning("请选择至少一个执行设备");
      return;
    }

    submitting.value = true;

    const actualTaskType =
      scriptForm.taskType === "script"
        ? scriptForm.scriptType
        : scriptForm.taskType;
    let fileData = null;

    // 如果有选中的文件，上传文件到服务器
    if (selectedFile.value) {
      try {
        const response = await uploadFile(selectedFile.value);
        fileData = response.data;
      } catch (error) {
        console.error("文件上传失败:", error);
        ElMessage.error(`文件上传失败: ${error.message || "未知错误"}`);
        submitting.value = false;
        return;
      }
    }

    if (scriptForm.executionMode === "immediate") {
      if (scriptForm.deviceIds.length === 1) {
        const deviceId = scriptForm.deviceIds[0];

        // 构建请求数据
        const requestData = {
          task_type: actualTaskType,
          command: scriptForm.command,
        };

        // 如果有上传的文件，使用file_path；否则使用file_content
        if (fileData) {
          requestData.file_path = fileData.file_path;
          requestData.script_file = fileData.filename;
        } else {
          // 对于立即执行且未上传文件的情况，继续使用file_content
          requestData.file_content = scriptForm.fileContent;
        }

        const response = await deviceApi.executeDeviceTask(
          deviceId,
          requestData,
        );

        resultData.value = {
          single: response.data,
        };
        resultVisible.value = true;
      } else {
        // 构建请求数据
        const requestData = {
          device_ids: scriptForm.deviceIds,
          task_type: actualTaskType,
          command: scriptForm.command,
        };

        // 如果有上传的文件，使用file_path；否则使用file_content
        if (fileData) {
          requestData.file_path = fileData.file_path;
          requestData.script_file = fileData.filename;
        } else {
          // 对于立即执行且未上传文件的情况，继续使用file_content
          requestData.file_content = scriptForm.fileContent;
        }

        const response = await deviceApi.executeBatchTasks(requestData);

        resultData.value = {
          batch: response.data.results,
        };
        resultVisible.value = true;
      }
    } else {
      // 构建定时任务请求数据
      const requestData = {
        device_ids: scriptForm.deviceIds,
        task_type: actualTaskType,
        command: scriptForm.command,
        scheduled_time: scriptForm.scheduledTime,
        // 定时执行相关参数
        task_name: scriptForm.taskName,
        task_description: scriptForm.taskDescription,
        priority: scriptForm.priority,
        documentation_url: scriptForm.documentationUrl,
      };

      // 定时任务必须上传文件
      if (fileData) {
        requestData.file_path = fileData.file_path;
        requestData.script_file = fileData.filename;
        requestData.file_hash = fileData.file_hash;
      }

      await deviceApi.scheduleBatchTasks(requestData);
      ElMessage.success(
        `定时任务已创建，将在 ${scriptForm.scheduledTime} 执行`,
      );
      handleClose();
    }
  } catch (error) {
    console.error("任务执行失败:", error);
    // 只有API调用错误才显示自定义错误信息，表单验证错误由Element Plus自动处理
    if (error.response || (error.message && !error.message.includes("请"))) {
      ElMessage.error(
        "任务执行失败：" +
          (error.response?.data?.message || error.message || "未知错误"),
      );
    }
  } finally {
    submitting.value = false;
  }
};

const handleClose = () => {
  visible.value = false;
};

const handleClosed = () => {
  scriptFormRef.value?.resetFields();

  Object.assign(scriptForm, {
    taskType: "script",
    scriptType: "",
    filePath: "",
    fileContent: "",
    command: "",
    deviceIds: [],
    executionMode: "immediate",
    scheduledTime: "",
    // 定时执行相关参数
    taskName: "",
    taskDescription: "",
    priority: "medium",
    documentationUrl: "",
  });
};

const open = () => {
  visible.value = true;

  const onlineDevices = props.devices.filter((d) => d.status === "online");
  if (onlineDevices.length === 1) {
    scriptForm.deviceIds = [onlineDevices[0].id];
  }
};

// 刷新设备列表
const refreshDevices = () => {
  emit("refresh-devices");
  ElMessage.success("设备列表已刷新");
};

defineExpose({
  open,
});
</script>

<style lang="scss" scoped>
.file-input-wrapper {
  display: flex;
  gap: 10px;
  width: 100%;

  .el-input {
    flex: 1;
  }
}

.result-section {
  margin-top: 20px;

  h4 {
    margin: 0 0 10px 0;
    font-size: 14px;
    font-weight: 600;
    color: #303133;
  }
}

.result-output {
  background-color: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
  font-size: 12px;
  line-height: 1.6;
  color: #606266;
  max-height: 400px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-wrap: break-word;

  &.error {
    background-color: #fef0f0;
    color: #f56c6c;
  }
}

.table-output {
  margin: 0;
  font-size: 12px;
  line-height: 1.6;
  color: #606266;
  max-height: 200px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>
