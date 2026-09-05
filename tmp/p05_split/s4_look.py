import bpy, json
SC = bpy.data.scenes["03_SCN_P05_XRAY_MECHANISM"]
prev = bpy.context.window.scene; bpy.context.window.scene = SC
LIGHTS = {
 "LGT_P05W_Key":    (240.0, (1.00, 0.86, 0.74), 2.2),
 "LGT_P05W_Rim_R":  (380.0, (0.80, 0.87, 1.00), 1.6),
 "LGT_P05W_Device": ( 95.0, (0.92, 0.95, 1.00), 0.7),
 "LGT_P05W_Fill":   ( 18.0, (1.00, 0.74, 0.55), 2.6),
 "LGT_P05W_Skin_L": (110.0, (1.00, 0.70, 0.52), 1.8),
}
for nm,(en,col,size) in LIGHTS.items():
    o = bpy.data.objects[nm]; o.data.energy=en; o.data.color=col; o.data.size=size

def P(matname):
    return bpy.data.materials[matname].node_tree.nodes["Principled BSDF"]
uw = P("MAT_P05W_HUMAN_Underwear_0")
uw.inputs["Base Color"].default_value = (0.004,0.004,0.005,1.0)
uw.inputs["Roughness"].default_value = 0.85
uw.inputs["Specular IOR Level"].default_value = 0.15
uw.inputs["Sheen Weight"].default_value = 0.12
uw.inputs["Sheen Roughness"].default_value = 0.5
sk = P("MAT_P05W_HUMAN_Male_0")
sk.inputs["Roughness"].default_value = 0.62
sk.inputs["Specular IOR Level"].default_value = 0.35
sk.inputs["Subsurface Weight"].default_value = 0.10
sk.inputs["Subsurface Scale"].default_value = 0.06
bpy.ops.wm.save_mainfile()
out = {"lights": {k:[v[0]] for k,v in LIGHTS.items()},
       "uw": [round(x,4) for x in uw.inputs["Base Color"].default_value],
       "skin_rough": sk.inputs["Roughness"].default_value}
print(json.dumps(out))
bpy.context.window.scene = prev
