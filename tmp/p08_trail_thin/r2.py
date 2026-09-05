import bpy, json, traceback
OUT=r"C:/Users/mountain/AppData/Local/Temp/claude/d-----26-0825----3D---VScode/87e289ce-469b-4c17-8671-68b6cfdb67b0/scratchpad/qa1"
sc=bpy.data.scenes["04_SCN_P08_SLEEVE_TUNNEL"]
win=bpy.context.window; prev_scene=win.scene
prev=dict(eng=sc.render.engine,rx=sc.render.resolution_x,ry=sc.render.resolution_y,
          pct=sc.render.resolution_percentage,fp=sc.render.filepath,frame=sc.frame_current,
          ff=sc.render.image_settings.file_format)
done=[]
try:
    win.scene=sc
    sc.render.engine='BLENDER_EEVEE_NEXT'
    sc.render.resolution_x=960; sc.render.resolution_y=540; sc.render.resolution_percentage=100
    sc.render.image_settings.file_format='PNG'
    for f in [2410,2424,2470,2505,2538]:
        sc.frame_set(f)
        sc.render.filepath=OUT+"/f%d.png"%f
        bpy.ops.render.render(write_still=True)
        done.append(f)
except Exception as e:
    print("ERR",traceback.format_exc()[-1500:])
finally:
    sc.render.engine=prev["eng"]; sc.render.resolution_x=prev["rx"]; sc.render.resolution_y=prev["ry"]
    sc.render.resolution_percentage=prev["pct"]; sc.render.filepath=prev["fp"]
    sc.render.image_settings.file_format=prev["ff"]
    sc.frame_set(prev["frame"]); win.scene=prev_scene
print(json.dumps({"done":done}))
