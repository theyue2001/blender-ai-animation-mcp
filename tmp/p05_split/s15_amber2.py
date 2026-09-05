import bpy, json
SC = bpy.data.scenes["03_SCN_P05_XRAY_MECHANISM"]
prev = bpy.context.window.scene; bpy.context.window.scene = SC
rep = {}

# ---------- sleeve: brighter, yellower, far more translucent ----------
nt = bpy.data.materials["MAT_P05_Silicone_White"].node_tree
sil = nt.nodes["SILICONE"]; milk = nt.nodes["MILK"]; ramp = nt.nodes["RAMP"]
sil.inputs["Base Color"].default_value = (0.550, 0.250, 0.060, 1.0)
sil.inputs["Roughness"].default_value  = 0.30
sil.inputs["Emission Color"].default_value = (1.0, 0.52, 0.16, 1.0)
milk.inputs["Color"].default_value = (0.95, 0.55, 0.20, 1.0)
els = sorted(ramp.color_ramp.elements, key=lambda e: e.position)
els[0].color = (0.15, 0.15, 0.15, 1.0)
els[-1].color = (0.55, 0.55, 0.55, 1.0)
rep["sleeve_ramp"] = [[round(e.position,2), round(e.color[0],2)] for e in els]

# ---------- cartridge: rebuild as translucent amber glass ----------
c = bpy.data.materials["MAT_P05_Cartridge_Amber"]
nt2 = c.node_tree
if nt2.animation_data:
    for d in list(nt2.animation_data.drivers):
        nt2.driver_remove(d.data_path, d.array_index)
nt2.nodes.clear()
o2 = nt2.nodes.new("ShaderNodeOutputMaterial"); o2.location=(620,0)
mix= nt2.nodes.new("ShaderNodeMixShader");      mix.location=(420,0);  mix.name="MIX_AMB"
tr = nt2.nodes.new("ShaderNodeBsdfTransparent");tr.location=(220,140); tr.name="AMB_CLEAR"
tr.inputs[0].default_value = (0.95, 0.58, 0.22, 1.0)
p2 = nt2.nodes.new("ShaderNodeBsdfPrincipled"); p2.location=(140,-160); p2.name="AMB_SURF"
p2.inputs["Base Color"].default_value = (0.620, 0.280, 0.070, 1.0)
p2.inputs["Roughness"].default_value  = 0.25
p2.inputs["Emission Color"].default_value = (1.0, 0.55, 0.18, 1.0)
lw = nt2.nodes.new("ShaderNodeLayerWeight");    lw.location=(-140,180); lw.name="LWA"
lw.inputs[0].default_value = 0.30
rp = nt2.nodes.new("ShaderNodeValToRGB");       rp.location=(40,180);  rp.name="RAMPA"
rp.color_ramp.elements[0].position = 0.0;  rp.color_ramp.elements[0].color=(0.18,0.18,0.18,1)
rp.color_ramp.elements[1].position = 0.72; rp.color_ramp.elements[1].color=(0.68,0.68,0.68,1)
v2 = nt2.nodes.new("ShaderNodeValue"); v2.name="V_EMIS"; v2.location=(-360,-320)
mu2= nt2.nodes.new("ShaderNodeMath");  mu2.name="MUL_EMIS"; mu2.location=(-180,-320)
mu2.operation='MULTIPLY'; mu2.inputs[1].default_value = 1.2
L=nt2.links
L.new(lw.outputs["Facing"], rp.inputs[0])
L.new(rp.outputs["Color"], mix.inputs[0])
L.new(tr.outputs[0], mix.inputs[1])
L.new(p2.outputs[0], mix.inputs[2])
L.new(mix.outputs[0], o2.inputs["Surface"])
L.new(v2.outputs[0], mu2.inputs[0])
L.new(mu2.outputs[0], p2.inputs["Emission Strength"])
dr = nt2.driver_add('nodes["V_EMIS"].outputs[0].default_value')
dr.driver.type='SCRIPTED'
var = dr.driver.variables.new(); var.name="c"; var.type='SINGLE_PROP'
var.targets[0].id = bpy.data.objects["X5_CTRL"]; var.targets[0].data_path = '["glow"]'
dr.driver.expression = "0.10+c*0.34"

# ---------- transparent bounce headroom ----------
rep["transparent_max_bounces_before"] = SC.cycles.transparent_max_bounces
if SC.cycles.transparent_max_bounces < 24:
    SC.cycles.transparent_max_bounces = 24
rep["transparent_max_bounces_after"] = SC.cycles.transparent_max_bounces
bpy.ops.wm.save_mainfile()
print(json.dumps(rep, ensure_ascii=False, indent=1))
bpy.context.window.scene = prev
