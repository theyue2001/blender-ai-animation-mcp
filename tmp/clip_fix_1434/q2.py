import bpy
sc = bpy.data.scenes["SCN_P05_XRAY_MECHANISM"]
L=[]
L.append("engine=%s res=%dx%d %d%%  film_transparent=%s" % (sc.render.engine, sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage, sc.render.film_transparent))
L.append("view_transform=%s look=%s exposure=%.3f" % (sc.view_settings.view_transform, sc.view_settings.look, sc.view_settings.exposure))
L.append("use_nodes=%s" % sc.use_nodes)
cam = sc.camera
L.append("CAM %s loc=%s rot=%s lens=%.2f" % (cam.name, tuple(round(v,4) for v in cam.location), tuple(round(v,4) for v in cam.rotation_euler), cam.data.lens))
L.append("objects in scene: %d" % len(sc.objects))
names = sorted(o.name for o in sc.objects)
L.append("names: " + ", ".join(names))
print("\n".join(L))
