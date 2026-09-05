import bpy, json
def kfs(ad):
    if not ad or not ad.action: return {}
    d={}
    for f in ad.action.fcurves:
        key = f.data_path + ("[%d]"%f.array_index if f.array_index else "")
        d[key]=[[round(k.co[0],1), round(k.co[1],4), k.interpolation] for k in f.keyframe_points]
    return d
out={}
for n in ["LGT_Opening_Logo_Accent","LGT_Opening_Silhouette_Rim_L","LGT_Opening_Silhouette_Rim_R","LGT_Opening_Silhouette_Top"]:
    o=bpy.data.objects[n]
    out[n]={"obj_act": o.animation_data.action.name if o.animation_data and o.animation_data.action else None,
            "obj_keys": kfs(o.animation_data),
            "data": {"type":o.data.type,"energy":o.data.energy,"color":[round(v,3) for v in o.data.color],
                     "size":getattr(o.data,'size',None),"size_y":getattr(o.data,'size_y',None),
                     "shape":getattr(o.data,'shape',None),"spread":getattr(o.data,'spread',None)},
            "data_act": o.data.animation_data.action.name if o.data.animation_data and o.data.animation_data.action else None,
            "data_keys": kfs(o.data.animation_data),
            "loc":[round(v,3) for v in o.location], "rot":[round(v,3) for v in o.rotation_euler],
            "colls":[c.name for c in o.users_collection]}
c=bpy.data.objects["CAM_Opening_Silhouette"]
out["CAM"]={"lens":c.data.lens,"keys":kfs(c.animation_data),"data_keys":kfs(c.data.animation_data),
            "constraints":[(k.type, getattr(k,'target',None).name if getattr(k,'target',None) else None) for k in c.constraints],
            "dof": (c.data.dof.use_dof, c.data.dof.focus_distance, c.data.dof.aperture_fstop, c.data.dof.focus_object.name if c.data.dof.focus_object else None)}
print(json.dumps(out, ensure_ascii=False, indent=1))
