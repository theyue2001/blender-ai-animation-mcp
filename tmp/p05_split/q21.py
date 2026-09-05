import bpy, json
SC = bpy.data.scenes["03_SCN_P05_XRAY_MECHANISM"]
prev = bpy.context.window.scene; bpy.context.window.scene = SC
ctrl = bpy.data.objects["X5_CTRL"]
out = {}
act = ctrl.animation_data.action
out["ctrl_action"] = act.name
out["ctrl_fcurves"] = [fc.data_path for fc in act.fcurves]
fc = act.fcurves.find('["amber"]')
out["amber_fcurve_found"] = fc is not None
if fc:
    out["amber_eval"] = {f: round(fc.evaluate(f), 3) for f in (900, 950, 1050, 1150, 1248, 1440)}
    out["amber_keys"] = [[round(k.co[0]), round(k.co[1],3)] for k in fc.keyframe_points]
# evaluate live at frame 1248
SC.frame_set(1248)
out["ctrl_amber_live_1248"] = round(ctrl["amber"], 4)
dg = bpy.context.evaluated_depsgraph_get()
ce = ctrl.evaluated_get(dg)
out["ctrl_amber_evaluated_1248"] = round(ce["amber"], 4)
for mn, node in (("MAT_P05_Silicone_White","V_AMBER"), ("MAT_P05_Cartridge_Amber","V_AMBER")):
    m = bpy.data.materials[mn]
    me = m.evaluated_get(dg)
    out[mn] = {"V_AMBER_orig": round(m.node_tree.nodes[node].outputs[0].default_value,4),
               "V_AMBER_eval": round(me.node_tree.nodes[node].outputs[0].default_value,4),
               "drivers": [[d.data_path, d.driver.expression,
                            [[v.name, (v.targets[0].id.name if v.targets[0].id else None), v.targets[0].data_path] for v in d.driver.variables]]
                           for d in (m.node_tree.animation_data.drivers if m.node_tree.animation_data else [])]}
nt = bpy.data.materials["MAT_P05_Silicone_White"].node_tree
out["MIX_SIL_fac_from"] = nt.nodes["MIX_SIL"].inputs[0].links[0].from_node.name if nt.nodes["MIX_SIL"].inputs[0].links else None
out["SILICONE_base_from"] = nt.nodes["SILICONE"].inputs["Base Color"].links[0].from_node.name if nt.nodes["SILICONE"].inputs["Base Color"].links else None
nt2 = bpy.data.materials["MAT_P05_Cartridge_Amber"].node_tree
out["MIX_AMB_fac_from"] = nt2.nodes["MIX_AMB"].inputs[0].links[0].from_node.name if nt2.nodes["MIX_AMB"].inputs[0].links else None
print(json.dumps(out, ensure_ascii=False, indent=1))
bpy.context.window.scene = prev
