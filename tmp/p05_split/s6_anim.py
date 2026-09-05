import bpy, json
SC = bpy.data.scenes["03_SCN_P05_XRAY_MECHANISM"]
prev = bpy.context.window.scene; bpy.context.window.scene = SC
log = {}

REVEAL_IN, REVEAL_FULL = 1632, 1674
SHIFT_A, SHIFT_B = 1620, 1662
PRESS = [1686, 1722, 1758]

def key(id_data, path, index, frames_vals, interp='BEZIER'):
    if id_data.animation_data is None: id_data.animation_data_create()
    ad = id_data.animation_data
    if ad.action is None:
        ad.action = bpy.data.actions.new("ACT_P05W_" + id_data.name[:40])
    act = ad.action
    fc = act.fcurves.find(path, index=index) if index >= 0 else act.fcurves.find(path)
    if fc: act.fcurves.remove(fc)
    fc = act.fcurves.new(path, index=max(index,0))
    for f, v in frames_vals:
        kp = fc.keyframe_points.insert(f, v)
        kp.interpolation = interp
        if interp == 'BEZIER': kp.handle_left_type = kp.handle_right_type = 'AUTO_CLAMPED'
    fc.update()
    return fc

# ---- 1. camera lens shift ----
cam = SC.camera
key(cam.data, "shift_x", -1, [(SHIFT_A, 0.0), (SHIFT_B, -0.23)])
log["shift"] = [SHIFT_A, SHIFT_B]

# ---- 2. worn set hidden before the reveal ----
worn = list(bpy.data.collections["P05_WORN_PRODUCT"].objects) + \
       list(bpy.data.collections["P05_WORN_BODY"].objects)
for o in worn:
    key(o, "hide_render", -1, [(1080, 1.0), (REVEAL_IN-1, 1.0), (REVEAL_IN, 0.0)], 'CONSTANT')
    key(o, "hide_viewport", -1, [(1080, 1.0), (REVEAL_IN-1, 1.0), (REVEAL_IN, 0.0)], 'CONSTANT')
log["hidden_until"] = REVEAL_IN
log["n_worn"] = len(worn)

# ---- 3. worn lights fade up ----
for nm in ("LGT_P05W_Key","LGT_P05W_Rim_R","LGT_P05W_Device","LGT_P05W_Fill","LGT_P05W_Skin_L"):
    o = bpy.data.objects[nm]
    key(o.data, "energy", -1, [(REVEAL_IN, 0.0), (REVEAL_FULL, o.data.energy)])

# ---- 4. LED discs: fade up, then step brighter on every press ----
def led(matname, base, steps):
    nt = bpy.data.materials[matname].node_tree
    seq = [(REVEAL_IN, 0.0), (REVEAL_FULL, base)]
    for i, f in enumerate(PRESS):
        seq += [(f+2, seq[-1][1]), (f+14, steps[i])]
    key(nt, 'nodes["EMIS"].inputs[1].default_value', -1, seq)
    return seq
log["amber"] = led("MAT_P05W_LED_Amber", 2.0, [3.4, 4.8, 6.6])
log["green"] = led("MAT_P05W_LED_Green", 2.4, [2.6, 2.8, 3.0])

# ---- 5. speed-up key glow on the control plate ----
KX, KY, KZ = -16.41, -60.70, -174.0     # "+" key centre, mesh-local (screen-right of the disc)
m = bpy.data.materials["MAT_P05W_Control_Plate"]
nt = m.node_tree
if "KEY_UP" not in nt.nodes:
    bsdf = nt.nodes["Principled BSDF"]; outn = nt.nodes["Material Output"]
    tc  = nt.nodes.new("ShaderNodeTexCoord");    tc.location=(-1100,-300); tc.object = bpy.data.objects["WRN_49.002"]
    sep = nt.nodes.new("ShaderNodeSeparateXYZ"); sep.location=(-900,-300); sep.name="SEP"
    comb= nt.nodes.new("ShaderNodeCombineXYZ");  comb.location=(-720,-300)
    sub = nt.nodes.new("ShaderNodeVectorMath");  sub.location=(-560,-300); sub.operation='SUBTRACT'
    sub.inputs[1].default_value=(KX, KY, 0.0)
    ln  = nt.nodes.new("ShaderNodeVectorMath");  ln.location=(-400,-300);  ln.operation='LENGTH'
    rad = nt.nodes.new("ShaderNodeMapRange");    rad.location=(-240,-300); rad.name="RAD"
    rad.inputs[1].default_value=6.8; rad.inputs[2].default_value=9.6
    rad.inputs[3].default_value=1.0; rad.inputs[4].default_value=0.0
    rad.clamp=True; rad.interpolation_type='SMOOTHSTEP'
    zg  = nt.nodes.new("ShaderNodeMapRange");    zg.location=(-240,-520); zg.name="ZGATE"
    zg.inputs[1].default_value=-173.6; zg.inputs[2].default_value=-173.0
    zg.inputs[3].default_value=1.0; zg.inputs[4].default_value=0.0; zg.clamp=True
    val = nt.nodes.new("ShaderNodeValue");       val.location=(-240,-700); val.name="KEY_UP"
    val.outputs[0].default_value = 0.0
    m1  = nt.nodes.new("ShaderNodeMath");        m1.location=(-60,-380);  m1.operation='MULTIPLY'
    m2  = nt.nodes.new("ShaderNodeMath");        m2.location=(100,-380);  m2.operation='MULTIPLY'
    m3  = nt.nodes.new("ShaderNodeMath");        m3.location=(260,-380);  m3.operation='MULTIPLY'; m3.inputs[1].default_value=16.0
    emi = nt.nodes.new("ShaderNodeEmission");    emi.location=(420,-380)
    emi.inputs[0].default_value=(0.80,0.92,1.0,1.0)
    add = nt.nodes.new("ShaderNodeAddShader");   add.location=(600,-100)
    L=nt.links
    L.new(tc.outputs["Object"], sep.inputs[0])
    L.new(sep.outputs["X"], comb.inputs[0]); L.new(sep.outputs["Y"], comb.inputs[1])
    L.new(comb.outputs[0], sub.inputs[0]); L.new(sub.outputs[0], ln.inputs[0])
    L.new(ln.outputs["Value"], rad.inputs[0]); L.new(sep.outputs["Z"], zg.inputs[0])
    L.new(rad.outputs[0], m1.inputs[0]); L.new(zg.outputs[0], m1.inputs[1])
    L.new(m1.outputs[0], m2.inputs[0]); L.new(val.outputs[0], m2.inputs[1])
    L.new(m2.outputs[0], m3.inputs[0]); L.new(m3.outputs[0], emi.inputs[1])
    L.new(bsdf.outputs[0], add.inputs[0]); L.new(emi.outputs[0], add.inputs[1])
    L.new(add.outputs[0], outn.inputs["Surface"])
seq = [(REVEAL_IN, 0.0)]
for f in PRESS:
    seq += [(f-4, 0.0), (f, 1.0), (f+6, 0.85), (f+16, 0.0)]
key(nt, 'nodes["KEY_UP"].outputs[0].default_value', -1, seq)
log["press"] = PRESS

bpy.ops.wm.save_mainfile()
print(json.dumps(log, ensure_ascii=False, indent=1))
bpy.context.window.scene = prev
