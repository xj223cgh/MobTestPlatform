# Agent 下载路径配置（可选）

**默认**：后端会自动使用项目下 **agent/dist/MobTestAgent.exe**。部署时只需将打包好的 exe 放入服务器项目目录的 `agent/dist/` 下，无需任何配置即可在平台提供「下载 Agent」入口。

以下为**覆盖默认路径**时使用。

## 方式一：脚本（覆盖默认路径时）

在项目根目录或任意可执行到脚本的目录下：

**配置（开启下载入口）：**
```bash
python backend/scripts/set_agent_exe_path.py set "D:\deploy\MobTestAgent.exe"
```
路径请改为本机实际存在的 `MobTestAgent.exe` 绝对路径（Windows 下注意引号与反斜杠）。

**清理（关闭下载入口）：**
```bash
python backend/scripts/set_agent_exe_path.py clear
```

脚本会写入或删除 `backend/agent_exe_path.txt`。**修改后需重启后端**生效。

## 方式二：环境变量

设置 `AGENT_EXE_PATH` 为 exe 绝对路径即可覆盖默认的 agent/dist/MobTestAgent.exe。

**优先级**：环境变量 > backend/agent_exe_path.txt > 默认 agent/dist/MobTestAgent.exe。
