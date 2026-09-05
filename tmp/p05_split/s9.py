import bpy, json
nt = bpy.data.materials["MAT_P05W_Control_Plate"].node_tree
emi = [n for n in nt.nodes if n.type=='EMISSION'][0]
m3 = emi.inputs[1].links[0].from_node
m3.inputs[1].default_value = 1.4
bpy.ops.wm.save_mainfile()
print(json.dumps({"mult": m3.inputs[1].default_value}))
