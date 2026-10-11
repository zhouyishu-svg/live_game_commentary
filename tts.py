# -*- coding: utf-8 -*-
"""语音合成：使用微软神经语音「晓晓」(zh-CN-XiaoxiaoNeural) 朗读解说。

用法：from tts import speak; speak("解说内容")
朗读在后台线程执行，不阻塞视频播放；edge-tts 失败时自动回退到系统语音。
"""
import asyncio
import os
import queue
import subprocess
import tempfile
import threading

import edge_tts
import imageio_ffmpeg
import winsound

VOICE = "zh-CN-XiaoxiaoNeural"

_q = queue.Queue()


def _synth_edge(text, mp3_path):
    async def _run():
        tts = edge_tts.Communicate(text, VOICE)
        await tts.save(mp3_path)

    asyncio.run(_run())


def _speak_edge(text):
    tmpdir = tempfile.mkdtemp(prefix="tts_")
    mp3 = os.path.join(tmpdir, "s.mp3")
    wav = os.path.join(tmpdir, "s.wav")
    _synth_edge(text, mp3)
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run(
        [ffmpeg, "-y", "-i", mp3, "-ar", "24000", "-ac", "1", wav],
        capture_output=True, check=True,
    )
    winsound.PlaySound(wav, winsound.SND_FILENAME | winsound.SND_ASYNC)


def _speak_fallback(text):
    import pyttsx3

    engine = pyttsx3.init()
    for v in engine.getProperty("voices"):
        if "zh" in v.id.lower():
            engine.setProperty("voice", v.id)
            break
    engine.setProperty("rate", 200)
    engine.say(text)
    engine.runAndWait()


def _worker():
    while True:
        text = _q.get()
        if text is None:
            break
        try:
            _speak_edge(text)
        except Exception as e:  # noqa: BLE001
            print("[晓晓语音失败，改用系统语音]", e)
            try:
                _speak_fallback(text)
            except Exception as e2:  # noqa: BLE001
                print("[语音出错]", e2)


_thread = threading.Thread(target=_worker, daemon=True)
_thread.start()


def speak(text):
    """非阻塞朗读：把文本放进队列，后台线程合成并朗读。"""
    text = (text or "").strip()
    if text:
        _q.put(text)
