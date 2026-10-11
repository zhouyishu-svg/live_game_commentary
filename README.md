# 电竞AI智能解说辅助系统（课程作业版）

输入一个《王者荣耀》比赛视频链接，自动完成：

> 视频下载 → 抽帧 → 视觉识别事件 → 知识库检索 → RAG 生成三种风格解说

## 运行前提

需要一个**智谱开放平台 API Key**（能看图、能写字的账号 key）。

PowerShell 里先设置：

```powershell
$env:ZHIPUAI_API_KEY = "你的key"
```

## 安装依赖

```powershell
uv pip install --python .venv -r requirements.txt
```

## 运行

```powershell
# 真实运行（用默认测试视频，离线批处理：抽帧→识别→三风格解说）
.\.venv\Scripts\python.exe main.py

# 指定视频链接
.\.venv\Scripts\python.exe main.py "https://www.bilibili.com/video/BVxxxx"

# 不调 API，验证链路是否跑通（mock 模式）
.\.venv\Scripts\python.exe main.py --mock

# 实时解说：边播放视频边识别并语音朗读（按 q 退出）
.\.venv\Scripts\python.exe main.py --live

# 实时解说：跳过片头，从 280 秒的对局画面开始
.\.venv\Scripts\python.exe main.py --live --start=280
```

## 文件说明

| 文件 | 作用 |
|---|---|
| `main.py` | 主流程（含 `--live` / `--mock` / `--start` 参数） |
| `live.py` | 实时解说：播放视频 + 定时识别 + 语音朗读 |
| `video.py` | 下载视频 + 抽帧 |
| `vision.py` | GLM-4V 识别画面事件 |
| `retrieve.py` | 知识库关键词检索 |
| `generate.py` | RAG 三风格解说生成 |
| `tts.py` | 语音合成（系统中文语音朗读） |
| `knowledge.json` | 自建《王者荣耀》知识库 |
| `config.py` | API Key、模型名、抽帧参数 |
