import bpy, json
from mathutils import Matrix
sc = bpy.data.scenes["01_SCN_OPENING_P01_P03"]
out={}
out["objs"]=[]
for o in sc.objects:
    ad = o.animation_data
    fc = sorted({int(k.co[0]) for f in (ad.action.fcurves if ad and ad.action else []) for k in f.keyframe_points}) if ad and ad.action else []
    out["objs"].append({"n":o.name,"t":o.type,"inst":o.instance_collection.name if o.instance_collection else None,
                        "loc":[round(v,3) for v in o.location],"hide_r":o.hide_render,
                        "act": ad.action.name if ad and ad.action else None,
                        "keys": fc[:40], "nkeys": len(fc)})
# recursive collection walk
def walk(c, depth=0, acc=None):
    acc.append(("  "*depth)+c.name+"  objs=%d"%len(c.objects))
    for ch in c.children: walk(ch, depth+1, acc)
acc=[]
walk(sc.collection,0,acc)
out["tree"]=acc
print(json.dumps(out, ensure_ascii=False, indent=1))
