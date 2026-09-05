import bpy, os, json
OUT = r"d:\接案\26_0825_紅犀牛3D動畫\VScode\tmp\clip_fix_1434"
JOB = os.path.join(OUT, "cyc_job.txt")
def _run():
    import traceback
    sc = bpy.data.scenes["SCN_P05_XRAY_MECHANISM"]
    win = bpy.context.window; prev = win.scene
    r = sc.render
    P = dict(e=r.engine, pct=r.resolution_percentage, fp=r.filepath,
             sm=sc.cycles.samples, ad=sc.cycles.use_adaptive_sampling)
    me = bpy.data.objects["X5_16_0.002"].data
    bk = json.load(open(os.path.join(OUT,"vert_backup.json")))["coords"]
    fixed = {}
    log=[]
    try:
        for k, co in bk.items():
            i = int(k); v = me.vertices[i]
            fixed[i] = (v.co.x, v.co.y, v.co.z)
            v.co = co
        me.update()
        log.append("reverted %d verts" % len(bk))
        win.scene = sc; sc.frame_set(1434)
        r.engine='CYCLES'; r.resolution_percentage=100
        sc.cycles.samples = 64; sc.cycles.use_adaptive_sampling = True
        r.filepath = os.path.join(OUT, "cyc_before_1434.png")
        bpy.ops.render.render(write_still=True)
        log.append("rendered before")
    except Exception:
        log.append("ERR\n"+traceback.format_exc())
    finally:
        for i,(x,y,z) in fixed.items():
            me.vertices[i].co = (x,y,z)
        me.update()
        log.append("re-applied fix to %d verts" % len(fixed))
        r.engine=P['e']; r.resolution_percentage=P['pct']; r.filepath=P['fp']
        sc.cycles.samples=P['sm']; sc.cycles.use_adaptive_sampling=P['ad']
        win.scene = prev
        open(JOB,"w").write("done\n"+"\n".join(log))
    return None
open(JOB,"w").write("running")
bpy.app.timers.register(_run, first_interval=0.1)
print("dispatched")
