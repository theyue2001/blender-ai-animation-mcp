import bpy, json
out={}
byname={}
for o in bpy.data.collections["P05_XRAY_INTERNAL"].objects:
    for s in o.material_slots:
        if s.material: byname.setdefault(s.material.name, []).append(o.name)
out["internal_mat_usage"]=byname
for mn in ("MAT_P05_Silicone_White","MAT_P05_Internal_Mid","MAT_P05_Internal_Dark","MAT_P05_Rear_Ring"):
    m=bpy.data.materials[mn]; nt=m.node_tree
    d={"nodes":[]}
    for n in nt.nodes:
        e={"name":n.name,"type":n.type}
        if n.type=='BSDF_PRINCIPLED':
            e["base"]=[round(v,4) for v in n.inputs["Base Color"].default_value]
            e["rough"]=round(n.inputs["Roughness"].default_value,3)
            e["trans"]=round(n.inputs["Transmission Weight"].default_value,3)
            e["emis_col"]=[round(v,3) for v in n.inputs["Emission Color"].default_value]
            e["emis_str"]=round(n.inputs["Emission Strength"].default_value,3)
        if n.type=='VALUE': e["val"]=round(n.outputs[0].default_value,4)
        if n.type=='EMISSION':
            e["col"]=[round(v,3) for v in n.inputs[0].default_value]; e["str"]=round(n.inputs[1].default_value,3)
        if n.type=='VALTORGB':
            e["ramp"]=[[round(el.position,3),[round(v,3) for v in el.color]] for el in n.color_ramp.elements]
        d["nodes"].append(e)
    d["links"]=[[l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name] for l in nt.links]
    ad=nt.animation_data
    d["drivers"]=[[dr.data_path, dr.driver.expression] for dr in ad.drivers] if ad else []
    out[mn]=d
print(json.dumps(out, ensure_ascii=False, indent=1))
