# Possibility Scheduler

这是一个运行在 Ubuntu Server 上的定时任务程序。它会根据配置的概率，在每个小时开始时决定当前的活动内容，并进行语音播报。

## 功能特性

1.  **概率调度**：在 `config.json` 中配置不同时间段的活动及其权重。
2.  **整点播报**：程序会自动休眠，直到整点唤醒执行。
3.  **连续性检测**：如果随机到的且连续的活动与上一小时相同，则保持静默，不打扰。
4.  **语音合成**：使用 Google TTS (gTTS) 生成语音。
5.  **前奏音效**：支持自定义 `intro.mp3` 前奏。

## 安装指南 (Ubuntu Server)

### 1. 系统依赖

你需要 Python 3 和音频播放工具。在 Ubuntu 上，建议安装 `mpg123` 作为音频播放后端（代码内部也会尝试使用 pygame）。

```bash
sudo apt-get update
sudo apt-get install python3 python3-pip mpg123 libsdl2-mixer-2.0-0
```

*注意：如果是完全无头（Headless）服务器，没有声卡或扬声器，你可能需要配置 USB 声卡或确保服务器扬声器驱动已加载。*

### 2. Python 依赖

```bash
pip3 install -r requirements.txt
```

### 3. 配置

编辑 `config.json` 文件来设定你的日程表。

- `start_hour` 和 `end_hour`：定义时间段（24小时制，`start` 包含，`end` 不包含）。
- `activities`：活动列表，`weight` 是相对权重，数值越大被选中的概率越高。

### 4. 准备音频

请将一个 MP3 文件重命名为 `intro.mp3` 并放入同级目录，作为播报前的提示音。

### 5. 运行

建议使用 `nohup` 或 `systemd` 在后台运行。

**直接运行测试：**
```bash
python3 scheduler.py
```

**后台运行：**
```bash
nohup python3 scheduler.py > scheduler.log 2>&1 &
```

## 常见问题

- **没有声音？**
    - 检查音量：`alsamixer`
    - 检查音频设备：`aplay -l`
    - 确保 `intro.mp3` 存在。
- **播报报错？**
    - 检查网络连接（gTTS 需要连接 Google 服务器）。
    - 确保安装了 `config.json` 中指定的语言包（默认 zh-cn）。
