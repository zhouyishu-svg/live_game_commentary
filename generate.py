# -*- coding: utf-8 -*-
"""RAG 解说生成：检索资料 + 事件 + 风格约束，调用大模型生成三种风格文案。"""
import requests

import config

STYLES = {
    "正式": "客观专业，术语准确，语序平稳，像官方赛事解说。",
    "激情": "短句快节奏，情绪高亢有张力，像热血直播解说。",
    "短视频口语": "口语化、有梗，开头3秒抓人，适合短视频口播。",
}


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


def generate(event_text, knowledge_items, style, api_key):
    """生成一种风格的解说文案。"""
    if knowledge_items:
        ctx = ""
        for i, item in enumerate(knowledge_items, 1):
            ctx += f"[{i}] {item['title']}：{item['content']}（来源：{item['source']}）\n"
        cite_rule = (
            "引用编号 [n] 必须严格对应上面资料里给出的编号，只能引用资料里真实存在的编号，"
            "不得使用资料里没有的编号或来源。"
        )
    else:
        ctx = "（上面没有任何可用资料）\n"
        cite_rule = (
            "由于上面没有任何资料，不得编造任何引用编号或来源；"
            "正文里不要出现 [1] 之类的引用标记，事实引用部分只写：暂无资料（知识库未命中）。"
        )

    prompt = f"""你是一名专业的《王者荣耀》电竞解说。

【英雄称呼】本局己方（视角）英雄是{config.PERSPECTIVE_HERO}。事件描述里如果没有具体英雄名，请用"{config.PERSPECTIVE_HERO}"指代己方英雄、"敌方英雄"指代对方；严禁使用"XXX"之类占位符，也严禁编造具体的敌方英雄名字。

【比赛关键事件】
{event_text}

【可参考的资料（这是你唯一的事实来源）】
{ctx}

【解说风格】{STYLES[style]}

【要求】
1. 事实性内容只能来自上面的资料，资料里没有的就写"暂无资料"，不得编造选手战绩、技能等任何资料外的事实；
2. {cite_rule}
3. 按下面格式输出：
正文：
<解说文案>
事实引用：
[1] <资料标题> — <来源>
（事实引用部分每行只写：[编号] 资料标题 — 来源，不要重复资料的完整内容；若没有任何引用，事实引用部分写：暂无资料）
"""

    payload = {
        "model": config.TEXT_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
    }
    return _call_zhipu(payload, api_key)
