// passiveEventListenerFix.js
// 修复mousewheel事件监听器的passive选项问题

// 重写addEventListener方法，自动为特定事件添加passive选项
const originalAddEventListener = EventTarget.prototype.addEventListener;

EventTarget.prototype.addEventListener = function (type, listener, options) {
  // 对于scroll-blocking事件，自动添加passive: true选项
  const passiveEvents = [
    "mousewheel",
    "wheel",
    "touchstart",
    "touchmove",
    "touchscroll",
  ];

  if (passiveEvents.includes(type) && typeof options !== "boolean") {
    // 如果options是对象且没有明确指定passive，则添加passive: true
    const updatedOptions = {
      passive: true,
      ...(options || {}),
    };

    return originalAddEventListener.call(this, type, listener, updatedOptions);
  }

  // 其他事件使用原始的addEventListener方法
  return originalAddEventListener.call(this, type, listener, options);
};

export default {};
