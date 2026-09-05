import bpy, json, os
print(json.dumps({"filepath": bpy.data.filepath,
                  "basename": os.path.basename(bpy.data.filepath),
                  "worn_objs_present": len([o for o in bpy.data.objects if o.name.startswith("WRN_")]),
                  "orbit": "X5_CAM_ORBIT" in bpy.data.objects,
                  "shift_x": round(bpy.data.scenes["03_SCN_P05_XRAY_MECHANISM"].camera.data.shift_x,4),
                  "is_dirty": bpy.data.is_dirty}, ensure_ascii=False))
