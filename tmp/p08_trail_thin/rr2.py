import bpy, json, traceback
OUT=r"C:/Users/mountain/AppData/Local/Temp/claude/d-----26-0825----3D---VScode/87e289ce-469b-4c17-8671-68b6cfdb67b0/scratchpad/ring2"
sc=bpy.data.scenes["04_SCN_P08_SLEEVE_TUNNEL"]
win=bpy.context.window; prev_scene=win.scene
prev=dict(pct=sc.render.resolution_percentage,fp=sc.render.filepath,frame=sc.frame_current,samples=sc.cycles.samples)
try:
    win.scene=sc; sc.render.resolution_percentage=40; sc.cycles.samples=48
    sc.frame_set(2650); sc.render.filepath=OUT+"/layout45.png"
    bpy.ops.render.render(write_still=True)
except Exception:
    print("ERR",traceback.format_exc()[-1200:])
finally:
    sc.render.resolution_percentage=prev["pct"]; sc.render.filepath=prev["fp"]
    sc.cycles.samples=prev["samples"]; sc.frame_set(prev["frame"]); win.scene=prev_scene
print("done")
