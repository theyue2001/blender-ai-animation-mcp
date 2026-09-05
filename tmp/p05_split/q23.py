import bpy, json
SC = bpy.data.scenes["03_SCN_P05_XRAY_MECHANISM"]
prev = bpy.context.window.scene; bpy.context.window.scene = SC
out={}
ctrl = bpy.data.objects["X5_CTRL"]
def t(label, fn):
    try: out[label] = fn()
    except Exception as e: out[label] = "ERR: %s" % e
t("keys_before", lambda: list(ctrl.keys()))
t("amber_before", lambda: round(ctrl["amber"],4))
SC.frame_set(1248)
t("keys_after_frameset", lambda: list(ctrl.keys()))
t("amber_after_frameset", lambda: round(ctrl["amber"],4))
t("xray_after_frameset", lambda: round(ctrl["xray"],4))
dg = bpy.context.evaluated_depsgraph_get()
t("eval_keys", lambda: list(ctrl.evaluated_get(dg).keys()))
t("eval_amber", lambda: round(ctrl.evaluated_get(dg)["amber"],4))
for mn in ("MAT_P05_Silicone_White","MAT_P05_Cartridge_Amber"):
    m=bpy.data.materials[mn]
    t(mn+"_V_AMBER_orig", lambda m=m: round(m.node_tree.nodes["V_AMBER"].outputs[0].default_value,4))
    t(mn+"_V_AMBER_eval", lambda m=m: round(m.evaluated_get(dg).node_tree.nodes["V_AMBER"].outputs[0].default_value,4))
    ad=m.node_tree.animation_data
    t(mn+"_driver_valid", lambda ad=ad: [[d.data_path, d.is_valid, d.driver.is_valid] for d in ad.drivers])
print(json.dumps(out, ensure_ascii=False, indent=1))
bpy.context.window.scene = prev
