import bpy, json
out={}
sc1 = bpy.data.scenes["01_SCN_OPENING_P01_P03"]
out["sc1_markers"] = [[m.frame, m.name, m.camera.name if m.camera else None] for m in sorted(sc1.timeline_markers, key=lambda m:m.frame)]
for mn in ["SHOT1_HUMAN_Male_0","SHOT1_HUMAN_Underwear_0","Rubber #4","Rubber #5","SHOT1_CONTROL_Disc #1.002_0"]:
    m = bpy.data.materials.get(mn)
    if not m: 
        out[mn]="MISSING"; continue
    nt = m.node_tree
    d = {"users": m.users, "nodes": len(nt.nodes)}
    ad = nt.animation_data
    if ad:
        if ad.action:
            d["action"]=ad.action.name
            d["fc"]=[[fc.data_path, fc.array_index, len(fc.keyframe_points),
                      round(fc.evaluate(300),4), round(fc.evaluate(430),4), round(fc.evaluate(1700),4)] for fc in ad.action.fcurves]
        d["drivers"]=[[dr.data_path, dr.array_index, dr.driver.expression] for dr in ad.drivers]
    out[mn]=d
# what MAT_P05 materials exist
out["MAT_P05"] = sorted([m.name for m in bpy.data.materials if m.name.startswith("MAT_P05")])
print(json.dumps(out, ensure_ascii=False, indent=1))
