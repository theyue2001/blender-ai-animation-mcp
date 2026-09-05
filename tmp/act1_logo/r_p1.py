import bpy, os, json
OUT = r"d:\接案\26_0825_紅犀牛3D動畫\VScode\tmp\act1_logo"
JOB = os.path.join(OUT, "job.txt")
FRAMES = [198]
TAG = "probe060"
PCT = 100
SAMP = 128
def _run():
    import traceback
    sc = [s for s in bpy.data.scenes if "CAM_Opening_Silhouette" in s.objects][0]
    win=bpy.context.window; prev=win.scene; r=sc.render
    P=dict(e=r.engine,pct=r.resolution_percentage,fp=r.filepath,ub=r.use_border,
           uc=r.use_crop_to_border,sm=sc.cycles.samples,fr=sc.frame_current)
    mk = [m for m in sc.timeline_markers if m.camera]
    MP = [(m, m.camera) for m in mk]
    try:
        win.scene=sc
        r.engine='CYCLES'; r.use_border=False; r.use_crop_to_border=False
        r.resolution_percentage=PCT; sc.cycles.samples=SAMP
        cam = sc.objects["CAM_Opening_Silhouette"]
        sc.camera = cam
        for m,_ in MP: m.camera = cam
        done=[]
        for f in FRAMES:
            sc.frame_set(f)
            r.filepath=os.path.join(OUT,"%s_%04d.png"%(TAG,f))
            bpy.ops.render.render(write_still=True)
            done.append(f)
            open(JOB,"w").write("running %s done=%s" % (TAG, done))
        open(JOB,"w").write("done %s frames=%s scene=%s dirty=%s" % (TAG, done, sc.name, bpy.data.is_dirty))
    except Exception:
        open(JOB,"w").write("ERR\n"+traceback.format_exc())
    finally:
        for m,c in MP: m.camera = c
        r.engine=P['e']; r.resolution_percentage=P['pct']; r.filepath=P['fp']
        r.use_border=P['ub']; r.use_crop_to_border=P['uc']; sc.cycles.samples=P['sm']
        sc.frame_set(P['fr']); win.scene=prev
    return None
open(JOB,"w").write("running "+TAG)
bpy.app.timers.register(_run, first_interval=0.1)
print("dispatched "+TAG)
