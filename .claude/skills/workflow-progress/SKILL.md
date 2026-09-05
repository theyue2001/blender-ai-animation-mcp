---
name: workflow-progress
description: Show the NITE R1 3D animation project's real, cross-session workflow progress by reading LIVE Blender state over the BlenderMCP socket (scenes, timeline-marker shots, actual keyframe counts, render settings) plus the preview/render files that exist on disk. Use when the user types /workflow-progress or asks 進度 / 做到哪了 / 還剩什麼 / which shots are done / what's left / 目前狀態.
---

# Workflow Progress

Report where the NITE R1 animation actually stands. Every number comes from live
Blender state or from files on disk — never from memory, notes, or estimation.

## Run it

```bash
python "D:/接案/26_0825_紅犀牛3D動畫/VScode/.claude/skills/workflow-progress/scripts/progress.py"
```

Useful flags:

| flag | effect |
| --- | --- |
| `--brief` | scene summary table only, skip the per-shot breakdown |
| `--scene P08` | only scenes whose name contains `P08` |
| `--timeout 300` | wait longer when Blender's main thread is busy (default 90s) |
| `--cache-only` | skip Blender entirely, print the last snapshot |

Print the script's output to the user **verbatim inside a code block** — the
report is column-aligned and loses its shape if reflowed. Then add a short
read of it below (see *Interpreting* ).

## What it measures

The probe (`scripts/blender_probe.py`) runs **read-only** inside Blender and
never touches the depsgraph, the window scene, or any datablock. It reports:

- every scene, its frame range, fps, engine, resolution, camera, drivers
- **shots** = the spans between timeline markers (marker frame → next marker−1,
  last marker → `frame_end`). Marker names are the shot names.
- per shot, the real number of keyframes falling inside the span, split into
  物件 / 鏡頭 / 燈光 / 材質 / 形狀鍵 / 場景-世界-合成器 sources
- each scene's `render.filepath`, and whether frames exist there

The driver then scans `VScode/tmp/*/` for QA preview images and each scene's
render target for output frames.

Results are cached to `.cache/last_probe.json`. If the socket times out, that
means **Blender's main thread is busy, not that Blender crashed** — the script
says so and falls back to the cache with its timestamp.

## Interpreting

Per-shot marks:

- `✔` — has keyframes, and the camera moves (or a marker binds one)
- `⚠` — has object animation but zero camera keys in the span
- `✖` — the span contains no keyframes at all

The `shot` column is `有 keyframe 的 shot 數 / 總 shot 數`. It is a **count of
measured spans, not a completion percentage.** Per `CLAUDE.md` rule 11, never
convert it into a "% done", and never describe a shot as finished just because
it has keys — keys prove animation exists, not that it was reviewed.

The bar next to each shot scales with raw keyframe count (saturating at 600).
It shows density, not quality.

Things worth calling out when they appear in the 需要注意 block:

- **時間軸重疊 / 空隙** between scenes — the final edit is one continuous
  timeline, so overlapping or gapped scene ranges are a real conflict.
- **autosave 開著** — a known trap on this 1 GB file; it blocks the main thread
  and makes every scripted command take minutes.
- **未存檔變更** — offer a save (in place; see the save-cadence rule in
  `CLAUDE.md` §10 before proposing any "Save As").

## Don't

- Don't invent shot names or storyboard mappings the report doesn't contain.
  If the user asks about a storyboard page with no scene yet, say the scene
  does not exist rather than guessing which frames it would occupy.
- Don't run this while a render or a long script is in flight — it will just
  queue behind it. Use `--cache-only` instead.
