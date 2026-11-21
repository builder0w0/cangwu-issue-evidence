"""只读验证：用仓库自己的 device_judge.judge_frame 判定同一张 1080p 原始帧。

目的：证明预检里唯一不满足的条件就是「帧尺寸必须精确等于 1280x720」——
把期望尺寸换成实际帧尺寸后，同一个判据函数对其余条件（黑屏/填充率）全部放行。
不修改安装目录、不写设备。
"""
from __future__ import annotations

import json
import sys

sys.path.insert(0, r"F:\tool\MaaCrossCoreX\scripts")

import device_judge as dj  # noqa: E402
import pretask_landscape as pl  # noqa: E402

def main() -> int:
    serial = pl.adb_serial()
    print("serial:", serial)
    print("orientation:", pl.get_orientation())
    data = pl.screencap()
    print("raw screencap bytes:", len(data) if data else None)
    info = pl.analyze_frame(data)
    print("frame stats:", json.dumps(info, ensure_ascii=False))
    if info:
        print("aspect:", round(info["w"] / info["h"], 4))

    print("judge with EXPECTED =", (dj.EXPECTED_W, dj.EXPECTED_H), "->",
          json.dumps(dj.judge_frame(info), ensure_ascii=False))

    dj.EXPECTED_W, dj.EXPECTED_H = info["w"], info["h"]
    print("judge with EXPECTED =", (dj.EXPECTED_W, dj.EXPECTED_H), "->",
          json.dumps(dj.judge_frame(info), ensure_ascii=False))

    # 同一判据在竖屏帧尺寸下的表现（对照，用于说明它只认像素尺寸）
    dj.EXPECTED_W, dj.EXPECTED_H = dj.EXPECTED_H, dj.EXPECTED_W
    print("judge with EXPECTED(transposed) =", (dj.EXPECTED_W, dj.EXPECTED_H), "->",
          json.dumps(dj.judge_frame(info), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
