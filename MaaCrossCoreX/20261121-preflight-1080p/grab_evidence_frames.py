"""只读：抓取 MAA 实际画布（默认缩放后）与设备原始帧，各存一张 PNG。"""
from __future__ import annotations

import os

import numpy as np
from PIL import Image
from maa.controller import AdbController
from maa.toolkit import Toolkit

ADB = r"C:\Program Files\Netease\MuMu\nx_main\adb.exe"
ADDR = "127.0.0.1:16448"
OUT = r"C:\AI\crosscore-verify\evidence"

Toolkit.init_option(r"F:\tool\MaaCrossCoreX")
ctrl = AdbController(ADB, ADDR, config={})
ctrl.post_connection().wait()
print("resolution:", ctrl.resolution)

job = ctrl.post_screencap()
job.wait()
img = job.get()
print("canvas shape (h,w,c):", img.shape)
Image.fromarray(np.ascontiguousarray(img[:, :, ::-1])).save(os.path.join(OUT, "maa_canvas.png"))

ctrl.set_screenshot_use_raw_size(True)
job = ctrl.post_screencap()
job.wait()
raw = job.get()
print("raw shape (h,w,c):", raw.shape)
Image.fromarray(np.ascontiguousarray(raw[:, :, ::-1])).save(os.path.join(OUT, "device_raw.png"))
print("saved to", OUT)
