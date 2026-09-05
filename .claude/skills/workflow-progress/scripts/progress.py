# -*- coding: utf-8 -*-
"""Render the NITE R1 animation workflow progress from LIVE Blender state.

Facts only: scenes, timeline markers, real keyframe counts, render settings,
and files that actually exist on disk. No estimated completion percentages.
"""
import argparse, json, os, socket, sys, time, unicodedata
from pathlib import Path

HOST, PORT = "127.0.0.1", 9876
SKILL_DIR = Path(__file__).resolve().parent.parent
CACHE = SKILL_DIR / ".cache" / "last_probe.json"
VSCODE_DIR = SKILL_DIR.parent.parent.parent          # <root>/VScode
ROOT = VSCODE_DIR.parent                             # <root>

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


# ---------- CJK-aware text layout ----------
def dw(s):
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in str(s))


def pad(s, n):
    s = str(s)
    return s + " " * max(0, n - dw(s))


def rpad(s, n):
    s = str(s)
    return " " * max(0, n - dw(s)) + s


def trunc(s, n):
    s = str(s)
    if dw(s) <= n:
        return s
    out, w = "", 0
    for c in s:
        cw = 2 if unicodedata.east_asian_width(c) in "WF" else 1
        if w + cw > n - 1:
            break
        out += c
        w += cw
    return out + "…"


