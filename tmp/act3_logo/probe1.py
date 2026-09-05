import bpy
L=[]
L.append("FILE: %s" % bpy.data.filepath)
L.append("WINDOW SCENE: %s" % bpy.context.window.scene.name)
L.append("--- SCENES ---")
for sc in bpy.data.scenes:
    L.append("  %-45s f%d-%d  objs=%d  cam=%s" % (sc.name, sc.frame_start, sc.frame_end, len(sc.objects), sc.camera.name if sc.camera else None))
    mk = sorted(sc.timeline_markers, key=lambda m: m.frame)
    if mk:
        L.append("     markers: " + " | ".join("%d:%s%s" % (m.frame, m.name, ("->"+m.camera.name) if m.camera else "") for m in mk[:24]))
print("\n".join(L))
