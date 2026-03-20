/** 自动为 scroll-blocking 事件（wheel/touchmove 等）注入 passive 选项，消除浏览器警告。 */
const originalAddEventListener = EventTarget.prototype.addEventListener;

EventTarget.prototype.addEventListener = function (type, listener, options) {
  const passiveEvents = [
    "mousewheel",
    "wheel",
    "touchstart",
    "touchmove",
    "touchscroll",
  ];

  if (passiveEvents.includes(type) && typeof options !== "boolean") {
    const updatedOptions = {
      passive: true,
      ...(options || {}),
    };

    return originalAddEventListener.call(this, type, listener, updatedOptions);
  }

  return originalAddEventListener.call(this, type, listener, options);
};

export default {};
