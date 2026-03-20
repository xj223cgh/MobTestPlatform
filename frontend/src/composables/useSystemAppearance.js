import { watch } from "vue";

/**
 * 根据系统设置应用主题（深/浅/跟随系统）到 document.documentElement。
 * 返回清理函数，供组件 onUnmounted 调用以移除 matchMedia 监听。
 */
export function useSystemAppearance(store) {
  const apply = () => {
    if (!store) return;
    const root = document.documentElement;
    const theme = store.theme || "light";
    let isDark = false;
    if (theme === "dark") {
      isDark = true;
    } else if (theme === "auto") {
      isDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
    }
    if (isDark) {
      root.classList.add("dark");
    } else {
      root.classList.remove("dark");
    }
  };

  apply();

  watch(
    () => store.theme,
    () => apply(),
    { deep: true }
  );

  if (typeof window !== "undefined" && window.matchMedia) {
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const onChange = () => {
      if ((store.theme || "light") === "auto") apply();
    };
    mq.addEventListener("change", onChange);
    return () => mq.removeEventListener("change", onChange);
  }
}
