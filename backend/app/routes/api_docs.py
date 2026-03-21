"""OpenAPI 规范与 Scalar 交互式文档页（较 Swagger UI 更易读，仍消费同一 openapi.json）。"""
import re
from typing import Dict, List, Set

from flask import Blueprint, Response, current_app, jsonify

bp = Blueprint("api_docs", __name__, url_prefix="/api-docs")

# Scalar 固定版本，避免 CDN @latest Breaking Change；升级时可改此号后自测 /api-docs/
_SCALAR_CDN = "https://cdn.jsdelivr.net/npm/@scalar/api-reference@1.49.3"

_FLASK_VAR = re.compile(r"<(?:[^:>]+:)?([^>]+)>")

# 侧栏分组顺序（内部键，与 URL 段一致）；展示名见 _TAG_LABELS
_TAG_ORDER = [
    "auth",
    "users",
    "roles",
    "home",
    "projects",
    "iterations",
    "devices",
    "agent",
    "test suites",
    "test cases",
    "mindmap",
    "review tasks",
    "test tasks",
    "reports",
    "notifications",
    "settings",
    "files",
    "ai tasks",
    "other",
]

_TAG_LABELS = {
    "auth": "认证",
    "users": "用户管理",
    "roles": "角色与权限",
    "home": "首页",
    "projects": "项目管理",
    "iterations": "迭代管理",
    "devices": "设备管理",
    "agent": "本机 Agent",
    "test suites": "测试套件",
    "test cases": "测试用例",
    "mindmap": "脑图",
    "review tasks": "用例评审",
    "test tasks": "测试任务",
    "reports": "测试报告",
    "notifications": "消息通知",
    "settings": "系统设置",
    "files": "文件",
    "ai tasks": "AI 用例生成",
    "other": "其他",
}


def _tag_label(tag_key: str) -> str:
    return _TAG_LABELS.get(tag_key, tag_key)


def _endpoint_summary(app, endpoint: str) -> str:
    """优先使用视图函数 docstring 首行中文说明，否则退回端点名。"""
    view = app.view_functions.get(endpoint)
    if view is None:
        return endpoint
    doc = getattr(view, "__doc__", None) or ""
    doc = doc.strip()
    if not doc:
        return endpoint
    first = doc.split("\n", 1)[0].strip()
    return first if first else endpoint


# HTML 内嵌脚本使用 __SCALAR_CDN__ 占位，避免与 JS 花括号冲突
_SCALAR_PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>移动测试平台 · 接口文档</title>
  <style>
    html, body, #scalar-root { margin: 0; height: 100%; }
    body {
      font-family: system-ui, -apple-system, "Segoe UI", "PingFang SC",
        "Microsoft YaHei", sans-serif;
    }
  </style>
</head>
<body>
  <div id="scalar-root"></div>
  <script src="__SCALAR_CDN__" crossorigin="anonymous"></script>
  <script>
