import bpy, json
v={}
o=bpy.data.objects["49.002"]
m=bpy.data.materials["MAT_P01_CONTROL_BUTTONS"]
src=bpy.data.materials["SHOT1_CONTROL_49.002_0"]
v["49.002"]={"slot":(o.material_slots[0].link,o.material_slots[0].material.name),
             "colls":[c.name for c in o.users_collection],
             "scenes":[s.name for s in bpy.data.scenes if o.name in s.objects]}
v["new_mat_users"]=m.users
v["orig_mat_base"]=[round(x,4) for x in src.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value]
v["orig_mat_rough"]=round(src.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value,4)
v["orig_mat_anim"]= src.node_tree.animation_data.action.name if src.node_tree.animation_data and src.node_tree.animation_data.action else None
v["orig_mat_used_by_objs"]=[ob.name for ob in bpy.data.objects if ob.type=='MESH' and any(s.material==src for s in ob.material_slots)]
# the P04 / P08 button objects must still point at their own materials
for n in ["EXP_49.002","EXP_49_PowerButton","EXP_49_PowerCap","EXP_49_PowerGlyph","P08_ASM_49.002"]:
    ob=bpy.data.objects.get(n)
    if ob: v[n]={"slots":[(s.link, s.material.name if s.material else None) for s in ob.material_slots],
                 "scenes":[s.name for s in bpy.data.scenes if ob.name in s.objects]}
# scene-01 additions recap
v["p01_additions"]=[x for x in ["P01_DECAL_NITE_R1_Logo_Reveal","LGT_Opening_Logo_Highlight"] if x in bpy.data.objects]
bpy.ops.wm.save_mainfile()
v["saved"]=True
print(json.dumps(v, ensure_ascii=False, indent=1))
