import bpy, json
SC = bpy.data.scenes["03_SCN_P05_XRAY_MECHANISM"]
prev = bpy.context.window.scene; bpy.context.window.scene = SC
rep = {}

# --- 1. key glow strength down ---
nt = bpy.data.materials["MAT_P05W_Control_Plate"].node_tree
for n in nt.nodes:
    if n.type == 'MATH' and n.operation == 'MULTIPLY' and abs(n.inputs[1].default_value - 16.0) < 1e-6:
        n.inputs[1].default_value = 4.5
        rep["key_mult"] = 4.5

# --- 2. amber LED steps up harder ---
def rekey(matname, seq):
    ntt = bpy.data.materials[matname].node_tree
    fc = ntt.animation_data.action.fcurves.find('nodes["EMIS"].inputs[1].default_value')
    for kp in fc.keyframe_points:
        for f, v in seq:
            if abs(kp.co[0]-f) < 0.5: kp.co[1] = v
    fc.update()
    return [[round(k.co[0]), round(k.co[1],2)] for k in fc.keyframe_points]
rep["amber"] = rekey("MAT_P05W_LED_Amber", [(1700,3.5),(1724,3.5),(1736,7.0),(1760,7.0),(1772,12.0)])

# --- 3. a touch more skin light (fade-up keys hold the peak value) ---
for nm, en in (("LGT_P05W_Key",180.0), ("LGT_P05W_Skin_L",65.0)):
    o = bpy.data.objects[nm]
    o.data.energy = en
    fc = o.data.animation_data.action.fcurves.find("energy")
    fc.keyframe_points[-1].co[1] = en
    fc.update()
rep["lights"] = {"Key":180.0, "Skin_L":65.0}

# --- 4. isolation verification ---
v = {}
orig_prod = [o for o in bpy.data.collections["P05_XRAY_SHELL"].objects] + \
            [o for o in bpy.data.collections["P05_XRAY_INTERNAL"].objects]
v["xray_objs_unanimated"] = sum(1 for o in orig_prod if o.animation_data and o.animation_data.action)
v["src_scene01_untouched"] = all(
    not (bpy.data.objects[n].animation_data and bpy.data.objects[n].animation_data.action)
    for n in ("Male","Underwear","P01_STRAP_UPPER","P01_STRAP_LOWER"))
worn = list(bpy.data.collections["P05_WORN_PRODUCT"].objects)+list(bpy.data.collections["P05_WORN_BODY"].objects)
v["worn_slots_all_OBJECT"] = all(s.link=='OBJECT' for o in worn for s in o.material_slots)
v["worn_mats_all_P05W"] = sorted({s.material.name.split("_")[1] for o in worn for s in o.material_slots if s.material})
v["worn_shares_mesh_data"] = sum(1 for o in worn if o.data.users > 1)
v["worn_in_other_scenes"] = [s.name for s in bpy.data.scenes
                             if s is not SC and any(o.name.startswith("WRN_") or o.name.startswith("P05_WORN")
                                                    or o.name.startswith("LGT_P05W") for o in s.objects)]
v["orig_mats_no_W_nodes"] = all("KEY_UP" not in bpy.data.materials[m].node_tree.nodes
                                for m in ("MAT_P05_Control_Plate",))
v["orig_shell_driver_alive"] = bool(bpy.data.materials["MAT_P05_Shell_Smoked"].node_tree.animation_data
                                    and bpy.data.materials["MAT_P05_Shell_Smoked"].node_tree.animation_data.drivers)
v["shared_scene01_mats_untouched"] = {
    m: bpy.data.materials[m].node_tree.animation_data.action.name
    for m in ("SHOT1_HUMAN_Male_0","Rubber #4") }
v["scene_obj_counts"] = {s.name: len(s.objects) for s in bpy.data.scenes}
v["shift_x_before_reveal"] = round(SC.camera.data.animation_data.action.fcurves.find("shift_x").evaluate(1500), 4)
v["worn_hidden_at_1500"] = all(
    o.animation_data.action.fcurves.find("hide_render").evaluate(1500) > 0.5 for o in worn)
rep["verify"] = v
bpy.ops.wm.save_mainfile()
print(json.dumps(rep, ensure_ascii=False, indent=1))
bpy.context.window.scene = prev
