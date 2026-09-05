import bpy, json
out = {}
out["file"] = bpy.data.filepath
out["scenes"] = [(s.name, s.frame_start, s.frame_end, s.camera.name if s.camera else None) for s in bpy.data.scenes]
sc = bpy.data.scenes.get("01_SCN_OPENING_P01_P03")
if sc:
    out["markers"] = [(m.name, m.frame, m.camera.name if m.camera else None) for m in sc.timeline_markers]
    out["engine"] = sc.render.engine
    out["res"] = (sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage)
    out["view_transform"] = sc.view_settings.view_transform
    out["exposure"] = sc.view_settings.exposure
    out["use_nodes"] = sc.use_nodes
    out["cams"] = [o.name for o in sc.objects if o.type=='CAMERA']
    out["lights"] = [(o.name, o.data.type, o.data.energy, tuple(round(v,3) for v in o.location)) for o in sc.objects if o.type=='LIGHT']
    out["top_colls"] = [c.name for c in sc.collection.children]
    out["n_objects"] = len(sc.objects)
print(json.dumps(out, ensure_ascii=False, indent=1))
