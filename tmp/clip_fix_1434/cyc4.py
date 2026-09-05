import bpy, os
OUT = r"d:\接案\26_0825_紅犀牛3D動畫\VScode\tmp\clip_fix_1434"
JOB = os.path.join(OUT, "cyc_job.txt")
def _run():
    import traceback
    sc = bpy.data.scenes["SCN_P05_XRAY_MECHANISM"]
    win=bpy.context.window; prev=win.scene; r=sc.render
    P=dict(e=r.engine,pct=r.resolution_percentage,fp=r.filepath,ub=r.use_border,
           uc=r.use_crop_to_border,sm=sc.cycles.samples)
    try:
        win.scene=sc; sc.frame_set(1434)
        r.engine='CYCLES'; r.use_border=False; r.use_crop_to_border=False
        r.resolution_percentage=100; sc.cycles.samples=160
        r.filepath=os.path.join(OUT,"NOW_1434.png")
        bpy.ops.render.render(write_still=True)
        open(JOB,"w").write("done  scene=%s frame=%d engine=CYCLES samples=160 dirty=%s" % (
            sc.name, sc.frame_current, bpy.data.is_dirty))
    except Exception:
        open(JOB,"w").write("ERR\n"+traceback.format_exc())
    finally:
        r.engine=P['e']; r.resolution_percentage=P['pct']; r.filepath=P['fp']
        r.use_border=P['ub']; r.use_crop_to_border=P['uc']; sc.cycles.samples=P['sm']
        win.scene=prev
    return None
open(JOB,"w").write("running")
bpy.app.timers.register(_run, first_interval=0.1)
print("dispatched")
