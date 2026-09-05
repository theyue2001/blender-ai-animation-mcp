import bpy, json, os
o = {}
o["filepath"] = os.path.basename(bpy.data.filepath)
o["is_dirty"] = bpy.data.is_dirty
o["scenes"] = {s.name: [s.frame_start, s.frame_end, s.render.fps] for s in bpy.data.scenes}
SC = bpy.data.scenes.get("03_SCN_P05_XRAY_MECHANISM")
if SC is None:
    print(json.dumps({"ERROR":"P05 scene missing", **o})); raise SystemExit
chk = {}
chk["WRN_objects"] = len([x for x in bpy.data.objects if x.name.startswith("WRN_")])
chk["WRN_in_P05_scene"] = len([x for x in SC.objects if x.name.startswith("WRN_")])
chk["P05W_materials"] = len([m for m in bpy.data.materials if m.name.startswith("MAT_P05W")])
chk["worn_root"] = "P05_WORN_ROOT" in bpy.data.objects
chk["worn_root_loc"] = [round(v,3) for v in bpy.data.objects["P05_WORN_ROOT"].location] if chk["worn_root"] else None
chk["gobo"] = "P05_GOBO_RIGHT" in bpy.data.objects
if chk["gobo"]:
    g = bpy.data.objects["P05_GOBO_RIGHT"]
    chk["gobo_parent"] = g.parent.name if g.parent else None
    chk["gobo_local"] = [round(v,2) for v in g.location]
    mr = bpy.data.materials["MAT_P05_GOBO"].node_tree.nodes["EDGE"]
    chk["gobo_ramp"] = [round(mr.inputs[1].default_value,3), round(mr.inputs[2].default_value,3)]
chk["orbit"] = "X5_CAM_ORBIT" in bpy.data.objects
if chk["orbit"]:
    ob = bpy.data.objects["X5_CAM_ORBIT"]
    chk["cam_parented_to_orbit"] = SC.camera.parent.name if SC.camera.parent else None
    chk["orbit_keys"] = [[round(k.co[0]), round(k.co[1],4)] for k in ob.animation_data.action.fcurves[0].keyframe_points]
chk["shift_x"] = round(SC.camera.data.shift_x, 4)
chk["cam_loc_keys"] = [[round(k.co[0])] + [round(f.evaluate(k.co[0]),3) for f in SC.camera.animation_data.action.fcurves if f.data_path=="location"]
                       for k in SC.camera.animation_data.action.fcurves[0].keyframe_points]
chk["lights_P05W"] = len([x for x in bpy.data.objects if x.name.startswith("LGT_P05W")])
lk = bpy.data.objects.get("LGT_P05W_Key")
chk["key_light_keys"] = [[round(k.co[0]), round(k.co[1],1)] for k in lk.data.animation_data.action.fcurves.find("energy").keyframe_points] if lk and lk.data.animation_data else None
chk["light_linking"] = bool(bpy.data.objects["LGT_P05_Key_Top"].light_linking.receiver_collection)
w0 = list(bpy.data.collections["P05_WORN_BODY"].objects)[0] if "P05_WORN_BODY" in bpy.data.collections else None
chk["hide_render_keys"] = [[round(k.co[0]), round(k.co[1],1)] for k in w0.animation_data.action.fcurves.find("hide_render").keyframe_points] if w0 and w0.animation_data else None
nt = bpy.data.materials.get("MAT_P05W_Control_Plate")
chk["key_glow_nodes"] = ("KEY_UP" in nt.node_tree.nodes and "FACE_MOD" in nt.node_tree.nodes) if nt else False
chk["press_keys"] = [round(k.co[0]) for k in nt.node_tree.animation_data.action.fcurves[0].keyframe_points if abs(k.co[1]-1.0)<1e-6] if nt and nt.node_tree.animation_data else None
amb = bpy.data.materials.get("MAT_P05W_LED_Amber")
chk["amber_keys"] = [[round(k.co[0]),round(k.co[1],1)] for k in amb.node_tree.animation_data.action.fcurves[0].keyframe_points] if amb and amb.node_tree.animation_data else None
o["checks"] = chk
print(json.dumps(o, ensure_ascii=False, indent=1))
