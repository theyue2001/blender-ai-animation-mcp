import bpy
bpy.data.lights["LGT_Opening_Logo_Highlight"].energy = 2.0
bpy.ops.wm.save_mainfile()
print("energy", bpy.data.lights["LGT_Opening_Logo_Highlight"].energy)
