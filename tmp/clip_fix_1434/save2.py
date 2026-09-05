import bpy, os
OUT = r"d:\接案\26_0825_紅犀牛3D動畫\VScode\tmp\clip_fix_1434"
JOB = os.path.join(OUT, "save_job.txt")
def _run():
    import traceback
    try:
        p=bpy.data.filepath
        bpy.ops.wm.save_mainfile()
        open(JOB,"w").write("done saved=%s size=%d dirty=%s" % (p, os.path.getsize(p), bpy.data.is_dirty))
    except Exception:
        open(JOB,"w").write("ERR\n"+traceback.format_exc())
    return None
open(JOB,"w").write("running")
bpy.app.timers.register(_run, first_interval=0.1)
print("save dispatched:", bpy.data.filepath)
