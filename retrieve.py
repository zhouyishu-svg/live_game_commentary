# -*- coding: utf-8 -*-
"""知识检索：关键词匹配（简单可靠，够课程作业用）。"""
import json

import config


def load_knowledge(path=None):
    with open(path or config.KNOWLEDGE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["entries"]


def retrieve(event_text, knowledge, top_k=5):
    """按关键词命中打分，返回相关度最高的知识条目。"""
    scored = []
    for item in knowledge:
        title = item.get("title", "")
        keywords = item.get("keywords", [])
        score = 0
        # 标题命中权重更高
        if title and title in event_text:
            score += 3
        for kw in keywords:
            if kw and kw in event_text:
                score += 1
        if score > 0:
            scored.append((score, item))

    scored.sort(key=lambda x: -x[0])
    return [item for _, item in scored[:top_k]]
