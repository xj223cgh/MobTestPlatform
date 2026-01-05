# Escrcpy 开发者指南

## 简介

[Escrcpy](https://github.com/viarotel-org/escrcpy) 是一个基于 Electron 的 Scrcpy 图形用户界面，旨在方便显示和控制 Android 设备。本指南旨在帮助开发者有效地为该项目做出贡献。

## 开始使用

### 系统要求
- Node.js v20 或更高版本
- Git

### 开发环境设置
```shell
# 克隆仓库
git clone https://github.com/viarotel-org/escrcpy.git
cd escrcpy

# 启用 pnpm 包管理器
corepack enable pnpm

# 安装依赖
pnpm install

# 启动开发服务器
pnpm dev

# 构建应用
pnpm build          # 自动检测平台
pnpm build:win      # 构建 Windows 版本
pnpm build:mac      # 构建 macOS 版本 
pnpm build:linux    # 构建 Linux 版本
```

## 技术架构

### 核心技术
- Electron - 跨平台桌面应用框架
- Vue.js - 前端框架
- JavaScript - 主要编程语言
- Node.js - 运行时环境
- scrcpy - Android 设备显示和控制工具
- adbkit - Android 调试桥工具包

### 项目结构
```
📦Escrcpy
 ┣ 📂.github              # GitHub 工作流和配置
 ┣ 📂.husky              # Git 钩子设置
 ┣ 📂.vscode             # VSCode 编辑器设置
 ┣ 📂control             # 设备悬浮控制栏
 ┣ 📂electron          # Electron 主进程
 ┣ 📂src               # 主渲染进程
 ┃ ┣ 📂assets         # 静态资源
 ┃ ┣ 📂components     # Vue 组件
 ┃ ┃ ┣ 📂Device      # 设备管理
 ┃ ┃ ┣ 📂Preference  # 设置界面
 ┃ ┃ ┗ 📂Quick       # 快速访问功能
 ┃ ┣ 📂hooks   # Vue 组合式函数
 ┃ ┣ 📂configs       # 应用配置
 ┃ ┣ 📂dicts         # 常量和枚举
 ┃ ┣ 📂icons         # 图标资源
 ┃ ┣ 📂locales       # 国际化
 ┃ ┣ 📂plugins       # Vue 插件
 ┃ ┣ 📂store         # 状态管理
 ┃ ┣ 📂styles        # 全局样式
 ┃ ┗ 📂utils         # 辅助函数
 ┣ 📂public             # 公共资源
 ┣ 📂screenshots        # 应用截图
 ┣ 📂scripts           # 构建脚本
 ┣ 📜.eslintrc-auto-import.json  # ESLint 设置
 ┣ 📜package.json      # 项目元数据
 ┣ 📜vite.config.js    # 构建配置
 ┗ 📜electron-builder.json  # Electron 打包配置
```

## 开发指南

### 编码标准
- 遵循 ESLint 配置
- 实现 Vue 3 Composition API 实践
- 遵循 Angular 的提交信息约定 ([指南](https://github.com/angular/angular/blob/22b96b9/CONTRIBUTING.md#-commit-message-guidelines))
- 为复杂实现添加文档

### 贡献流程
1. 查看现有问题和拉取请求
2. 遵循编码标准
3. 实现并测试更改
4. 更新相关文档
5. 向主分支提交拉取请求

## 调试工具

- 在应用偏好设置中启用调试模式
- 使用 Ctrl+Shift+I 访问 DevTools
- 使用控制台日志进行开发

## 参考文档

- [Electron](https://www.electronjs.org/docs)
- [Vue.js](https://vuejs.org/)
- [Scrcpy](https://github.com/Genymobile/scrcpy)
- [Adbkit](https://github.com/DeviceFarmer/adbkit)
- [Gnirehtet](https://github.com/Genymobile/gnirehtet/)

## 常见问题

### 特定区域错误："throw new Error('Electron failed to install correctly, please delete node_modules/electron and try installing again')"

将项目中的 `.npmrc.zh` 内容覆盖到 `.npmrc`，然后删除 `node_modules` 并重新安装依赖。

或者，您可以使用 [electron-fix](https://github.com/pangxieju/electron-fix)

```shell
  # 在项目目录中运行
  npx electron-fix start
```

## 支持和联系

- 错误报告：[GitHub Issues](https://github.com/viarotel-org/escrcpy/issues)
- 联系方式：viarotel@qq.com