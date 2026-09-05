# Runs INSIDE Blender via the BlenderMCP socket. READ-ONLY.
# Never calls view_layer.update() / depsgraph — this file must stay side-effect free.
# The driver prepends:  OUT_PATH = r"...json"
import bpy, json, os, time

_key_cache = {}

def action_keys(act):
    if act is None:
        return []
    k = act.name
    if k in _key_cache:
        return _key_cache[k]
    frames = []
    for fcu in act.fcurves:
        n = len(fcu.keyframe_points)
        if not n:
            continue
        buf = [0.0] * (2 * n)
        fcu.keyframe_points.foreach_get("co", buf)
        frames.extend(buf[0::2])
    frames.sort()
    _key_cache[k] = frames
    return frames

def act_of(holder):
    ad = getattr(holder, "animation_data", None)
    return ad.action if ad and ad.action else None

def nla_ranges(holder):
    ad = getattr(holder, "animation_data", None)
    if not ad:
        return []
    out = []
    for tr in ad.nla_tracks:
        for st in tr.strips:
            out.append([round(st.frame_start, 1), round(st.frame_end, 1), st.name])
    return out

def n_drivers(holder):
    ad = getattr(holder, "animation_data", None)
    return len(ad.drivers) if ad else 0

def scene_sources(sc):
    """[(category, label, keyframe_list)] for everything animated that belongs to this scene."""
    src = []
    seen_mat = set()
    for ob in sc.objects:
        if ob.type == "CAMERA":
            cat = "cam"
        elif ob.type == "LIGHT":
            cat = "lgt"
        else:
            cat = "obj"
        a = act_of(ob)
        if a:
            src.append((cat, ob.name, action_keys(a)))
        d = getattr(ob, "data", None)
        if d is not None:
            a = act_of(d)
            if a:
                src.append((cat, ob.name + ".data", action_keys(a)))
            sk = getattr(d, "shape_keys", None)
            if sk is not None:
                a = act_of(sk)
                if a:
                    src.append(("shp", ob.name + ".shapekeys", action_keys(a)))
        for slot in getattr(ob, "material_slots", []):
            m = slot.material
            if not m or m.name in seen_mat:
                continue
            seen_mat.add(m.name)
            a = act_of(m)
            if a:
                src.append(("mat", m.name, action_keys(a)))
            nt = getattr(m, "node_tree", None)
            if nt is not None:
                a = act_of(nt)
                if a:
                    src.append(("mat", m.name + ".nodes", action_keys(a)))
    a = act_of(sc)
    if a:
        src.append(("scn", sc.name + " (scene)", action_keys(a)))
    if sc.world is not None:
        for h, lbl in ((sc.world, " (world)"), (getattr(sc.world, "node_tree", None), " (world nodes)")):
            if h is None:
                continue
            a = act_of(h)
            if a:
                src.append(("scn", sc.world.name + lbl, action_keys(a)))
    if sc.use_nodes and sc.node_tree is not None:
        a = act_of(sc.node_tree)
        if a:
            src.append(("scn", sc.name + " (compositor)", action_keys(a)))
    return src

def count_in(keys, lo, hi):
    # keys is sorted
    import bisect
    return bisect.bisect_right(keys, hi) - bisect.bisect_left(keys, lo)

def abspath(p):
    try:
        return bpy.path.abspath(p)
    except Exception:
        return p

data = {
    "probed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    "blend": bpy.data.filepath,
    "blend_mtime": None,
    "blender": bpy.app.version_string,
    "is_dirty": bool(bpy.data.is_dirty),
    "window_scene": bpy.context.window.scene.name if bpy.context.window else None,
    "autosave": bool(bpy.context.preferences.filepaths.use_auto_save_temporary_files),
    "scenes": [],
}
try:
    if data["blend"] and os.path.exists(data["blend"]):
        data["blend_mtime"] = time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(data["blend"])))
except Exception:
    pass

for sc in bpy.data.scenes:
    fs, fe = sc.frame_start, sc.frame_end
    mk = sorted(
        [{"frame": m.frame, "name": m.name, "camera": (m.camera.name if m.camera else None)}
         for m in sc.timeline_markers],
        key=lambda x: x["frame"],
    )
    # shots = marker -> next marker-1, clipped to the scene range.
    # Markers can sit outside [fs, fe]; the last one at or before fs still
    # governs the head of the scene, so it names the leading span.
    inr = [m for m in mk if fs <= m["frame"] <= fe]
    outr = [m for m in mk if not (fs <= m["frame"] <= fe)]
    before = [m for m in mk if m["frame"] < fs]
    shots = []
    if inr:
        if inr[0]["frame"] > fs:
            head = before[-1] if before else None
            shots.append({"name": (head["name"] + " (承接)") if head else "(marker 前)",
                          "start": fs, "end": inr[0]["frame"] - 1,
                          "camera": head["camera"] if head else None})
        for i, m in enumerate(inr):
            end = inr[i + 1]["frame"] - 1 if i + 1 < len(inr) else fe
            shots.append({"name": m["name"], "start": m["frame"],
                          "end": min(end, fe), "camera": m["camera"]})
    elif before:
        shots.append({"name": before[-1]["name"] + " (承接)", "start": fs, "end": fe,
                      "camera": before[-1]["camera"]})
    else:
        shots.append({"name": "(whole scene)", "start": fs, "end": fe, "camera": None})

    src = scene_sources(sc)
    for sh in shots:
        lo, hi = sh["start"], sh["end"]
        tally = {"obj": 0, "cam": 0, "lgt": 0, "mat": 0, "shp": 0, "scn": 0}
        movers = set()
        for cat, label, keys in src:
            c = count_in(keys, lo, hi)
            if c:
                tally[cat] += c
                movers.add(label)
        sh["keys"] = tally
        sh["total_keys"] = sum(tally.values())
        sh["n_animated"] = len(movers)
        sh["frames"] = max(0, hi - lo + 1)

    cams = [o.name for o in sc.objects if o.type == "CAMERA"]
    lights = [o.name for o in sc.objects if o.type == "LIGHT"]
    drv = sum(n_drivers(o) for o in sc.objects)
    nla = []
    for o in sc.objects:
        for r in nla_ranges(o):
            nla.append([o.name] + r)

    rp = sc.render.filepath
    data["scenes"].append({
        "name": sc.name,
        "frame_start": fs,
        "frame_end": fe,
        "fps": sc.render.fps / (sc.render.fps_base or 1.0),
        "engine": sc.render.engine,
        "res": [sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage],
        "samples": getattr(getattr(sc, "cycles", None), "samples", None),
        "camera": sc.camera.name if sc.camera else None,
        "n_objects": len(sc.objects),
        "cameras": cams,
        "lights": lights,
        "n_drivers": drv,
        "markers": mk,
        "markers_outside": outr,
        "shots": shots,
        "n_animated_sources": len(src),
        "nla": nla[:40],
        "render_filepath": rp,
        "render_abspath": abspath(rp),
    })

with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=1)
print("PROBE_OK " + str(len(data["scenes"])))
