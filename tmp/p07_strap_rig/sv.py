import bpy
bpy.ops.wm.save_mainfile()
print("saved", bpy.data.filepath)
