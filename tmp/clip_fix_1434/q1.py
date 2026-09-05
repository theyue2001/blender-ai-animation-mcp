import bpy, os
L=[]
L.append("FILE: %s" % bpy.data.filepath)
L.append("window scene: %s  frame %d" % (bpy.context.window.scene.name, bpy.context.window.scene.frame_current))
for sc in bpy.data.scenes:
    L.append("SCENE %-50s %d-%d cam=%s" % (sc.name, sc.frame_start, sc.frame_end, sc.camera.name if sc.camera else None))
    for m in sorted(sc.timeline_markers, key=lambda m:m.frame):
        L.append("    marker %5d %-40s cam=%s" % (m.frame, m.name, m.camera.name if m.camera else None))
print("\n".join(L))
