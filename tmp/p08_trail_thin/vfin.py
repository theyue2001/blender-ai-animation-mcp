import bpy, json, math
sc=bpy.data.scenes["04_SCN_P08_SLEEVE_TUNNEL"]
rep={"file":bpy.data.filepath.split("\\")[-1],"dirty":bpy.data.is_dirty}
# shot-2 rig integrity
for n in ["P08_RING_CTR","P08_PIV_A","P08_PIV_B","P08_PIV_C","P08_SLV_A","P08_SLV_B","P08_SLV_C",
          "P08_SLVTRAIL_A","P08_SLVDOT_A","LGT_P08_SLVFX_A","CAM_P08_02_Sleeves"]:
    o=bpy.data.objects.get(n)
    ad=o.animation_data if o else None
    rep.setdefault("rig",{})[n]={"parent":(o.parent.name if o and o.parent else None),
        "keys":sorted(set(f.data_path for f in ad.action.fcurves)) if (ad and ad.action) else None}
# nothing from shot 2 may be visible in the later shots
def vis(obj,f):
    ad=obj.animation_data
    if not (ad and ad.action): return not obj.hide_render
    for fc in ad.action.fcurves:
        if fc.data_path=="hide_render": return fc.evaluate(f)<0.5
    return not obj.hide_render
probe=[2543,2600,2670,2800,3050,3200]
for n in ["P08_SLV_A","P08_SLVDOT_A","P08_SLVTRAIL_A","P08_CMP_A","P08_TUN_A"]:
    o=bpy.data.objects.get(n)
    if o: rep.setdefault("visibility",{})[n]={str(f):vis(o,f) for f in probe}
# shot 5 untouched?
rep["cmp_A_loc"]=[round(v,3) for v in bpy.data.objects["P08_CMP_A"].location]
rep["transparent_bounces"]=sc.cycles.transparent_max_bounces
print(json.dumps(rep,indent=1))
