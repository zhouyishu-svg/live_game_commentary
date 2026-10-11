# -*- coding: utf-8 -*-
"""实时解说：边播放视频边识别画面、生成解说、语音朗读。

用法：python main.py --live
在弹出窗口中按 q 或 Esc 退出。
"""
import os
import re
import threading

import cv2

import config
from vision import recognize_frame
from retrieve import load_knowledge, retrieve
from generate import generate
import tts


def extract_body(text):
    """从生成结果里取出"正文"部分用于朗读，并去掉标记与行内引用。"""
    m = re.search(r"正文：\s*\n?(.*?)(?:事实引用：|$)", text, re.S)
    if m:
        body = m.group(1)
    else:
        body = text
    body = re.sub(r"</?解说文案>", "", body)
    # 去掉行内引用标记 [1] 及其后的引用内容，只保留干净解说
    body = re.split(r"\[\d+\]", body)[0]
    return body.strip()


def _process(frame_path, kb, api_key, spoken, max_events):
    """识别 + 生成 + 朗读（后台线程执行，不阻塞视频播放）。"""
    try:
        desc = recognize_frame(frame_path, api_key)
        if not desc or desc.strip() == "无":
            return
        desc = desc.strip()
        # 去掉模型可能原样照抄的占位符，如 <哪方>
        desc = re.sub(r"<[^>]*>", "", desc).strip()
        if not desc:
            return
        if len(spoken) >= max_events:
            return
        # 去重：同一事件只解说一次
        if desc in spoken:
            return
        items = retrieve(desc, kb)
        text = generate(desc, items, "激情", api_key)
        body = extract_body(text)
        print("\n[解说]", body)
        spoken.append(desc)
        tts.speak(body)
    except Exception as e:  # noqa: BLE001
        print("[识别/生成出错]", e)


def live(video_path, api_key, interval=4, max_events=6, start_sec=0):
    kb = load_knowledge()
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("无法打开视频:", video_path)
        return

    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    frame_interval = int(fps * interval)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # 跳过片头（BP/加载），直接从对局画面开始
    if start_sec > 0:
        start_frame = int(fps * start_sec)
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        print(f"已跳过片头，从 {start_sec} 秒开始播放")

    print(f"视频 {fps:.0f}fps / {total} 帧，每 {interval} 秒识别一次，最多解说 {max_events} 次")
    print("按 q 或 Esc 退出")

    spoken = []
    proc = None
    idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow("Live - 电竞AI实时解说 (q 退出)", frame)

        if idx % frame_interval == 0 and (proc is None or not proc.is_alive()):
            tmp = os.path.join(config.FRAME_DIR, "live_frame.jpg")
            os.makedirs(config.FRAME_DIR, exist_ok=True)
            cv2.imwrite(tmp, frame)
            proc = threading.Thread(
                target=_process, args=(tmp, kb, api_key, spoken, max_events), daemon=True
            )
            proc.start()

        key = cv2.waitKey(int(1000 / fps)) & 0xFF
        if key in (ord("q"), 27):
            break
        idx += 1

    cap.release()
    cv2.destroyAllWindows()
    print("\n实时解说结束")


if __name__ == "__main__":
    from video import download_video
    vp = download_video(config.DEFAULT_VIDEO_URL)
    live(vp, config.ZHIPU_API_KEY)
