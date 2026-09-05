import bpy, os
OUT = r"d:\接案\26_0825_紅犀牛3D動畫\VScode\tmp\clip_fix_1434"
JOB = os.path.join(OUT, "cyc_job.txt")
def _run():
    import traceback
    sc = bpy.data.scenes["SCN_P05_XRAY_MECHANISM"]
    win=bpy.context.window; prev=win.scene; r=sc.render
    P=dict(e=r.engine,pct=r.resolution_percentage,fp=r.filepath,ub=r.use_border,uc=r.use_crop_to_border,
           b=(r.border_min_x,r.border_max_x,r.border_min_y,r.border_max_y),sm=sc.cycles.samples)
    try:
        win.scene=sc; sc.frame_set(1434)
        r.engine='CYCLES'
        # 1) full frame
        r.use_border=False; r.use_crop_to_border=False
        r.resolution_percentage=100; sc.cycles.samples=64
        r.filepath=os.path.join(OUT,"cyc_v3_1434.png")
        bpy.ops.render.render(write_still=True)
        # 2) zoom on the circled area, same crop as before
        r.resolution_percentage=400; sc.cycles.samples=256
        r.use_border=True; r.use_crop_to_border=True
        r.border_min_x, r.border_max_x = 1256/1920.0, 1500/1920.0
        r.border_min_y, r.border_max_y = (1080-495)/1080.0, (1080-280)/1080.0
        r.filepath=os.path.join(OUT,"zoom_circle_after.png")
        bpy.ops.render.render(write_still=True)
        open(JOB,"w").write("done")
    except Exception:
        open(JOB,"w").write("ERR\n"+traceback.format_exc())
    finally:
        r.engine=P['e']; r.resolution_percentage=P['pct']; r.filepath=P['fp']
        r.use_border=P['ub']; r.use_crop_to_border=P['uc']
        r.border_min_x,r.border_max_x,r.border_min_y,r.border_max_y=P['b']
        sc.cycles.samples=P['sm']; win.scene=prev
    return None
open(JOB,"w").write("running")
bpy.app.timers.register(_run, first_interval=0.1)
print("dispatched")