(function () {
  if ("scrollRestoration" in history) {
    history.scrollRestoration = "manual";
  }

  /** 按「左侧区域 + 可滚动高度」定位侧栏滚动容器，避免误选主内容区 */
  function findSidebarScroller(root) {
    var rectRoot = root.getBoundingClientRect();
    var best = null;
    var bestSh = 0;
    var all = root.querySelectorAll("*");
    for (var i = 0; i < all.length; i++) {
      var el = all[i];
      var st = window.getComputedStyle(el);
      if (st.overflowY !== "auto" && st.overflowY !== "scroll") continue;
      if (el.scrollHeight <= el.clientHeight + 2) continue;
      var r = el.getBoundingClientRect();
      if (r.left > rectRoot.left + rectRoot.width * 0.42) continue;
      if (r.width < 96) continue;
      if (el.scrollHeight > bestSh) {
        bestSh = el.scrollHeight;
        best = el;
      }
    }
    return best;
  }

  /**
   * 侧栏滚到底后被拉回顶部：多为 Scalar 重排 / 排序导致 scrollTop 被置 0。
   * 配合 createApiReference 内 tagsSorter/operationsSorter 恒等排序，减少重排；
   * 此处再在子树变更后恢复最近一次非零滚动位置。
   */
  function installSidebarScrollGuard(root) {
    var scroller = null;
    var saved = 0;
    var mo = null;
    var scheduled = false;

    function bind(el) {
      if (!el || el === scroller) return;
      if (mo) {
        mo.disconnect();
        mo = null;
      }
      scroller = el;
      scroller.addEventListener(
        "scroll",
        function () {
          saved = scroller.scrollTop;
        },
        { passive: true }
      );
      mo = new MutationObserver(function () {
        if (!scroller) return;
        if (saved < 24) return;
        if (scroller.scrollTop !== 0) return;
        if (scheduled) return;
        scheduled = true;
        requestAnimationFrame(function () {
          scheduled = false;
          if (scroller && saved > 24 && scroller.scrollTop === 0) {
            scroller.scrollTop = saved;
          }
        });
      });
      mo.observe(scroller, { childList: true, subtree: true });
    }

    function tryBind() {
      var el = findSidebarScroller(root);
      if (el) bind(el);
    }

    tryBind();
    var n = 0;
    var t = setInterval(function () {
      if (!scroller) tryBind();
      if (scroller || n++ > 100) clearInterval(t);
    }, 80);
  }

  /** Scalar 界面固定英文短语 → 中文（子串替换，长词在前） */
  var ZH_PAIRS = [
    ["Authentication Required", "需要登录"],
    ["Authentication", "认证"],
    ["Send Request", "发送请求"],
    ["Test Request", "调试请求"],
    ["Add Server", "添加服务地址"],
    ["Select Server", "选择服务地址"],
    ["Server Variables", "服务变量"],
    ["Servers", "服务地址"],
    ["Server", "服务"],
    ["Responses", "响应"],
    ["Response", "响应"],
    ["Request Body", "请求体"],
    ["Request", "请求"],
    ["Query Parameters", "查询参数"],
    ["Query", "查询"],
    ["Path Parameters", "路径参数"],
    ["Parameters", "参数"],
    ["Headers", "请求头"],
    ["Cookies", "Cookie"],
    ["Body", "正文"],
    ["Download OpenAPI", "下载 OpenAPI"],
    ["Open API Client", "打开 API 客户端"],
    ["Client", "客户端"],
    ["Code Samples", "代码示例"],
    ["Code Example", "代码示例"],
    ["Example", "示例"],
    ["Examples", "示例"],
    ["Required", "必填"],
    ["Optional", "可选"],
    ["Schema", "数据结构"],
    ["Show more", "展开更多"],
    ["Show less", "收起"],
    ["Copy", "复制"],
    ["Copied!", "已复制"],
    ["Search", "搜索"],
    ["Filter", "筛选"],
    ["All", "全部"],
    ["Hide", "隐藏"],
    ["Show", "显示"],
    ["Reset", "重置"],
    ["Cancel", "取消"],
    ["Apply", "应用"],
    ["Close", "关闭"],
    ["Loading", "加载中"],
    ["Powered by Scalar", "由 Scalar 驱动"],
  ];

  function applyScalarZh(root) {
    if (!root) return;
    var twFilter = {
      acceptNode: function (node) {
        var p = node.parentElement;
        if (!p) return NodeFilter.FILTER_REJECT;
        if (p.closest("script, style, code, pre, textarea, [contenteditable]")) {
          return NodeFilter.FILTER_REJECT;
        }
        return NodeFilter.FILTER_ACCEPT;
      },
    };
    var w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, twFilter);
    var node;
    while ((node = w.nextNode())) {
      var v = node.nodeValue;
      if (!v || !/\\S/.test(v)) continue;
      var nv = v;
      for (var i = 0; i < ZH_PAIRS.length; i++) {
        var a = ZH_PAIRS[i][0];
        var b = ZH_PAIRS[i][1];
        if (nv.indexOf(a) === -1) continue;
        nv = nv.split(a).join(b);
      }
      if (nv !== v) node.nodeValue = nv;
    }
  }

  var zhTimer = null;
  function scheduleApplyZh(root) {
    if (zhTimer) clearTimeout(zhTimer);
    zhTimer = setTimeout(function () {
      applyScalarZh(root);
      zhTimer = null;
    }, 60);
  }

  var specUrl = new URL("openapi.json", window.location.href).href;
  Scalar.createApiReference("#scalar-root", {
    url: specUrl,
    layout: "modern",
    theme: "purple",
    darkMode: true,
    hideModels: true,
    defaultOpenAllTags: true,
    defaultOpenFirstTag: true,
    showDeveloperTools: "never",
    operationTitleSource: "summary",
    /* 保持 openapi.json 里已排好的 tag / 接口顺序，避免 Scalar 默认 alpha 重排引发侧栏 DOM 抖动 */
    tagsSorter: function () {
      return 0;
    },
    operationsSorter: function () {
      return 0;
    },
    metaData: {
      title: "移动测试平台 · 接口文档",
      description: "REST 接口 · OpenAPI 3 · 同源会话 Cookie",
    },
    customCss: `
      .scalar-app { font-family: inherit; }
      .scalar-app aside { overflow-anchor: none; }
    `,
    onLoaded: function () {
      var root = document.getElementById("scalar-root");
      installSidebarScrollGuard(root);
      applyScalarZh(root);
      var mo = new MutationObserver(function () {
        scheduleApplyZh(root);
      });
      mo.observe(root, { childList: true, subtree: true });
    },
  });
})();
  </script>
  <noscript>请启用 JavaScript 以查看接口文档。</noscript>
