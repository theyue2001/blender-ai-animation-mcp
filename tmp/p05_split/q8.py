import bpy, json
out={}
m = bpy.data.materials["SHOT1_HUMAN_Male_0"]
nt=m.node_tree
out["male_nodes"]=[[n.name,n.type,[ (i.name, (list(i.default_value)[:4] if hasattr(i.default_value,'__len__') else round(i.default_value,4)) if hasattr(i,'default_value') else None, (i.links[0].from_node.name if i.links else None)) for i in n.inputs]] for n in nt.nodes]
out["male_links"]=[[l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name] for l in nt.links]
out["male_blend"]=[m.blend_method, m.use_backface_culling]
drv={}
for mn in [x.name for x in bpy.data.materials if x.name.startswith("MAT_P05")]:
    mm=bpy.data.materials[mn]; nt2=mm.node_tree
    ad=nt2.animation_data
    d={}
    if ad:
        d["drivers"]=[[dr.data_path, dr.array_index, dr.driver.expression,
                       [[v.name, v.targets[0].id.name if v.targets[0].id else None, v.targets[0].data_path] for v in dr.driver.variables]] for dr in ad.drivers]
        if ad.action: d["action"]=ad.action.name
    d["nodes"]=[n.name for n in nt2.nodes]
    drv[mn]=d
out["p05_mats"]=drv
print(json.dumps(out, ensure_ascii=False, indent=1)[:12000])
