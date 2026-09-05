import bpy
print("ALIVE file=%s window_scene=%s frame=%d" % (bpy.data.filepath, bpy.context.window.scene.name, bpy.context.window.scene.frame_current))
