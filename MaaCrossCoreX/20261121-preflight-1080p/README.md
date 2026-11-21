# MaaCrossCoreX · 1920×1080（16:9）实例被 pretask 预检中止 — 取证材料

采集时间：2026-11-21 11:32–11:45（UTC+8）。识别/判定取证全程只读：未修改安装目录、未改动游戏数据，pipeline 节点的 action 一律覆盖为 DoNothing；期间仅用 `adb input tap` 把游戏从待机画面唤醒到大厅（游戏闲置约 5 分钟会自己回到待机画面）。

## 环境

| 项 | 值 |
| --- | --- |
| 系统 | Windows 11 Pro 26H2，PowerShell 5.1 |
| 客户端 | MaaCrossCoreX v1.0.5（`MaaCrossCoreX.exe` FileVersion 1.0.4），Release 内置 python 3.12.10 |
| MaaFramework | 5.14.3（`runtimes/win-x64/native` 与 `python/Lib/site-packages/maa/bin` 两份 DLL 同 sha256，见 `11-maa-dll-sha256.txt`） |
| 模拟器 | MuMu 12，实例 index 2，ADB `127.0.0.1:16448`，Android 15 |
| 设备 | `wm size` 1080x1920 竖屏物理屏；`wm density` Physical 280 / Override 240；`mCurrentOrientation=1`（横屏） |
| 游戏 | com.megagame.crosscore，前台 MJUnityActivity，大厅界面 |

## 现象

把 MuMu 实例分辨率设为 1920×1080（16:9）后，日常任务在真正开始前被「设备横屏预检」中止：

```
预检失败：分辨率不符：期望 1280×720 横屏（tablet.3），当前渲染面 1920×1080
已中止本次自动化（预检失败，识别会失准）
```

`python.exe scripts\pretask_landscape.py --check` 退出码 2（见 `4-pretask-*`、`5-*`）。
壳内两次启动（11:17:55、11:25:21）同样在该步中止，日志见 `4-pretask-landscape.log`。

## 期望

README.md:45 写「模拟器建议使用 `16:9` 分辨率，例如 `1920×1080`、`1280×720`」，按此说明 1920×1080 应当可用。

## 实测：MAA 画布与该判据衡量的对象不一致

- 设备原始帧：1920×1080（`7-device-raw-1920x1080.png`）。
- MaaFramework 交给识别的画布：**1280×720**（`6-maa-canvas-1280x720.png`，`canvas.shape=(720,1280,3)`），因为 MaaFW 5.x 默认按短边 720 等比缩放；只有显式 `set_screenshot_use_raw_size(True)` 才会拿到 1920×1080。
- 同一帧交给仓库自己的 `scripts/device_judge.py` 的 `judge_frame()`：
  - `EXPECTED=(1280,720)` → `{"ok": false, "reason": "分辨率不符：…当前渲染面 1920×1080"}`
  - `EXPECTED=(1920,1080)`（仅把期望换成实际帧尺寸）→ `{"ok": true, "fill": 0.9965, "bbox_w": 1916}`
  - 见 `8-judge-frame-contrast.txt`：除「精确像素尺寸」外，方向、非黑屏、填充率全部通过。
- 生产节点在该 1280×720 画布上按原模板/ROI/阈值命中（`9-*`、`10-*`）：

| 节点 | 模板 | 阈值 | 实测分数 | 命中框 |
| --- | --- | --- | --- | --- |
| 通用_主界面_出击 | StartUp/chuji.png | 0.70 | 0.8691 | [1117, 593, 131, 63] |
| 通用_主界面_邮箱 | Infrastructures/mail.png | 0.70 | 0.9956 | [1058, 26, 38, 30] |
| 香川大典_主界面入口 | 活动/香川大典_入口.png | 0.80 | 0.9492 | [1078, 455, 156, 64] |
| 领奖_进邮件 | Infrastructures/mail.png | 0.70 | 0.9956 | [1058, 26, 38, 30] |

命中框尺寸与模板像素尺寸一致（131×63、156×64），说明游戏 UI 在 1280×720 画布上是 1:1 渲染，没有缩放误差。

## 文件

| 文件 | 内容 |
| --- | --- |
| `1-adb-wm-size.txt` | `adb shell wm size` 输出 |
| `2-adb-wm-density.txt` | `adb shell wm density` 输出 |
| `3-adb-dumpsys-display.txt` | `mCurrentOrientation` 与 `mBaseDisplayInfo`（real 1080x1920） |
| `4-pretask-landscape.log` | `logs/pretask_landscape.log` 全量（含壳内两次失败与只读复现） |
| `5-pretask-check-stdout.txt` | `--check` 的控制台输出 |
| `6-maa-canvas-1280x720.png` | MaaFramework 默认缩放后画布 |
| `7-device-raw-1920x1080.png` | adb 原始帧 |
| `8-judge-frame-contrast.txt` | `judge_frame()` 同一帧三种期望值对照 |
| `9-pipeline-node-hits-1920x1080.txt` / `10-*.json` | 生产节点识别结果 |
| `11-maa-dll-sha256.txt` | 两份 MaaFramework.dll 的 sha256 |
| `12-maafw-log-20261121.zip` | `debug/maafw.log` 原样打包：11:17:38 壳启动的那次 MAA 会话，以及 11:44 起的只读探针会话（探针用全截图方式，故含 minicap 回退告警） |
| `verify_judge.py` / `match_real_nodes.py` / `grab_evidence_frames.py` | 上述取证脚本（只读，`action` 一律覆盖为 DoNothing） |
