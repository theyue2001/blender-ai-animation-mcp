import bpy, json
SC = bpy.data.scenes["03_SCN_P05_XRAY_MECHANISM"]
prev = bpy.context.window.scene; bpy.context.window.scene = SC
F0, F1 = 950, 1248          # amber ramps in while the camera is still rotating
rep = {}

# ---------- 1. new control value on X5_CTRL ----------
ctrl = bpy.data.objects["X5_CTRL"]
if "amber" not in ctrl.keys():
    ctrl["amber"] = 0.0
ui = ctrl.id_properties_ui("amber"); ui.update(min=0.0, max=1.0, soft_min=0.0, soft_max=1.0)
act = ctrl.animation_data.action
fc = act.fcurves.find('["amber"]')
if fc: act.fcurves.remove(fc)
fc = act.fcurves.new('["amber"]')
for f, v in ((F0, 0.0), (F1, 1.0)):
    kp = fc.keyframe_points.insert(f, v)
    kp.interpolation = 'BEZIER'; kp.handle_left_type = kp.handle_right_type = 'AUTO_CLAMPED'
fc.update()
rep["amber_keys"] = [[F0, 0.0], [F1, 1.0]]

def amber_value_node(nt, loc):
    """Value node driven by X5_CTRL['amber']."""
    n = nt.nodes.get("V_AMBER")
    if n is None:
        n = nt.nodes.new("ShaderNodeValue"); n.name = "V_AMBER"; n.location = loc
    if nt.animation_data:
        for d in list(nt.animation_data.drivers):
            if d.data_path == 'nodes["V_AMBER"].outputs[0].default_value':
                nt.driver_remove(d.data_path, d.array_index)
    dr = nt.driver_add('nodes["V_AMBER"].outputs[0].default_value')
    dr.driver.type = 'SCRIPTED'
    v = dr.driver.variables.new(); v.name = "a"; v.type = 'SINGLE_PROP'
    v.targets[0].id = bpy.data.objects["X5_CTRL"]; v.targets[0].data_path = '["amber"]'
    dr.driver.expression = "a"
    return n

def mix(nt, name, dtype, loc):
    n = nt.nodes.get(name)
    if n is None:
        n = nt.nodes.new("ShaderNodeMix"); n.name = name; n.location = loc
    n.data_type = dtype
    fac = next(i for i in n.inputs if i.name == "Factor" and i.type == 'VALUE')
    tp = 'RGBA' if dtype == 'RGBA' else 'VALUE'   # socket type, not data_type
    ab = [i for i in n.inputs if i.name in ("A", "B") and i.type == tp]
    outp = next(o for o in n.outputs if o.type == tp)
    return n, fac, ab[0], ab[1], outp

# ---------- 2. sleeve: milky-white <-> translucent amber ----------
nt = bpy.data.materials["MAT_P05_Silicone_White"].node_tree
sil, milk, ramp = nt.nodes["SILICONE"], nt.nodes["MILK"], nt.nodes["RAMP"]
va = amber_value_node(nt, (-900, -420))
WHITE_BASE = (0.930, 0.935, 0.940, 1.0); AMB_BASE = (0.550, 0.364, 0.060, 1.0)
WHITE_MILK = (1.0, 1.0, 1.0, 1.0);       AMB_MILK = (0.950, 0.725, 0.200, 1.0)
WHITE_EMIS = (1.0, 1.0, 1.0, 1.0);       AMB_EMIS = (1.000, 0.716, 0.160, 1.0)
for nm, tgt, ca, cb, loc in (("MIX_BASE", sil.inputs["Base Color"],  WHITE_BASE, AMB_BASE, (-620, -120)),
                             ("MIX_MILKC", milk.inputs["Color"],     WHITE_MILK, AMB_MILK, (-620, 160)),
                             ("MIX_EMISC", sil.inputs["Emission Color"], WHITE_EMIS, AMB_EMIS, (-620, -320))):
    n, f, a, b, o = mix(nt, nm, 'RGBA', loc)
    a.default_value = ca; b.default_value = cb
    nt.links.new(va.outputs[0], f); nt.links.new(o, tgt)
# transparency ramp: opaque milky (0.50/0.95) -> translucent amber (0.15/0.55)
rm = nt.nodes.get("RAMP_MILKY")
if rm is None:
    rm = nt.nodes.new("ShaderNodeValToRGB"); rm.name = "RAMP_MILKY"; rm.location = (-620, 420)
    nt.links.new(nt.nodes["LW"].outputs["Facing"], rm.inputs[0])
e = sorted(rm.color_ramp.elements, key=lambda x: x.position)
e[0].position = 0.0; e[0].color = (0.50, 0.50, 0.50, 1.0)
e[-1].position = 0.7; e[-1].color = (0.95, 0.95, 0.95, 1.0)
n, f, a, b, o = mix(nt, "MIX_RAMP", 'RGBA', (-380, 420))
nt.links.new(rm.outputs["Color"], a); nt.links.new(ramp.outputs["Color"], b)
nt.links.new(va.outputs[0], f); nt.links.new(o, nt.nodes["MIX_SIL"].inputs[0])
# emission only once amber is in
me = nt.nodes.get("MUL_AMB")
if me is None:
    me = nt.nodes.new("ShaderNodeMath"); me.name = "MUL_AMB"; me.location = (-380, -520)
me.operation = 'MULTIPLY'
nt.links.new(nt.nodes["MUL_EMIS"].outputs[0], me.inputs[0])
nt.links.new(va.outputs[0], me.inputs[1])
nt.links.new(me.outputs[0], sil.inputs["Emission Strength"])

# ---------- 3. cartridge: opaque grey <-> translucent amber ----------
nt2 = bpy.data.materials["MAT_P05_Cartridge_Amber"].node_tree
p2, rpa, mixamb = nt2.nodes["AMB_SURF"], nt2.nodes["RAMPA"], nt2.nodes["MIX_AMB"]
va2 = amber_value_node(nt2, (-900, -520))
GREY_BASE = (0.245, 0.258, 0.285, 1.0); CART_BASE = (0.620, 0.408, 0.070, 1.0)
n, f, a, b, o = mix(nt2, "MIX_BASE2", 'RGBA', (-360, -60))
a.default_value = GREY_BASE; b.default_value = CART_BASE
nt2.links.new(va2.outputs[0], f); nt2.links.new(o, p2.inputs["Base Color"])
# Fac: 1.0 (fully opaque surface) -> facing ramp
n, f, a, b, o = mix(nt2, "MIX_FAC2", 'FLOAT', (240, 260))
a.default_value = 1.0
nt2.links.new(rpa.outputs["Color"], b)
nt2.links.new(va2.outputs[0], f); nt2.links.new(o, mixamb.inputs[0])
me2 = nt2.nodes.get("MUL_AMB")
if me2 is None:
    me2 = nt2.nodes.new("ShaderNodeMath"); me2.name = "MUL_AMB"; me2.location = (-20, -320)
me2.operation = 'MULTIPLY'
nt2.links.new(nt2.nodes["MUL_EMIS"].outputs[0], me2.inputs[0])
nt2.links.new(va2.outputs[0], me2.inputs[1])
nt2.links.new(me2.outputs[0], p2.inputs["Emission Strength"])

bpy.ops.wm.save_mainfile()
rep["ctrl_props"] = {k: round(ctrl[k],3) for k in ctrl.keys() if not k.startswith("_")}
rep["sleeve_nodes"] = [x.name for x in nt.nodes]
rep["cart_nodes"] = [x.name for x in nt2.nodes]
print(json.dumps(rep, ensure_ascii=False, indent=1))
bpy.context.window.scene = prev
