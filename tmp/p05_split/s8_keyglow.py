import bpy, json
nt = bpy.data.materials["MAT_P05W_Control_Plate"].node_tree
N = nt.nodes; L = nt.links
# locate the final multiply feeding the Emission strength
emi = [n for n in N if n.type=='EMISSION'][0]
m3  = emi.inputs[1].links[0].from_node
m2  = m3.inputs[0].links[0].from_node
if "FACE_MOD" not in N:
    lw = N.new("ShaderNodeLayerWeight"); lw.location=(100,-620); lw.name="LWK"
    lw.inputs[0].default_value = 0.35
    pw = N.new("ShaderNodeMath"); pw.location=(260,-620); pw.name="FACE_POW"
    pw.operation='POWER'; pw.inputs[1].default_value=1.4
    fm = N.new("ShaderNodeMath"); fm.location=(420,-500); fm.name="FACE_MOD"
    fm.operation='MULTIPLY'
    L.new(lw.outputs["Facing"], pw.inputs[0])
    L.new(m2.outputs[0], fm.inputs[0])
    L.new(pw.outputs[0], fm.inputs[1])
    L.new(fm.outputs[0], m3.inputs[0])
m3.inputs[1].default_value = 0.9
emi.inputs[0].default_value = (0.72, 0.86, 1.0, 1.0)
bpy.ops.wm.save_mainfile()
print(json.dumps({"mult": m3.inputs[1].default_value, "chain":[m2.name,"FACE_MOD",m3.name]}))
