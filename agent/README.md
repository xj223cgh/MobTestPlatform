# 本机 Agent

在「访问平台的那台电脑」上运行，用于在本机执行 adb/scrcpy，实现设备列表、投屏等设备管理能力。**adb 与 scrcpy 已封装进 exe，用户直接运行即可，无需单独安装。**

## 用户使用（流程概览）

1. 浏览器打开平台，进入**设备管理**页，点击 **「使用引导」**。
2. 第一步：点击 **「下载 Agent」**，将 **MobTestAgent.exe** 下载到本机，双击运行；窗口显示「已连接平台，等待任务…」即就绪。
3. 第二步：在本页点击 **「绑定本机」**。本机已运行 Agent 时会**自动完成绑定**；若未检测到 Agent，会显示 6 位绑定码，可在本机运行 Agent 时加参数 `--bind-code 绑定码` 完成绑定。
4. 绑定成功后，设备管理页显示「本机 Agent 已连接」，设备列表、投屏等均在本机执行。

详细流程（含部署、再次访问、清理）见 **AGENT_FLOW.md**。用户无需单独安装 adb、scrcpy。

## 本机会产生什么数据 / 是否影响电脑

Agent 在您电脑上**仅**会做以下事情，不会安装系统服务、不写系统目录、不修改 PATH：

| 项目 | 说明 |
|------|------|
| **本地配置文件** | 在 **exe 所在目录** 下生成一个 `agent_config.txt`，仅两行：`agent_uid=...` 和 `token=...`，用于下次启动时免重新注册。不涉及系统盘或用户文档。 |
| **协议注册（仅 Windows）** | 首次运行 exe 时，在 **当前用户** 注册表下写入 `HKEY_CURRENT_USER\Software\Classes\mobtestagent`，用于浏览器「启动 Agent」一键拉起。不写系统级注册表，不影响其他软件。 |
| **网络** | 仅监听本机 `127.0.0.1:8765`（本地回环），用于平台页一键绑定和状态检测；并主动连接您配置的平台地址。不开放公网端口。 |
| **其他** | 不写日志文件、不写 AppData、不创建开机启动或系统服务。 |

**结论**：只影响 exe 所在目录下的一个配置文件，以及当前用户的协议关联；不会影响系统稳定性或其它软件，卸载/删除后无残留（按下方清理步骤即可）。

## 不再使用平台时如何清理 / 重置（Windows 一键处理）

### 入口在平台上（推荐）

打开平台 **设备管理** 页 → 点击 **「清理本机 Agent」** → 在弹窗中点击 **「解绑并清理」**。  
平台会先解除绑定，再请求本机 Agent（若正在运行）执行清理并退出；若本机未运行 Agent，会提示您在本机运行 `clean_agent.bat` 或 `MobTestAgent.exe --clean` 完成清理。

### 本机单独清理（未通过平台时）

- **方式 A**：将 **clean_agent.bat** 与 **MobTestAgent.exe** 放在同一目录，双击运行 `clean_agent.bat`。  
- **方式 B**：先关闭 Agent，在 exe 所在目录打开命令行，执行：`MobTestAgent.exe --clean`。

（可选）不再需要 Agent 时，直接删除存放 exe 的整个文件夹即可。

### 仅命令行参考

| 操作 | 命令 |
|------|------|
| 一键清理（协议 + 配置文件） | `MobTestAgent.exe --clean` |
| 仅移除「启动 Agent」协议 | `MobTestAgent.exe --unregister-protocol` |

## 打包（Windows）

在 **agent 目录** 下执行：

1. **准备 bin**（从项目 escrcpy 复制 adb、scrcpy 及依赖到 `agent/bin/`）：
   ```bash
   python prepare_bin.py
   ```
   或双击 `prepare_bin.bat`。
2. **打包**：
   ```bash
   pip install pyinstaller -r requirements.txt
   pyinstaller MobTestAgent.spec
   ```
   或双击 `build.bat`（会自动执行 prepare_bin 再打包）。

生成的可执行文件在 `dist/MobTestAgent.exe`，已内含 adb 与 scrcpy。

**部署到服务器**：将 `dist/MobTestAgent.exe`（或整份 `dist/`）拷贝到服务器上**项目目录的 agent/dist/ 下**，平台会自动提供「下载 Agent」入口，无需配置环境变量。换到其他服务器部署时，同样把 exe 放在该目录即可直接使用。
