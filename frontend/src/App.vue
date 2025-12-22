<template>
  <router-view />
</template>

<script setup>
import { onMounted } from "vue";
import { useUserStore } from "@/stores/user";

const userStore = useUserStore();

onMounted(() => {
  // 应用启动时检查用户登录状态
  userStore.checkAuth();
});
</script>

<style lang="scss">
#app {
  height: 100vh;
  width: 100vw;
  font-family:
    "Helvetica Neue", Helvetica, "PingFang SC", "Hiragino Sans GB",
    "Microsoft YaHei", "微软雅黑", Arial, sans-serif;
}
</style>
