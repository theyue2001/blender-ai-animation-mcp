import bpy, json
out = {}
out["file"] = bpy.data.filepath
out["scenes"] = [{"name": s.name, "start": s.frame_start, "end": s.frame_end,
                  "cur": s.frame_current, "cam": s.camera.name if s.camera else None,
                  "engine": s.render.engine, "res": [s.render.resolution_x, s.render.resolution_y, s.render.resolution_percentage],
                  "nobj": len(s.objects)} for s in bpy.data.scenes]
out["window_scene"] = bpy.context.window.scene.name
sc = bpy.data.scenes.get("SCN_P05_XRAY_MECHANISM")
if sc:
    out["p05_markers"] = [[m.frame, m.name, m.camera.name if m.camera else None] for m in sorted(sc.timeline_markers, key=lambda m: m.frame)]
    out["p05_cams"] = [o.name for o in sc.objects if o.type == 'CAMERA']
    out["p05_lights"] = [[o.name, o.data.type, round(o.data.energy,2)] for o in sc.objects if o.type=='LIGHT']
    out["p05_colls"] = [c.name for c in sc.collection.children_recursive]
    out["p05_root_objs"] = [o.name for o in sc.collection.objects][:40]
    out["p05_use_nodes"] = sc.use_nodes
    out["p05_world"] = sc.world.name if sc.world else None
print(json.dumps(out, ensure_ascii=False, indent=1))
