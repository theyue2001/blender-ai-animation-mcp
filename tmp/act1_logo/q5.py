import bpy, json
out={}
sc = bpy.data.scenes["01_SCN_OPENING_P01_P03"]
out["fps"]=(sc.render.fps, sc.render.fps_base)
def mat_info(m):
    if not m: return None
    d={"name":m.name,"users":m.users,"use_nodes":m.use_nodes,"blend":m.blend_method,
       "anim": None,"nodes":[]}
    if m.node_tree:
        if m.node_tree.animation_data and m.node_tree.animation_data.action:
            a=m.node_tree.animation_data.action
            d["anim"]={"act":a.name,"fc":[(f.data_path,f.array_index,[[round(k.co[0],1),round(k.co[1],4)] for k in f.keyframe_points]) for f in a.fcurves]}
        for n in m.node_tree.nodes:
            e={"n":n.name,"t":n.bl_idname}
            if n.bl_idname=="ShaderNodeBsdfPrincipled":
                e["base"]=[round(v,4) for v in n.inputs["Base Color"].default_value]
                e["rough"]=round(n.inputs["Roughness"].default_value,3)
                e["metal"]=round(n.inputs["Metallic"].default_value,3)
                e["emis"]=[round(v,4) for v in n.inputs["Emission Color"].default_value]
                e["emis_s"]=round(n.inputs["Emission Strength"].default_value,4)
                if "Coat Weight" in n.inputs: e["coat"]=round(n.inputs["Coat Weight"].default_value,3)
            d["nodes"].append(e)
    return d
for mn in ["MAT_P04_FRONT_LOGO_REVEAL","SHOT1_NITE_LOGO_DECAL_NITE_R1_Logo_0","Paint Matte Black #2.001"]:
    out[mn]=mat_info(bpy.data.materials.get(mn))
o = bpy.data.objects["P04_DECAL_NITE_R1_Logo_Reveal"]
out["p04_obj"]={"matrix":[[round(v,5) for v in r] for r in o.matrix_basis],
                "act_fc":[(f.data_path,[[round(k.co[0],1),round(k.co[1],3),k.interpolation] for k in f.keyframe_points]) for f in o.animation_data.action.fcurves] if o.animation_data and o.animation_data.action else None,
                "slots":[(s.link, s.material.name if s.material else None) for s in o.material_slots]}
src = bpy.data.objects["DECAL_NITE_R1_Logo"]
out["src_obj"]={"matrix_basis":[[round(v,5) for v in r] for r in src.matrix_basis]}
print(json.dumps(out, ensure_ascii=False, indent=1))