def tc(frame, fps):
    if not fps:
        return "?"
    sec = frame / fps
    return "%d:%05.2f" % (int(sec // 60), sec % 60)


def num(n):
    return format(int(n), ",")


def short_path(d, n):
    """Keep the drive and the last components so long paths stay identifiable."""
    d = str(d).replace("/", os.sep)
    if dw(d) <= n:
        return d
    parts = [x for x in d.split(os.sep) if x]
    tail = ""
    for i in range(len(parts) - 1, 0, -1):
        cand = os.sep.join(parts[i:])
        if dw(parts[0] + os.sep + "…" + os.sep + cand) > n:
            break
        tail = cand
    return parts[0] + os.sep + "…" + os.sep + tail if tail else trunc(d, n)


# ---------- talk to Blender ----------
def probe(timeout):
    out = CACHE.parent / "probe_out.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()
    body = (SKILL_DIR / "scripts" / "blender_probe.py").read_text(encoding="utf-8")
    code = 'OUT_PATH = r"%s"\n' % str(out) + body
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    s.connect((HOST, PORT))
    s.sendall(json.dumps({"type": "execute_code", "params": {"code": code}}).encode("utf-8"))
    buf = b""
    while True:
        chunk = s.recv(65536)
        if not chunk:
            break
        buf += chunk
        try:
            json.loads(buf.decode("utf-8"))
            break
        except json.JSONDecodeError:
            continue
    s.close()
    reply = json.loads(buf.decode("utf-8"))
    if reply.get("status") != "success":
        raise RuntimeError("Blender 回報失敗: " + json.dumps(reply)[:400])
    if not out.exists():
        raise RuntimeError("探測腳本沒有寫出結果檔，Blender 端可能出錯")
    data = json.loads(out.read_text(encoding="utf-8"))
    CACHE.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    return data, "live"


def load(timeout, cache_only):
    if not cache_only:
        try:
            return probe(timeout)
        except socket.timeout:
            print("!! Blender 沒有在 %ds 內回應 — 主執行緒忙碌中（不是當掉）。改用快取。\n" % timeout)
        except (ConnectionRefusedError, OSError) as e:
            print("!! 連不上 Blender %s:%d (%s)。改用快取。\n" % (HOST, PORT, type(e).__name__))
        except Exception as e:
            print("!! 探測失敗：%s: %s。改用快取。\n" % (type(e).__name__, e))
    if CACHE.exists():
        return json.loads(CACHE.read_text(encoding="utf-8")), "cache"
    print("沒有可用的快取，且 Blender 無法連線。請確認 Blender 有開、BlenderMCP addon 在 port 9876。")
    sys.exit(1)


# ---------- filesystem evidence ----------
IMG = {".png", ".jpg", ".jpeg", ".exr", ".tif", ".tiff"}
VID = {".mp4", ".mov", ".mkv", ".avi", ".webm"}


def scan_dir(p):
    """(image count, video count, newest mtime) for one directory, non-recursive."""
    n_img = n_vid = 0
    newest = 0
    try:
        for e in os.scandir(p):
            if not e.is_file():
                continue
            ext = os.path.splitext(e.name)[1].lower()
            if ext in IMG:
                n_img += 1
            elif ext in VID:
                n_vid += 1
            else:
                continue
            newest = max(newest, e.stat().st_mtime)
    except OSError:
        return None
    if not (n_img or n_vid):
        return None
    return n_img, n_vid, newest


def previews(limit):
    base = VSCODE_DIR / "tmp"
    rows = []
    if base.is_dir():
        for e in os.scandir(base):
            if not e.is_dir():
                continue
            r = scan_dir(e.path)
            if r:
                rows.append((e.name, r[0], r[1], r[2]))
    rows.sort(key=lambda x: -x[3])
    return rows[:limit], len(rows)


def render_targets(data):
    rows = []
    for sc in data["scenes"]:
        p = sc.get("render_abspath") or ""
        if not p:
            continue
        d = p if os.path.isdir(p) else os.path.dirname(p)
        r = scan_dir(d) if d else None
        rows.append((sc["name"], d, r))
    return rows


# ---------- report ----------
W = 86


def rule(ch="─"):
    return ch * W


def status_of(sh):
    if sh["total_keys"] == 0:
        return "✖", "無動畫"
    if sh["keys"]["cam"] == 0 and not sh.get("camera"):
        return "⚠", "有物件動畫、鏡頭不動"
    return "✔", ""


def bar(sh, width=8):
    k = sh["total_keys"]
    if k == 0:
        return "░" * width
    filled = min(width, max(1, int(round(width * min(1.0, k / 600.0)))))
    return "█" * filled + "░" * (width - filled)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeout", type=float, default=90.0)
    ap.add_argument("--cache-only", action="store_true")
    ap.add_argument("--brief", action="store_true")
    ap.add_argument("--scene", default=None)
    args = ap.parse_args()

    data, srcmode = load(args.timeout, args.cache_only)
    scenes = data["scenes"]
    if args.scene:
        scenes = [s for s in scenes if args.scene.lower() in s["name"].lower()]
        if not scenes:
            print("找不到符合 '%s' 的場景。" % args.scene)
            sys.exit(1)

    title = " NITE R1 動畫 · WORKFLOW 進度"
    stamp = ("即時讀取 " if srcmode == "live" else "快取快照 ") + data["probed_at"] + " "
    print(rule("═"))
    print(title + rpad(stamp, W - dw(title)))
    blend = os.path.basename(data["blend"]) or "(未存檔)"
    print(" " + trunc("%s · Blender %s · 存檔於 %s"
                      % (blend, data["blender"], data.get("blend_mtime") or "?"), W - 2))
    flags = []
    if data.get("is_dirty"):
        flags.append("● 有未存檔變更")
    if data.get("autosave"):
        flags.append("⚠ autosave 開著")
    if data.get("window_scene"):
        flags.append("視窗場景=" + data["window_scene"])
    if flags:
        print(" " + trunc(" · ".join(flags), W - 2))
    print(rule("═"))

    # ---- scene summary table ----
    print()
    print(" " + pad("場景", 34) + pad("frames", 13) + pad("時間碼", 16)
          + pad("shot", 9) + rpad("keyframes", 10))
    print(" " + rule()[:W - 1])
    tot_shots = tot_done = tot_keys = 0
    for sc in scenes:
        shots = sc["shots"]
        done = sum(1 for s in shots if s["total_keys"] > 0)
        keys = sum(s["total_keys"] for s in shots)
        tot_shots += len(shots)
        tot_done += done
        tot_keys += keys
        f = sc["fps"]
        print(" " + pad(trunc(sc["name"], 33), 34)
              + pad("%d-%d" % (sc["frame_start"], sc["frame_end"]), 13)
              + pad("%s–%s" % (tc(sc["frame_start"], f), tc(sc["frame_end"], f)), 16)
              + pad("%d/%d" % (done, len(shots)), 9)
              + rpad(num(keys), 10))
    print(" " + rule()[:W - 1])
    print(" " + pad("合計 %d 個場景" % len(scenes), 63)
          + pad("%d/%d" % (tot_done, tot_shots), 9) + rpad(num(tot_keys), 10))
    print("   shot 欄 = 「區間內有 keyframe 的 shot 數 / 總 shot 數」，"
          "是實測數量，不是完成度估計。")

    # ---- per-scene shot detail ----
    if not args.brief:
        for sc in scenes:
            f = sc["fps"]
            print()
            print(rule())
            head = "%s   %d-%d · %s–%s · %gfps · %s · %dx%d@%d%%" % (
                sc["name"], sc["frame_start"], sc["frame_end"],
                tc(sc["frame_start"], f), tc(sc["frame_end"], f), f, sc["engine"],
                sc["res"][0], sc["res"][1], sc["res"][2])
            print(" " + trunc(head, W - 2))
            sub = "  相機 %s%s · 燈 %d · 物件 %d · 動畫來源 %d · 驅動器 %d" % (
                sc["camera"] or "(無)",
                "" if len(sc["cameras"]) <= 1 else " (共 %d 台)" % len(sc["cameras"]),
                len(sc["lights"]), sc["n_objects"], sc["n_animated_sources"], sc["n_drivers"])
            print(" " + trunc(sub, W - 2))
            print(rule())
            for sh in sc["shots"]:
                mark, note = status_of(sh)
                k = sh["keys"]
                detail = " · ".join(
                    "%s %s" % (lbl, num(k[key]))
                    for key, lbl in (("obj", "物"), ("cam", "鏡"), ("lgt", "燈"),
                                     ("mat", "材"), ("shp", "形"), ("scn", "場"))
                    if k[key])
                print(" %s %s %s %s %s %s" % (
                    mark,
                    pad(trunc(sh["name"], 26), 27),
                    pad("%d-%d" % (sh["start"], sh["end"]), 12),
                    pad("%s–%s" % (tc(sh["start"], f), tc(sh["end"], f)), 15),
                    bar(sh),
                    trunc((note + " · " + detail) if note and detail else (note or detail), 44)))
                if sh.get("camera"):
                    print("     ↳ marker 綁定相機 " + sh["camera"]
                          + "（渲染時會覆蓋 scene.camera）")

    # ---- output evidence ----
    print()
    print(rule("═"))
    print(" 產出證據（檔案系統上實際存在的檔）")
    print(rule("═"))
    rows, total = previews(12)
    print(" QA 預覽  VScode/tmp/  — %d 個資料夾有影像，最新 %d 個：" % (total, len(rows)))
    for name, ni, nv, mt in rows:
        print("   " + pad(trunc(name, 32), 33)
              + rpad("%d 張" % ni, 8)
              + ("  %d 支影片" % nv if nv else "          ")
              + "   " + time.strftime("%m-%d %H:%M", time.localtime(mt)))
    if not rows:
        print("   (無)")
    print()
    print(" 算圖輸出  各場景 render.filepath：")
    for name, d, r in render_targets(data):
        if r:
            info = "%d 張 · 最新 %s" % (r[0], time.strftime("%m-%d %H:%M", time.localtime(r[2])))
        else:
            info = "尚無輸出檔"
        print("   " + pad(trunc(name, 44), 45) + info)
        print("     → " + short_path(d, W - 8))

    # ---- flags ----
    print()
    print(rule("═"))
    print(" 需要注意")
    print(rule("═"))
    warn = []
    for sc in scenes:
        for sh in sc["shots"]:
            m, note = status_of(sh)
            if m == "✖":
                warn.append("%s / %s (%d-%d) 整段沒有任何 keyframe"
                            % (sc["name"], sh["name"], sh["start"], sh["end"]))
            elif m == "⚠":
                warn.append("%s / %s (%d-%d) 有物件動畫但鏡頭完全不動"
                            % (sc["name"], sh["name"], sh["start"], sh["end"]))
        for m in sc.get("markers_outside", []):
            warn.append("%s 的 marker「%s」在 frame %d，落在場景範圍 %d-%d 之外"
                        % (sc["name"], m["name"], m["frame"],
                           sc["frame_start"], sc["frame_end"]))
        if not sc["camera"]:
            warn.append("%s 沒有設定 scene.camera" % sc["name"])
    spans = sorted((s["frame_start"], s["frame_end"], s["name"]) for s in scenes)
    for i in range(len(spans) - 1):
        a, b = spans[i], spans[i + 1]
        if b[0] <= a[1]:
            warn.append("時間軸重疊：%s (%d-%d) 與 %s (%d-%d) 共用 %d-%d"
                        % (a[2], a[0], a[1], b[2], b[0], b[1], b[0], a[1]))
        elif b[0] > a[1] + 1:
            warn.append("時間軸空隙：%s 結束於 %d，%s 才從 %d 開始（缺 %d 格）"
                        % (a[2], a[1], b[2], b[0], b[0] - a[1] - 1))
    if data.get("autosave"):
        warn.append("Blender autosave 是開的 — 這個 1GB 檔會讓每個腳本變超慢，建議關掉")
    if data.get("is_dirty"):
        warn.append("目前有未存檔的變更")
    if not warn:
        print("   沒有偵測到問題。")
    for w in warn:
        print("   · " + w)
    print()


if __name__ == "__main__":
    main()
