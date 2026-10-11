# -*- coding: utf-8 -*-
"""主流程：下载视频 → 抽帧 → 视觉识别 → 检索 → 三风格生成。

用法：
  python main.py [视频链接] [--mock]
  --mock：不调用真实 API，用假响应验证整条链路是否跑通。
"""
import sys

import config
from video import download_video, extract_frames
from vision import recognize_frame
from retrieve import load_knowledge, retrieve
from generate import generate


def run(video_url, mock=False):
    api_key = config.ZHIPU_API_KEY

    print("=" * 60)
    print("电竞AI智能解说辅助系统（课程作业版）")
    print("=" * 60)

    print("\n[1/4] 下载视频...")
    vp = download_video(video_url)
    print("  视频文件:", vp)

    print("\n[2/4] 抽帧...")
    frames = extract_frames(vp)
    print(f"  共抽 {len(frames)} 帧")

    print("\n[3/4] 视觉识别（识别画面关键事件）...")
    events = []
    for fp in frames:
        if mock:
            desc = "双方在野区发生团战，蓝方英雄被击杀。"
        else:
            desc = recognize_frame(fp, api_key)
        print(f"  {fp}: {desc}")
        if desc and desc.strip() != "无":
            events.append(desc.strip())

    # 去重：相同事件只保留一条，并统计次数
    counts = {}
    for e in events:
        counts[e] = counts.get(e, 0) + 1
    event_lines = [
        f"{e}（共{counts[e]}次）" if counts[e] > 1 else e
        for e in counts
    ]
    event_text = "\n".join(event_lines) if event_lines else "（未识别到明显事件）"
    print("\n  汇总事件：")
    print("  " + event_text.replace("\n", "\n  "))

    print("\n[4/4] 检索知识库 + 生成三种风格解说...")
    kb = load_knowledge()
    items = retrieve(event_text, kb)
    print("  检索到资料:", [i["title"] for i in items] or "（无）")

    for style in ["正式", "激情", "短视频口语"]:
        print(f"\n{'=' * 40}\n【{style}】\n{'=' * 40}")
        if mock:
            out = (f"正文：\n（mock）比赛进行到关键节点，{event_text[:50]}……\n"
                   f"事实引用：\n[1] 团战 — 电竞解说通用知识")
        else:
            out = generate(event_text, items, style, api_key)
        print(out)

    print("\n完成。")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    mock = "--mock" in sys.argv
    live_mode = "--live" in sys.argv
    url = args[0] if args else config.DEFAULT_VIDEO_URL

    if live_mode:
        from live import live
        if not config.ZHIPU_API_KEY:
            print("请先设置 api_key.txt 或环境变量 ZHIPUAI_API_KEY")
            sys.exit(1)
        vp = download_video(url)
        # 可选 --start 秒数，跳过片头直接从对局画面开始
        start_sec = 0
        for a in sys.argv[1:]:
            if a.startswith("--start="):
                start_sec = int(a.split("=", 1)[1])
        live(vp, config.ZHIPU_API_KEY, start_sec=start_sec)
    else:
        run(url, mock=mock)
