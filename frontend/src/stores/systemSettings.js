/** 系统设置状态：主题、名称、Logo 等。 */
import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { getSystemSettings } from "@/api/settings";

const DEFAULT_NAME = "移动测试平台";
const DEFAULT_DESC = "专业的移动应用自动化测试平台";

export const useSystemSettingsStore = defineStore("systemSettings", () => {
  const systemName = ref(DEFAULT_NAME);
  const systemDescription = ref(DEFAULT_DESC);
  const systemVersion = ref("1.0.0");
  const systemLogo = ref("");
  const timezone = ref("Asia/Shanghai");
  const theme = ref("light");
  const defaultPageSize = ref(10);

  const loaded = ref(false);

  const load = async () => {
    try {
      const res = await getSystemSettings();
      if (res?.data && typeof res.data === "object") {
        const d = res.data;
        if (d.system_name != null) systemName.value = d.system_name;
        if (d.system_description != null) systemDescription.value = d.system_description;
        if (d.system_version != null) systemVersion.value = d.system_version;
        if (d.system_logo != null) systemLogo.value = d.system_logo || "";
        if (d.timezone != null) timezone.value = d.timezone;
        if (d.theme != null) theme.value = d.theme;
        if (d.default_page_size != null && d.default_page_size !== "") {
          const v = Number(d.default_page_size);
          if (!Number.isNaN(v) && v >= 5 && v <= 100) defaultPageSize.value = v;
        }
      }
      loaded.value = true;
    } catch (e) {
      console.error("加载系统设置失败:", e);
      loaded.value = true;
    }
  };

  /** 由系统设置页保存后同步更新 store，入参字段为驼峰（前端侧） */
  const setFromSettings = (basicSettings) => {
    if (basicSettings.systemName != null) systemName.value = basicSettings.systemName;
    if (basicSettings.systemDescription != null) systemDescription.value = basicSettings.systemDescription;
    if (basicSettings.systemVersion != null) systemVersion.value = basicSettings.systemVersion;
    if (basicSettings.systemLogo != null) systemLogo.value = basicSettings.systemLogo;
    if (basicSettings.timezone != null) timezone.value = basicSettings.timezone;
    if (basicSettings.theme != null) theme.value = basicSettings.theme;
    if (basicSettings.defaultPageSize != null && basicSettings.defaultPageSize >= 5 && basicSettings.defaultPageSize <= 100) {
      defaultPageSize.value = basicSettings.defaultPageSize;
    }
  };

  /** 侧边栏折叠时显示的简短标题（取系统名称前两个字） */
  const shortTitle = computed(() => {
    const name = systemName.value || DEFAULT_NAME;
    if (name.length <= 2) return name;
    return name.slice(0, 2);
  });

  return {
    systemName,
    systemDescription,
    systemVersion,
    systemLogo,
    timezone,
    theme,
    defaultPageSize,
    loaded,
    load,
    setFromSettings,
    shortTitle,
  };
});
