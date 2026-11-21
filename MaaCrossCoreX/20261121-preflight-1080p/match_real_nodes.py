"""只读验证：直接取仓库 pipeline 里的「生产节点」定义（模板/ROI/阈值），
在 1920x1080 实例、MaaFramework 不缩放画布上跑一次识别，看能不能命中。

不做点击（action 覆盖为 DoNothing），不改安装目录，不改游戏状态。
"""
from __future__ import annotations

import json
import os
import sys

from maa.controller import AdbController
from maa.resource import Resource
from maa.tasker import Tasker
from maa.toolkit import Toolkit

ADB = r"C:\Program Files\Netease\MuMu\nx_main\adb.exe"
ADDR = "127.0.0.1:16448"
PROJECT = r"F:\tool\MaaCrossCoreX"
PIPELINE = os.path.join(PROJECT, "resource", "pipeline", "base")

# (显示名, 源文件, 节点名)
NODES = [
    ("通用_主界面_出击", "通用.json", "通用_主界面_出击"),
    ("通用_主界面_邮箱", "通用.json", "通用_主界面_邮箱"),
    ("香川大典_主界面入口", "活动-香川大典.json", "香川大典_主界面入口"),
    ("领奖_进邮件", "领取奖励.json", "领奖_进邮件"),
]


def load_node(fname: str, node: str) -> dict:
    with open(os.path.join(PIPELINE, fname), "r", encoding="utf-8") as fh:
        data = json.load(fh)
    if node not in data:
        raise KeyError(node)
    return data[node]


def recog_params(node: dict) -> dict:
    reco = node.get("recognition")
    if isinstance(reco, dict):
        rtype = reco.get("type")
        params = dict(reco.get("param") or {})
    else:
        rtype = reco
        params = {k: node[k] for k in ("template", "roi", "threshold", "expected")
                  if k in node}
    return {"type": rtype, "params": params}


def main() -> int:
    Toolkit.init_option(PROJECT)
    ctrl = AdbController(
        adb_path=ADB,
        address=ADDR,
        screencap_methods=0xFFFFFFFFFFFFFFFF,
        input_methods=0xFFFFFFFFFFFFFFFF,
        config={},
    )
    job = ctrl.post_connection()
    job.wait()
    print("connected:", job.succeeded, "resolution:", ctrl.resolution)

    res = Resource()
    bjob = res.post_bundle(os.path.join(PROJECT, "resource"))
    bjob.wait()
    print("bundle loaded:", res.loaded)

    tasker = Tasker()
    tasker.bind(res, ctrl)

    override = {}
    meta = {}
    for label, fname, node in NODES:
        nd = load_node(fname, node)
        rp = recog_params(nd)
        print(f"[node] {label} type={rp['type']} params={json.dumps(rp['params'], ensure_ascii=False)}")
        key = "vv_" + label
        override[key] = {
            "recognition": "TemplateMatch",
            "template": rp["params"]["template"],
            "roi": rp["params"]["roi"],
            "threshold": rp["params"].get("threshold", 0.7),
            "action": "DoNothing",
            "next": [],
        }
        meta[key] = (label, rp["params"].get("threshold", 0.7))

    ok = res.override_pipeline(override)
    print("override:", ok)

    out = []
    for key, (label, thr) in meta.items():
        tj = tasker.post_task(key)
        tj.wait()
        detail = tj.get()
        nodes = detail.nodes or []
        nd = nodes[-1] if nodes else None
        reco = nd.recognition if nd else None
        best = reco.best_result if reco else None
        row = {
            "node": label,
            "pipeline_threshold": thr,
            "hit": reco.hit if reco else None,
            "score": getattr(best, "score", None),
            "box": list(reco.box) if reco and reco.box is not None else None,
            "reco_name": reco.name if reco else None,
        }
        out.append(row)
        print(json.dumps(row, ensure_ascii=False))

    dst = r"C:\AI\crosscore-verify\out_match_real_nodes.json"
    with open(dst, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    print("saved:", dst)
    return 0


if __name__ == "__main__":
    sys.exit(main())
