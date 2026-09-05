import bpy, json, os
ctrl = bpy.data.objects.get("X5_CTRL")
out = {"filepath": os.path.basename(bpy.data.filepath), "is_dirty": bpy.data.is_dirty}
out["ctrl_keys"] = list(ctrl.keys()) if ctrl else None
act = ctrl.animation_data.action if ctrl and ctrl.animation_data else None
out["ctrl_action"] = act.name if act else None
out["ctrl_fcurves"] = [fc.data_path for fc in act.fcurves] if act else None
for mn in ("MAT_P05_Silicone_White","MAT_P05_Cartridge_Amber"):
    m = bpy.data.materials.get(mn)
    out[mn] = {"exists": m is not None}
    if m:
        out[mn]["nodes"] = [n.name for n in m.node_tree.nodes]
        ad = m.node_tree.animation_data
        out[mn]["drivers"] = [[d.data_path, d.driver.expression,
                               [[v.name, (v.targets[0].id.name if v.targets[0].id else None), v.targets[0].data_path]
                                for v in d.driver.variables]] for d in (ad.drivers if ad else [])]
out["scene_range"] = [bpy.data.scenes["03_SCN_P05_XRAY_MECHANISM"].frame_start,
                      bpy.data.scenes["03_SCN_P05_XRAY_MECHANISM"].frame_end]
print(json.dumps(out, ensure_ascii=False, indent=1))
