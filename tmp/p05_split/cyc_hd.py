import bpy, os, json
OUT = "D:/\u63a5\u6848/26_0825_\u7d05\u7280\u725b3D\u52d5\u756b/VScode/tmp/p05_split/"
FRAMES = [936, 1080, 1224]
TAG = "hd"
PCT = 100
SAMPLES = 96

def do_render():
    SC = bpy.data.scenes["03_SCN_P05_XRAY_MECHANISM"]
    prev = bpy.context.window.scene
    prevf = {s.name: s.frame_current for s in bpy.data.scenes}
    bpy.context.window.scene = SC
    r = SC.render
    sav = (r.engine, r.resolution_percentage, r.filepath, SC.cycles.samples,
           SC.cycles.use_denoising, r.image_settings.file_format)
    try:
        r.engine = 'CYCLES'
        r.resolution_percentage = PCT
        SC.cycles.samples = SAMPLES
        SC.cycles.use_denoising = True
        r.image_settings.file_format = 'PNG'
        for f in FRAMES:
            SC.frame_set(f)
            r.filepath = OUT + "%s_%d.png" % (TAG, f)
            bpy.ops.render.render(write_still=True)
    except Exception as e:
        with open(OUT + TAG + ".err", "w") as fh: fh.write(repr(e))
    finally:
        (r.engine, r.resolution_percentage, r.filepath, SC.cycles.samples,
         SC.cycles.use_denoising, r.image_settings.file_format) = sav
        for s in bpy.data.scenes:
            if s.name in prevf: s.frame_set(prevf[s.name])
        bpy.context.window.scene = prev
        with open(OUT + TAG + ".done", "w") as fh: fh.write("ok")
    return None

for p in (TAG + ".done", TAG + ".err"):
    if os.path.exists(OUT + p): os.remove(OUT + p)
bpy.app.timers.register(do_render, first_interval=0.2)
print(json.dumps({"queued": FRAMES, "tag": TAG, "pct": PCT, "samples": SAMPLES,
                  "film_transparent": bpy.data.scenes["03_SCN_P05_XRAY_MECHANISM"].render.film_transparent}))
