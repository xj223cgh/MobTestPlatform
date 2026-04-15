# 项目文档说明

本目录收录**与仓库维护、部署和协作相关的说明**；设计方案见 `docs/方案/`，论文材料见 `docs/论文/`。界面配图规范见 [`docs/images/README.md`](../images/README.md)。

---

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | Vue 3 + Element Plus + Vite + Pinia + Axios + ECharts + Socket.IO Client + simple-mind-map |
| 后端 | Flask + Flask-SQLAlchemy + Flask-Login + Flask-SocketIO + APScheduler + PyMySQL |
| 数据库 | MySQL 5.7+（utf8mb4），30 张表 |
| Agent | Python Socket.IO 客户端，打包为 MobTestAgent.exe |

---

## 环境变量与配置

后端配置通过 `backend/.env` 加载，首次部署请复制示例文件并填写实际值：

```bash
cp backend/.env.example backend/.env
```

`.env` 已在 `.gitignore` 中排除，**切勿提交**。完整配置项与注释见 [`backend/.env.example`](../../backend/.env.example)。

---

## 数据库

初始化脚本位于 `database/`，当前共 30 张表，详见 [`database/README.md`](../../database/README.md)。

---

## 第三方与开源组件（许可与归属）

### `escrcpy/` 目录（Electron 投屏客户端）

- **性质**：随本仓库引用的**第三方开源项目**，非 MobTestPlatform 自有业务代码。
- **上游**：[viarotel-org/escrcpy](https://github.com/viarotel-org/escrcpy)（Scrcpy + Electron）。
- **许可**：Apache License 2.0，全文见仓库内 [`escrcpy/LICENSE`](../../escrcpy/LICENSE)。
- **使用注意**：二次修改、再分发或单独发布时须遵守上游许可证；版本升级时请同步核对上游声明与依赖。

### 规划中集成的浏览器投屏（ws-scrcpy）

- **性质**：社区开源的 **scrcpy Web 端** 方案（常见上游如基于 scrcpy 的 WebSocket 镜像项目），具体选型以实施时为准。
- **说明**：集成方式、接口与进程管理见 [`docs/方案/ws-scrcpy实现计划.md`](../方案/ws-scrcpy实现计划.md)；落地后须在文档与发行物中标注上游项目名与许可证。

### 本仓库主体

- 平台业务代码的许可以仓库根目录 [`LICENSE`](../../LICENSE)（MIT）为准；**不包含**将第三方子目录误读为本项目单一著作权作品。

---

## REST 接口说明

不单独维护静态 API Markdown。后端启动后在浏览器打开 **Scalar** 文档页：

- 页面：`http://127.0.0.1:5000/api-docs/`
- OpenAPI JSON：`http://127.0.0.1:5000/api-docs/openapi.json`

调试需登录的接口时，请先在同一浏览器完成平台登录，或在该页调用 `POST /api/auth/login` 后再试。

---

## 功能地图

平台全量功能模块一览（含路由 / API / 数据模型对应关系）：[功能地图.md](功能地图.md)

---

## 方案与设计文档索引

| 文档 | 说明 |
|------|------|
| [平台访问与Agent流程说明.md](../方案/平台访问与Agent流程说明.md) | 服务器部署、多用户访问、Agent 注册绑定与设备列表来源 |
| [内网访问说明.md](../方案/内网访问说明.md) | 局域网访问与防火墙 |
| [AI用例生成配置说明.md](../方案/AI用例生成配置说明.md) | AI 异步生成用例、环境变量与知识库配置（可选） |
| [AI测试用例生成方案说明.md](../方案/AI测试用例生成方案说明.md) | AI 测试用例生成质量策略与架构说明 |
| [消息通知机制设计方案.md](../方案/消息通知机制设计方案.md) | 消息中心、持久化与 WebSocket 推送设计 |
| [脑图多人协作设计方案.md](../方案/脑图多人协作设计方案.md) | 脑图版本与冲突处理策略 |
| [ws-scrcpy实现计划.md](../方案/ws-scrcpy实现计划.md) | 浏览器内投屏集成规划（第三方组件） |

---

## 论文与写作参考（`docs/论文/`）

| 文档 | 说明 |
|------|------|
| [论文技术信息材料.md](../论文/论文技术信息材料.md) | 技术栈与模块汇总，便于正文引用 |
| [毕业论文-图片绘图代码汇总.txt](../论文/毕业论文-图片绘图代码汇总.txt) | 配图与绘图脚本备忘 |

其余 Word / PDF 为个人稿件或格式规范，不逐项列出。

---

## 本目录工具脚本

| 文件 | 说明 |
|------|------|
| [get_device_info.py](get_device_info.py) | 通过 ADB 读取设备信息的辅助脚本 |
