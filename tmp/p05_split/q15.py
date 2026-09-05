import bpy, json
out={}
for nm in ("LGT_P05W_Key","LGT_P05W_Rim_R","LGT_P05W_Device","LGT_P05W_Fill","LGT_P05W_Skin_L"):
    d = bpy.data.objects[nm].data
    ad = d.animation_data
    if not (ad and ad.action):
        out[nm] = {"animated": False, "energy": d.energy}; continue
    fc = ad.action.fcurves.find("energy")
    out[nm] = {"keys": [[round(k.co[0]), round(k.co[1],1)] for k in fc.keyframe_points],
               "at": {f: round(fc.evaluate(f),1) for f in (1631,1640,1650,1660,1674,1700)}}
nt = bpy.data.materials["MAT_P05W_LED_Amber"].node_tree
fc = nt.animation_data.action.fcurves.find('nodes["EMIS"].inputs[1].default_value')
out["amber_at"] = {f: round(fc.evaluate(f),2) for f in (1631,1640,1660,1674,1772)}
worn = list(bpy.data.collections["P05_WORN_BODY"].objects)[0]
fcw = worn.animation_data.action.fcurves.find("hide_render")
out["hide_render_at"] = {f: round(fcw.evaluate(f),2) for f in (1500,1631,1632,1700)}
print(json.dumps(out, ensure_ascii=False, indent=1))
