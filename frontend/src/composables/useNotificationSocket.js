import { io } from "socket.io-client";
import { useNotificationStore } from "@/stores/notification";
import { getUserSettings } from "@/api/settings";

let socket = null;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 10;
const BASE_DELAY = 1000;

/** 开发环境仅用 polling（经 Vite 代理），避免 WebSocket 导致 write() before start_response；且与页面同源才能带上 session cookie */
function getSocketOptions() {
  if (typeof window === "undefined") {
    return { path: "/socket.io", withCredentials: true, transports: ["websocket", "polling"], reconnection: true };
  }
  const isDev = window.location.port === "8081";
  return {
    path: "/socket.io",
    withCredentials: true,
    transports: isDev ? ["polling"] : ["websocket", "polling"],
    reconnection: true,
    reconnectionAttempts: MAX_RECONNECT_ATTEMPTS,
    reconnectionDelay: BASE_DELAY,
    reconnectionDelayMax: 30000,
  };
}

async function playNotificationSound() {
  try {
    const res = await getUserSettings();
    const sound = res?.data?.notification_sound;
    if (sound === "false" || sound === false) return;
    if (typeof window === "undefined" || !window.AudioContext) return;
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.frequency.value = 800;
    gain.gain.setValueAtTime(0.15, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.1);
    osc.start(ctx.currentTime);
    osc.stop(ctx.currentTime + 0.1);
  } catch (_) {}
}

async function showDesktopNotification(payload) {
  try {
    const res = await getUserSettings();
    const desktop = res?.data?.notification_desktop;
    if (desktop === "false" || desktop === false) return;
    if (!("Notification" in window)) return;
    if (Notification.permission === "default") {
      await Notification.requestPermission();
    }
    if (Notification.permission === "granted") {
      new Notification("新消息", {
        body: payload?.title || "您有一条新通知",
        tag: `n-${payload?.notification_id || Date.now()}`,
      });
    }
  } catch (_) {}
}

export function useNotificationSocket() {
  const notificationStore = useNotificationStore();

  function connect() {
    if (socket?.connected) return;
    const origin = typeof window !== "undefined" ? window.location.origin : "";
    socket = io(origin, getSocketOptions());

    socket.on("connect", () => {
      reconnectAttempts = 0;
    });

    socket.on("notification", async (payload) => {
      notificationStore.fetchUnreadCount();
      await playNotificationSound();
      await showDesktopNotification(payload);
    });

    socket.on("disconnect", (reason) => {
      if (reason === "io server disconnect" || reason === "io client disconnect") {
        return;
      }
      const delay = Math.min(BASE_DELAY * Math.pow(2, reconnectAttempts), 30000);
      reconnectAttempts++;
      setTimeout(() => {
        if (socket && !socket.connected) socket.connect();
      }, delay);
    });
  }

  function disconnect() {
    if (socket) {
      socket.disconnect();
      socket = null;
    }
    reconnectAttempts = 0;
  }

  return { connect, disconnect };
}
