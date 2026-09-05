import bpy, json
out = {}
sc = bpy.data.scenes["03_SCN_P05_XRAY_MECHANISM"]
out["markers"] = [[m.frame, m.name, m.camera.name if m.camera else None] for m in sorted(sc.timeline_markers, key=lambda m: m.frame)]
out["cams"] = []
for o in sc.objects:
    if o.type == 'CAMERA':
        d = o.data
        out["cams"].append({"n": o.name, "lens": round(d.lens,1), "loc": [round(v,3) for v in o.location],
                            "rot": [round(v,3) for v in o.rotation_euler], "parent": o.parent.name if o.parent else None,
                            "dof": d.dof.use_dof, "focus": round(d.dof.focus_distance,3),
                            "fstop": round(d.dof.aperture_fstop,2),
                            "anim": bool(o.animation_data and o.animation_data.action),
                            "action": o.animation_data.action.name if (o.animation_data and o.animation_data.action) else None})
out["lights"] = [[o.name, o.data.type, round(o.data.energy,1), [round(v,2) for v in o.location]] for o in sc.objects if o.type=='LIGHT']
out["colls"] = [[c.name, len(c.objects)] for c in sc.collection.children_recursive]
out["direct_objs"] = [o.name for o in sc.collection.objects]
out["use_nodes"] = sc.use_nodes
out["world"] = sc.world.name if sc.world else None
out["view_transform"] = sc.view_settings.view_transform
out["exposure"] = sc.view_settings.exposure
ctrl = bpy.data.objects.get("X5_CTRL")
if ctrl:
    out["X5_CTRL"] = {k: (round(ctrl[k],3) if isinstance(ctrl[k], float) else ctrl[k]) for k in ctrl.keys()}
    ad = ctrl.animation_data
    if ad and ad.action:
        out["X5_CTRL_fcurves"] = [[fc.data_path, [[round(k.co[0]), round(k.co[1],3)] for k in fc.keyframe_points]] for fc in ad.action.fcurves]
print(json.dumps(out, ensure_ascii=False, indent=1))
