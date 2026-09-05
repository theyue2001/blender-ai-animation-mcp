import bpy, os, json
old=bpy.data.filepath
new=old.replace("_v034.blend","_v035.blend")
assert new!=old, ("unexpected filename", old)
bpy.ops.wm.save_as_mainfile(filepath=new)
print(json.dumps({"from":os.path.basename(old),"to":os.path.basename(bpy.data.filepath),
                  "size_mb":round(os.path.getsize(bpy.data.filepath)/1e6,1),
                  "now_editing":bpy.data.filepath}))
