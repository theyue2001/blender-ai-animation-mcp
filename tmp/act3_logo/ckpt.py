import bpy, os
old = bpy.data.filepath
new = old.replace("_v035.blend", "_v036.blend")
assert new != old and not os.path.exists(new), (old, new, os.path.exists(new))
bpy.ops.wm.save_mainfile()          # flush v035 first
bpy.ops.wm.save_as_mainfile(filepath=new)
print("v035 saved, checkpoint ->", bpy.data.filepath)
