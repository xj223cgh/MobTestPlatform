/** 通知状态：未读数轮询。 */
import { defineStore } from "pinia";
import { ref } from "vue";
import { getUnreadCount } from "@/api/notifications";

export const useNotificationStore = defineStore("notification", () => {
  const unreadCount = ref(0);

  async function fetchUnreadCount() {
    try {
      const res = await getUnreadCount();
      if (res?.data?.count !== undefined) {
        unreadCount.value = res.data.count;
      }
      return unreadCount.value;
    } catch (_) {
      return unreadCount.value;
    }
  }

  function setUnreadCount(n) {
    unreadCount.value = Math.max(0, n);
  }

  function incrementUnread(delta = 1) {
    unreadCount.value = Math.max(0, unreadCount.value + delta);
  }

  return {
    unreadCount,
    fetchUnreadCount,
    setUnreadCount,
    incrementUnread,
  };
});
