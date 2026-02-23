import { watch } from "vue";

/**
 * 根据系统设置应用主题（深/浅/跟随系统）到 document
 * 在 Layout 挂载后调用，并 watch theme 变化
 */
export function useSystemAppearance(store) {
  const apply = () => {
    if (!store) return;
    const root = document.documentElement;

    // 主题：light | dark | auto
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

  // 初次应用
  apply();

  // 监听 theme 变化（如设置页保存后）
  watch(
    () => store.theme,
    () => apply(),
    { deep: true }
  );

  // 跟随系统时监听系统主题变化
  if (typeof window !== "undefined" && window.matchMedia) {
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const onChange = () => {
      if ((store.theme || "light") === "auto") apply();
    };
    mq.addEventListener("change", onChange);
    return () => mq.removeEventListener("change", onChange);
  }
}
