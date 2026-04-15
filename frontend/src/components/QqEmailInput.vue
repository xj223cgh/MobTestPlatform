<template>
  <div class="qq-email-input">
    <div class="email-input-wrap">
      <input
        :value="localPart"
        type="text"
        :placeholder="placeholder"
        :disabled="disabled"
        autocomplete="email"
        @input="onInput"
      />
      <span class="email-suffix">@qq.com</span>
    </div>
  </div>
</template>

<script setup>
// QQ 邮箱输入组件：左侧输入 QQ 号，右侧固定 @qq.com 后缀，v-model 绑定纯 QQ 号部分
import { computed } from "vue";

const props = defineProps({
  modelValue: { type: String, default: "" },
  placeholder: { type: String, default: "请输入 QQ 号" },
  disabled: { type: Boolean, default: false },
});

const emit = defineEmits(["update:modelValue"]);

const localPart = computed(() => {
  const v = (props.modelValue || "").trim();
  if (v.includes("@")) {
    const idx = v.indexOf("@");
    return v.slice(0, idx).trim();
  }
  return v;
});

function onInput(e) {
  let v = e.target.value;
  if (v.includes("@")) {
    const idx = v.indexOf("@");
    v = v.slice(0, idx).trim();
  }
  emit("update:modelValue", v);
}
</script>

<script>
/** 供外部使用：根据前缀得到完整 QQ 邮箱 */
export function getFullQqEmail(localPart) {
  const s = (localPart || "").trim();
  return s ? s + "@qq.com" : "";
}
</script>

<style scoped>
.qq-email-input {
  width: 100%;
}
.qq-email-input .email-input-wrap {
  display: flex;
  align-items: stretch;
  border-radius: 6px;
  overflow: hidden;
  border: 1px solid #dcdfe6;
  transition: border-color 0.2s;
  background: #fff;
}
.qq-email-input .email-input-wrap:focus-within {
  border-color: #409eff;
}
.qq-email-input .email-input-wrap input {
  flex: 1;
  min-width: 0;
  height: 32px;
  padding: 0 11px 0 12px;
  border: none;
  border-radius: 6px 0 0 6px !important;
  -webkit-appearance: none;
  appearance: none;
  margin-right: -1px;
  font-size: 14px;
  color: #303133;
  background: #fff;
  box-sizing: border-box;
}
.qq-email-input .email-input-wrap input:focus {
  outline: none;
}
.qq-email-input .email-input-wrap input:disabled {
  background-color: #f5f7fa;
  color: #c0c4cc;
  cursor: not-allowed;
}
.qq-email-input .email-input-wrap input::placeholder {
  color: #c0c4cc;
}
.qq-email-input .email-suffix {
  display: flex;
  align-items: center;
  padding: 0 12px;
  height: 32px;
  font-size: 14px;
  color: #606266;
  background: #f5f7fa;
  border-left: 1px solid #dcdfe6;
  border-radius: 0 6px 6px 0;
  flex-shrink: 0;
}
</style>
