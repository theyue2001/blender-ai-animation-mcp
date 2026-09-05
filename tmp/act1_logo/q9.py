import bpy, json
out={}
def dump(mn):
    m=bpy.data.materials.get(mn)
    if not m: return "MISSING"
    d={"users":m.users,"nodes":[],"anim":None}
    if m.node_tree:
        nt=m.node_tree
        if nt.animation_data and nt.animation_data.action:
            d["anim"]={"act":nt.animation_data.action.name,
                       "fc":[(f.data_path,f.array_index,[[round(k.co[0],1),round(k.co[1],4)] for k in f.keyframe_points]) for f in nt.animation_data.action.fcurves]}
        for n in nt.nodes:
            e={"n":n.name,"t":n.bl_idname}
            if n.bl_idname=="ShaderNodeBsdfPrincipled":
                for k in ["Base Color","Roughness","Metallic","Specular IOR Level","Coat Weight","Coat Roughness","Anisotropic"]:
                    if k in n.inputs:
                        v=n.inputs[k].default_value
                        e[k]=[round(x,4) for x in v] if hasattr(v,'__len__') else round(v,4)
                        if n.inputs[k].links: e[k+"_LINK"]=n.inputs[k].links[0].from_node.name
            if n.bl_idname in ("ShaderNodeMixRGB","ShaderNodeMix","ShaderNodeValue","ShaderNodeRGB"):
                try: e["val"]=[round(x,4) for x in n.outputs[0].default_value]
                except Exception: e["val"]=round(n.outputs[0].default_value,4)
            d["nodes"].append(e)
        d["links"]=[(l.from_node.name,l.from_socket.name,"->",l.to_node.name,l.to_socket.name) for l in nt.links]
    return d
out["BEZEL"]=dump("MAT_OPENING_Bezel_Satin_Controlled_v028")
out["BUTTONS"]=dump("SHOT1_CONTROL_49.002_0")
m=bpy.data.materials["SHOT1_CONTROL_49.002_0"]
out["btn_mat_meshes"]=[me.name for me in bpy.data.meshes if any(mm==m for mm in me.materials)]
out["btn_mat_objs"]=[(o.name,[c.name for c in o.users_collection]) for o in bpy.data.objects if o.type=='MESH' and any(s.material==m for s in o.material_slots)]
o34=bpy.data.objects["34.002"]
out["obj34"]={"colls":[c.name for c in o34.users_collection],"slots":[(s.link,s.material.name) for s in o34.material_slots],"mesh":(o34.data.name,o34.data.users)}
o49=bpy.data.objects["49.002"]
out["obj49"]={"colls":[c.name for c in o49.users_collection],"slots":[(s.link,s.material.name) for s in o49.material_slots],"mesh":(o49.data.name,o49.data.users)}
print(json.dumps(out, ensure_ascii=False, indent=1))