</body>
</html>
"""


def _rule_to_openapi_path(rule: str) -> str:
    return _FLASK_VAR.sub(r"{\1}", rule)


def _tag_from_path(path: str) -> str:
    parts = [p for p in path.split("/") if p]
    if len(parts) >= 2 and parts[0] == "api":
        return parts[1].replace("-", " ")
    return "other"


def _sort_tags_by_module(tag_names: Set[str]) -> List[str]:
    order = {name: i for i, name in enumerate(_TAG_ORDER)}
    known = [t for t in _TAG_ORDER if t in tag_names]
    rest = sorted(t for t in tag_names if t not in order)
    return known + rest


def _paths_ordered_by_module(paths: Dict) -> Dict:
    """按路径推断的模块键（英文段）排序；与 operation.tags 的中文展示名无关。"""
    by_key: Dict[str, List[str]] = {}
    for path in paths:
        key = _tag_from_path(path)
        by_key.setdefault(key, []).append(path)
    for key in by_key:
        by_key[key].sort()

    ordered_paths = {}
    for key in _sort_tags_by_module(set(by_key.keys())):
        for path in by_key.get(key, []):
            ordered_paths[path] = paths[path]
    return ordered_paths


def build_openapi_spec(app):
    paths = {}
    for rule in app.url_map.iter_rules():
        if rule.endpoint == "static":
            continue
        r = rule.rule
        if r.startswith("/api-docs"):
            continue
        path = _rule_to_openapi_path(r)
        if not path.startswith("/api"):
            continue
        methods = [m for m in rule.methods if m not in ("OPTIONS", "HEAD")]
        if not methods:
            continue
        entry = paths.setdefault(path, {})
        tag_key = _tag_from_path(path)
        tag_name = _tag_label(tag_key)
        summary = _endpoint_summary(app, rule.endpoint)
        for method in methods:
            m = method.lower()
            entry[m] = {
                "summary": summary,
                "tags": [tag_name],
                "responses": {
                    "200": {"description": "成功"},
                    "401": {"description": "未登录或会话失效"},
                    "403": {"description": "权限不足"},
                },
            }

    tag_keys = {_tag_from_path(p) for p in paths}
    sorted_keys = _sort_tags_by_module(tag_keys)
    tag_objs = [
        {
            "name": _tag_label(k),
            "description": f"`/api/{k.replace(' ', '-')}/` 相关接口",
        }
        for k in sorted_keys
    ]
    ordered_paths = _paths_ordered_by_module(paths)

    return {
        "openapi": "3.0.3",
        "info": {
            "title": "移动测试平台 REST API",
            "version": "1.0.0",
            "description": (
                "移动测试平台 HTTP 接口说明。"
                "认证方式为 **Flask-Login 会话（Cookie）**：请先调用 `POST /api/auth/login` 登录，"
                "同一浏览器内通过本页「发送请求」调试时会自动携带 Cookie。"
                "\n\n统一 JSON 响应形如 `{ \"code\", \"message\", \"data\", \"timestamp\" }`；"
                "分页列表见 `data.items` 与 `data.pagination`。"
            ),
        },
        "servers": [{"url": "/", "description": "当前后端（与文档同源）"}],
        "tags": tag_objs,
        "paths": ordered_paths,
        "components": {
            "securitySchemes": {
                "sessionCookie": {
                    "type": "apiKey",
                    "in": "cookie",
                    "name": "session",
                    "description": "登录成功后由服务端 Set-Cookie",
                }
            }
        },
    }


@bp.route("/")
def api_reference_page():
    html = _SCALAR_PAGE_TEMPLATE.replace("__SCALAR_CDN__", _SCALAR_CDN)
    return Response(html, mimetype="text/html; charset=utf-8")


@bp.route("/openapi.json")
def openapi_json():
    return jsonify(build_openapi_spec(current_app))
