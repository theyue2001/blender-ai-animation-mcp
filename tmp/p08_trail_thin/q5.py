import bpy, json, math
from mathutils import Vector
sc=bpy.data.scenes["04_SCN_P08_SLEEVE_TUNNEL"]
out={"range":[sc.frame_start,sc.frame_end]}
# collections in this scene
def walk(c,d=0,acc=None):
    acc.append(("  "*d)+c.name+" ["+str(len(c.objects))+"]")
    for ch in c.children: walk(ch,d+1,acc)
acc=[]; walk(sc.collection,0,acc); out["tree"]=acc
# P08_SLV_* objects
slv=[o for o in bpy.data.objects if o.name.startswith("P08_SLV") or o.name.startswith("P08_CMP")]
out["slv"]=[]
for o in sorted(slv,key=lambda x:x.name):
    ad=o.animation_data
    out["slv"].append({"n":o.name,"type":o.type,"data":o.data.name if o.data else None,
        "loc":[round(v,3) for v in o.location],"rot":[round(math.degrees(v),2) for v in o.rotation_euler],
        "scale":[round(v,4) for v in o.scale],"parent":o.parent.name if o.parent else None,
        "hide_render":o.hide_render,"dims":[round(v,4) for v in o.dimensions],
        "mods":[(m.type,m.name) for m in o.modifiers],
        "mats":[(s.link, s.material.name if s.material else None) for s in o.material_slots],
        "action":(ad.action.name if ad and ad.action else None),
        "fc":sorted(set(f.data_path for f in ad.action.fcurves)) if (ad and ad.action) else None,
        "in_scene": any(o.name==x.name for x in sc.objects)})
# cameras in scene
out["cams"]=[]
for o in sc.objects:
    if o.type=='CAMERA':
        ad=o.animation_data
        out["cams"].append({"n":o.name,"loc":[round(v,3) for v in o.location],
            "rot":[round(math.degrees(v),2) for v in o.rotation_euler],"lens":o.data.lens,
            "action":(ad.action.name if ad and ad.action else None),
            "fc":sorted(set((f.data_path,f.array_index) for f in ad.action.fcurves)) if (ad and ad.action) else None,
            "frange":[round(v,1) for v in ad.action.frame_range] if (ad and ad.action) else None,
            "dfc": sorted(set(f.data_path for f in o.data.animation_data.action.fcurves)) if (o.data.animation_data and o.data.animation_data.action) else None})
print(json.dumps(out,indent=1,ensure_ascii=False))
