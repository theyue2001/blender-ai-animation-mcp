import bpy
m=bpy.data.materials["Rubber #4"]
for n in m.node_tree.nodes:
    if "IGNITION" in n.name or n.type in ('OUTPUT_MATERIAL','BSDF_PRINCIPLED'):
        ins=[]
        for i in n.inputs:
            src = i.links[0].from_node.name if i.links else None
            try: dv = tuple(round(x,3) for x in i.default_value) if hasattr(i.default_value,'__len__') else round(i.default_value,3)
            except: dv='-'
            ins.append("%s<-%s=%s" % (i.name, src, dv))
        print("NODE %s (%s) : %s" % (n.name, n.type, " | ".join(ins[:8])))
o=bpy.data.objects["P07R_Male"]
print("Male mats:", [(s.link, s.material.name if s.material else None) for s in o.material_slots], "polys", len(o.data.polygons))
print("Male in scenes:", [s.name for s in o.users_scene], "colls", [c.name for c in o.users_collection])
sc=bpy.data.scenes["05_SCN_P07_STRAP_RIG"]
def walk(lc, d=0):
    print("  "*d, lc.name, "exclude=",lc.exclude, "hide_viewport=",lc.hide_viewport, "coll.hide_render=",lc.collection.hide_render)
    for c in lc.children: walk(c,d+1)
walk(sc.view_layers[0].layer_collection)
