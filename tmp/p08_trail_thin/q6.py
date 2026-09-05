import bpy, json, math
sc=bpy.data.scenes["04_SCN_P08_SLEEVE_TUNNEL"]
def dump_act(o):
    ad=o.animation_data
    if not (ad and ad.action): return None
    d={}
    for f in ad.action.fcurves:
        k="%s[%d]"%(f.data_path,f.array_index)
        d[k]=[[round(kp.co[0],1), round(math.degrees(kp.co[1]),2) if "rotation" in f.data_path else round(kp.co[1],4), kp.interpolation[:4]] for kp in f.keyframe_points]
    return d
out={}
for n in ["P08_PIV_A","P08_PIV_B","P08_PIV_C","P08_SLV_A","P08_SLV_B","P08_SLV_C",
          "P08_CMP_A","P08_CMP_B","P08_CMP_C","CAM_P08_02_Sleeves","CAM_P08_05_Compare"]:
    o=bpy.data.objects.get(n)
    if not o: out[n]="MISSING"; continue
    e={"loc":[round(v,3) for v in o.location],"rot":[round(math.degrees(v),2) for v in o.rotation_euler],
       "rot_mode":o.rotation_mode,"parent":o.parent.name if o.parent else None,
       "keys":dump_act(o)}
    if o.type=='CAMERA':
        dad=o.data.animation_data
        e["data_keys"]={f.data_path:[[round(k.co[0],1),round(k.co[1],3),k.interpolation[:4]] for k in f.keyframe_points] for f in dad.action.fcurves} if (dad and dad.action) else None
        e["dof"]={"use":o.data.dof.use_dof,"fstop":o.data.dof.aperture_fstop,"fd":round(o.data.dof.focus_distance,3)}
    out[n]=e
# lights in scene near shot2 / shot5
out["lights"]=[]
for o in sc.objects:
    if o.type=='LIGHT' and 400<o.matrix_world.translation.y<700:
        out["lights"].append({"n":o.name,"t":o.data.type,"E":round(o.data.energy,2),
            "loc":[round(v,2) for v in o.matrix_world.translation],
            "keys":dump_act(o)})
print(json.dumps(out,indent=1,ensure_ascii=False))
