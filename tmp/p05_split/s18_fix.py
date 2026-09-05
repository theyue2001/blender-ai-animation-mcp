import bpy, json
SC = bpy.data.scenes["03_SCN_P05_XRAY_MECHANISM"]
prev = bpy.context.window.scene; bpy.context.window.scene = SC
F0, F1 = 950, 1248
rep = {}
PATH = 'nodes["V_AMBER"].outputs[0].default_value'

for mn in ("MAT_P05_Silicone_White", "MAT_P05_Cartridge_Amber"):
    nt = bpy.data.materials[mn].node_tree
    ad = nt.animation_data
    # drop the dead driver
    if ad:
        for d in list(ad.drivers):
            if d.data_path == PATH:
                nt.driver_remove(d.data_path, d.array_index)
    if nt.animation_data is None: nt.animation_data_create()
    ad = nt.animation_data
    if ad.action is None:
        ad.action = bpy.data.actions.new("ACT_" + mn)
    fc = ad.action.fcurves.find(PATH)
    if fc: ad.action.fcurves.remove(fc)
    fc = ad.action.fcurves.new(PATH)
    for f, v in ((F0, 0.0), (F1, 1.0)):
        kp = fc.keyframe_points.insert(f, v)
        kp.interpolation = 'BEZIER'; kp.handle_left_type = kp.handle_right_type = 'AUTO_CLAMPED'
    fc.update()
    rep[mn] = {"action": ad.action.name,
               "keys": [[round(k.co[0]), round(k.co[1],2)] for k in fc.keyframe_points],
               "eval": {f: round(fc.evaluate(f),3) for f in (900, 950, 1050, 1150, 1248, 1440)},
               "drivers_left": [d.data_path for d in (ad.drivers or [])]}

# remove the dead custom property + its fcurve
ctrl = bpy.data.objects["X5_CTRL"]
a = ctrl.animation_data.action
fc = a.fcurves.find('["amber"]')
if fc: a.fcurves.remove(fc)
if "amber" in ctrl.keys(): del ctrl["amber"]
rep["ctrl_keys"] = list(ctrl.keys())
rep["ctrl_fcurves"] = [f.data_path for f in a.fcurves]
bpy.ops.wm.save_mainfile()
print(json.dumps(rep, ensure_ascii=False, indent=1))
bpy.context.window.scene = prev
