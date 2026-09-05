import bpy, json
SC = bpy.data.scenes["03_SCN_P05_XRAY_MECHANISM"]
prev = bpy.context.window.scene; bpy.context.window.scene = SC
rep = {}

# ---------- 1. sleeve -> translucent amber ----------
m = bpy.data.materials["MAT_P05_Silicone_White"]
assert m.users == 1
nt = m.node_tree
sil = nt.nodes["SILICONE"]; milk = nt.nodes["MILK"]; vem = nt.nodes["V_EMIS"]
sil.inputs["Base Color"].default_value  = (0.300, 0.105, 0.030, 1.0)
sil.inputs["Roughness"].default_value   = 0.33
sil.inputs["Emission Color"].default_value = (1.0, 0.42, 0.12, 1.0)
milk.inputs["Color"].default_value      = (0.80, 0.42, 0.16, 1.0)
if "MUL_EMIS" not in nt.nodes:
    mul = nt.nodes.new("ShaderNodeMath"); mul.name = "MUL_EMIS"
    mul.location = (vem.location[0]+180, vem.location[1]-60)
    mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = 1.6
    nt.links.new(vem.outputs[0], mul.inputs[0])
    nt.links.new(mul.outputs[0], sil.inputs["Emission Strength"])
rep["sleeve"] = {"base":[round(v,3) for v in sil.inputs["Base Color"].default_value],
                 "milk":[round(v,3) for v in milk.inputs["Color"].default_value],
                 "V_EMIS_now": round(vem.outputs[0].default_value,4)}

# ---------- 2. new amber cartridge material for the reciprocating barrel ----------
CART = "MAT_P05_Cartridge_Amber"
c = bpy.data.materials.get(CART)
if c is None:
    c = bpy.data.materials.new(CART)
c.use_nodes = True
nt2 = c.node_tree; nt2.nodes.clear()
out2 = nt2.nodes.new("ShaderNodeOutputMaterial"); out2.location=(400,0)
p2   = nt2.nodes.new("ShaderNodeBsdfPrincipled"); p2.location=(60,0)
p2.inputs["Base Color"].default_value = (0.460, 0.175, 0.050, 1.0)
p2.inputs["Roughness"].default_value  = 0.28
p2.inputs["Emission Color"].default_value = (1.0, 0.45, 0.14, 1.0)
v2 = nt2.nodes.new("ShaderNodeValue"); v2.name="V_EMIS"; v2.location=(-360,-220)
mu2= nt2.nodes.new("ShaderNodeMath");  mu2.name="MUL_EMIS"; mu2.location=(-180,-220)
mu2.operation='MULTIPLY'; mu2.inputs[1].default_value = 0.9
nt2.links.new(v2.outputs[0], mu2.inputs[0])
nt2.links.new(mu2.outputs[0], p2.inputs["Emission Strength"])
nt2.links.new(p2.outputs[0], out2.inputs["Surface"])
# same glow driver as the rest of the P05 set
for d in list(nt2.animation_data.drivers) if nt2.animation_data else []:
    nt2.driver_remove(d.data_path, d.array_index)
dr = nt2.driver_add('nodes["V_EMIS"].outputs[0].default_value')
dr.driver.type = 'SCRIPTED'
var = dr.driver.variables.new(); var.name = "c"; var.type = 'SINGLE_PROP'
var.targets[0].id = bpy.data.objects["X5_CTRL"]; var.targets[0].data_path = '["glow"]'
dr.driver.expression = "0.10+c*0.34"

CART_OBJS = ["X5_25.002", "X5_30_0_0.002", "X5_30_0_1.002", "X5_30_1.002"]
for n in CART_OBJS:
    o = bpy.data.objects[n]
    o.material_slots[0].link = 'OBJECT'
    o.material_slots[0].material = c
rep["cartridge_objs"] = CART_OBJS
rep["internal_mid_still_used_by"] = [o.name for o in bpy.data.objects
                                     for s in o.material_slots
                                     if s.material and s.material.name == "MAT_P05_Internal_Mid"]
bpy.ops.wm.save_mainfile()
print(json.dumps(rep, ensure_ascii=False, indent=1))
bpy.context.window.scene = prev
