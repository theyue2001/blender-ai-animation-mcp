import bpy, json
out={}
# who else uses the meshes the amber cartridge objects sit on
for n in ("X5_25.002","X5_30_0_0.002","X5_30_0_1.002","X5_30_1.002","X5_mesh.002"):
    o=bpy.data.objects[n]; me=o.data
    sharers=[x.name for x in bpy.data.objects if x.data is me]
    out[n]={"mesh":me.name,"mesh_users":me.users,
            "slot_link":[s.link for s in o.material_slots],
            "slot_mat":[s.material.name if s.material else None for s in o.material_slots],
            "DATA_mat":[m.name if m else None for m in me.materials],
            "sharers":{x: [ (s.link, s.material.name if s.material else None) for s in bpy.data.objects[x].material_slots]
                       for x in sharers if x != n}}
out["amber_mat_users"]={m: [o.name for o in bpy.data.objects for s in o.material_slots if s.material and s.material.name==m]
                        for m in ("MAT_P05_Silicone_White","MAT_P05_Cartridge_Amber","MAT_P05_Internal_Mid")}
out["scene_bounces"]={s.name: s.cycles.transparent_max_bounces for s in bpy.data.scenes}
out["worn_cart_mat"]=[ (o.name, [s.material.name for s in o.material_slots]) for o in bpy.data.objects if o.name in ("WRN_25.002","WRN_mesh.002")]
out["is_dirty"]=bpy.data.is_dirty
print(json.dumps(out, ensure_ascii=False, indent=1))
