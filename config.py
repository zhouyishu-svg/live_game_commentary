# -*- coding: utf-8 -*-
"""全局配置：API Key、模型名、路径、抽帧参数。"""
import os

# 智谱 API Key：优先读环境变量 ZHIPUAI_API_KEY，其次读本地 api_key.txt
ZHIPU_API_KEY = os.getenv("ZHIPUAI_API_KEY", "").strip()

if not ZHIPU_API_KEY:
    _key_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "api_key.txt")
    if os.path.exists(_key_file):
        with open(_key_file, "r", encoding="utf-8") as f:
            ZHIPU_API_KEY = f.read().strip()

# 模型名（视觉用 plus 更准；文案生成用 flash 免费档）
VISION_MODEL = "glm-4v-plus"    # 视觉识别（看图，识别野怪/英雄更准）
TEXT_MODEL = "glm-4-flash"      # 文案生成（写字）

# 本局视角英雄名（可从视频画面读出，作为已知上下文提高识别准确率）
PERSPECTIVE_HERO = "澜"

# 智谱开放平台接口
API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

# 抽帧参数
FRAME_INTERVAL_SEC = 5   # 每几秒抽一帧
MAX_FRAMES = 12          # 最多抽多少帧（控制调用量/成本）

# 路径
KNOWLEDGE_FILE = "knowledge.json"
DOWNLOAD_DIR = "downloads"
FRAME_DIR = "frames"

# 测试视频链接
DEFAULT_VIDEO_URL = "https://www.bilibili.com/video/BV1Wq4y1A7zN/?spm_id_from=333.337.search-card.all.click&vd_source=7968575c070f0556b4c4e16c28403a0e"
