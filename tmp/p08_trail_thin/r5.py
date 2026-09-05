import bpy, json, traceback
OUT=r"C:/Users/mountain/AppData/Local/Temp/claude/d-----26-0825----3D---VScode/87e289ce-469b-4c17-8671-68b6cfdb67b0/scratchpad/qa4"
sc=bpy.data.scenes["04_SCN_P08_SLEEVE_TUNNEL"]
win=bpy.context.window; prev_scene=win.scene
prev=dict(pct=sc.render.resolution_percentage,fp=sc.render.filepath,frame=sc.frame_current,samples=sc.cycles.samples)
done=[]
try:
    win.scene=sc
    sc.render.resolution_percentage=40; sc.cycles.samples=40
    for f in [2548,2554,2558,2562,2565,2568,2571,2574,2577,2584]:
        sc.frame_set(f); sc.render.filepath=OUT+"/f%d.png"%f
        bpy.ops.render.render(write_still=True); done.append(f)
except Exception:
    print("ERR",traceback.format_exc()[-1200:])
finally:
    sc.render.resolution_percentage=prev["pct"]; sc.render.filepath=prev["fp"]
    sc.cycles.samples=prev["samples"]; sc.frame_set(prev["frame"]); win.scene=prev_scene
print(json.dumps({"done":done}))
