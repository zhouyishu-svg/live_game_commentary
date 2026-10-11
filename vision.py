# -*- coding: utf-8 -*-
"""视觉识别：调用智谱 GLM-4V 识别帧画面中的关键事件。"""
import base64
import requests

import config

# 给视觉模型的提示词：先判断被攻击目标，严格区分小兵/野怪/英雄，并尽量读出真实英雄名
def _build_prompt():
    hero = (config.PERSPECTIVE_HERO or "").strip()
    hero_hint = (
        f"本局己方（视角）英雄是{hero}，{hero}是打野英雄，"
        "大部分时间在野区打野怪（红buff、蓝buff、暴君、主宰等），较少去兵线清小兵。"
        if hero else ""
    )
    return (
        "这是《王者荣耀》手机游戏截图。" + hero_hint +
        "请先判断画面中央正在被攻击的目标是什么，再据此回答："
        "目标是小兵（沿兵线道路成群列队行进的小型单位，通常多只连成一串）→ 回答：击杀小兵；"
        "目标是野区怪物（红buff、蓝buff、野猪、狼、蜥蜴、河道之灵，通常单独出现在草丛野区）→ 回答：打野怪（并说明是什么怪物，例如：打野怪，红buff）；"
        "目标是暴君或主宰（龙形怪）→ 回答：打暴君 或 打主宰；"
        "目标是敌方英雄 → 回答：击杀（并说明是哪一方击杀了哪一方，尽量读出画面里真实出现的英雄名字）；"
        "目标是防御塔 → 回答：推塔；"
        "多名英雄交战 → 回答：团战；"
        "画面里没有战斗 → 回答：无。"
        "注意：小兵成群走在兵线道路上，野怪单独待在野区草丛，两者都不是英雄，千万不要把小兵、野怪误报成击杀英雄。"
        "英雄名字只从画面里的文字（如击杀播报、英雄血条旁的昵称）读取；看不清就写\"英雄\"，严禁凭空编造英雄名字。"
        "只按上面的格式回答，不要多说。"
    )


VISION_PROMPT = _build_prompt()


def _encode_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def _call_zhipu(payload, api_key):
    resp = requests.post(
        config.API_URL,
        json=payload,
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=120,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"].strip()


def recognize_frame(frame_path, api_key):
    """识别单帧画面，返回一句话事件描述。"""
    b64 = _encode_image(frame_path)
    payload = {
        "model": config.VISION_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "image_url",
                     "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
                    {"type": "text", "text": VISION_PROMPT},
                ],
            }
        ],
    }
    return _call_zhipu(payload, api_key)
