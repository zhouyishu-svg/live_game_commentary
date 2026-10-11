# -*- coding: utf-8 -*-
"""视频下载与抽帧。"""
import os
import cv2
import yt_dlp
import imageio_ffmpeg

import config


def download_video(url, out_dir=None):
    """下载视频（只下视频流，配合 ffmpeg 合并为 mp4），返回本地文件路径。

    若本地已有同名视频则直接复用，避免重复下载。
    """
    out_dir = out_dir or config.DOWNLOAD_DIR
    os.makedirs(out_dir, exist_ok=True)

    # 先用轻量方式拿到视频 id，检查是否已下载过
    probe_opts = {"quiet": True, "no_warnings": True, "noplaylist": True}
    try:
        with yt_dlp.YoutubeDL(probe_opts) as ydl:
            _info = ydl.extract_info(url, download=False)
        vid = _info.get("id", "")
    except Exception:
        vid = ""

    if vid:
        for ext in ("mp4", "mkv", "flv", "webm"):
            existing = os.path.join(out_dir, f"{vid}.{ext}")
            if os.path.exists(existing):
                return existing

    # imageio-ffmpeg 自带的静态 ffmpeg，免去单独安装 ffmpeg
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

    ydl_opts = {
        "outtmpl": os.path.join(out_dir, "%(id)s.%(ext)s"),
        # 只下视频流（抽帧不需要声音），优先 H.264(avc1) 720p 以下，兼容 OpenCV
        "format": "bv*[ext=mp4][height<=720][vcodec^=avc1]/bv*[ext=mp4]/best",
        "ffmpeg_location": ffmpeg_path,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        # 合并后的最终路径
        path = ydl.prepare_filename(info)
        if info.get("requested_downloads"):
            for d in info["requested_downloads"]:
                p = d.get("filepath") or d.get("_filename")
                if p:
                    path = p
    if not os.path.exists(path):
        # 兜底：尝试找同 id 的 mp4
        vid = info.get("id", "")
        for ext in ("mp4", "mkv", "flv", "webm"):
            cand = os.path.join(out_dir, f"{vid}.{ext}")
            if os.path.exists(cand):
                path = cand
                break
    return path


def extract_frames(video_path, out_dir=None, interval=None, max_frames=None):
    """在整个视频上均匀抽帧，返回帧图片路径列表。"""
    out_dir = out_dir or config.FRAME_DIR
    interval = interval or config.FRAME_INTERVAL_SEC
    max_frames = max_frames or config.MAX_FRAMES
    os.makedirs(out_dir, exist_ok=True)

    # 若已有足够的帧，直接复用，避免重复抽帧
    existing = sorted(
        os.path.join(out_dir, f)
        for f in os.listdir(out_dir)
        if f.startswith("frame_") and f.endswith(".jpg")
    )
    if len(existing) >= max_frames:
        return existing[:max_frames]

    # 清空旧帧，避免和上次结果混在一起
    for f in existing:
        try:
            os.remove(f)
        except OSError:
            pass

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"无法打开视频: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # 均匀选取 max_frames 个帧位置（覆盖全片）
    positions = [int(total * i / max_frames) for i in range(max_frames)]
    positions = sorted(set(positions))

    frames = []
    idx = 0
    pos_set = set(positions)
    while idx <= max(positions) and len(frames) < len(positions):
        ret, frame = cap.read()
        if not ret:
            break
        if idx in pos_set:
            out_path = os.path.join(out_dir, f"frame_{idx:06d}.jpg")
            cv2.imwrite(out_path, frame)
            frames.append(out_path)
        idx += 1
    cap.release()
    return frames
