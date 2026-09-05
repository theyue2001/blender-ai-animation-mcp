import bpy, os
OUT = r"d:\接案\26_0825_紅犀牛3D動畫\VScode\tmp\clip_fix_1434"
JOB = os.path.join(OUT, "cyc_job.txt")
def _run():
    import traceback
    sc = bpy.data.scenes["SCN_P05_XRAY_MECHANISM"]
    win = bpy.context.window; prev = win.scene
    r = sc.render
    P = dict(e=r.engine, pct=r.resolution_percentage, fp=r.filepath, f=sc.frame_current,
             sm=sc.cycles.samples, ad=sc.cycles.use_adaptive_sampling)
    try:
        win.scene = sc; sc.frame_set(1434)
        r.engine='CYCLES'; r.resolution_percentage=100
        sc.cycles.samples = 64; sc.cycles.use_adaptive_sampling = True
        r.filepath = os.path.join(OUT, "cyc_after_1434.png")
        bpy.ops.render.render(write_still=True)
        open(JOB,"w").write("done")
    except Exception:
        open(JOB,"w").write("ERR\n"+traceback.format_exc())
    finally:
        r.engine=P['e']; r.resolution_percentage=P['pct']; r.filepath=P['fp']
        sc.cycles.samples=P['sm']; sc.cycles.use_adaptive_sampling=P['ad']
        win.scene = prev
    return None
if os.path.exists(JOB): os.remove(JOB)
open(JOB,"w").write("running")
bpy.app.timers.register(_run, first_interval=0.1)
print("dispatched")
