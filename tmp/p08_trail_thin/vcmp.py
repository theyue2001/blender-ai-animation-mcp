import bpy, json, math
rep={}
for k in "ABC":
    o=bpy.data.objects["P08_CMP_%s"%k]
    ad=o.animation_data
    if not (ad and ad.action):
        rep["P08_CMP_%s"%k]={"action":None,"static_loc":[round(v,3) for v in o.location]}
        continue
    ev={}
    for f in (3000,3058,3094):
        loc=[0,0,0]; rot=[0,0,0]
        for fc in ad.action.fcurves:
            if fc.data_path=="location": loc[fc.array_index]=round(fc.evaluate(f),3)
            if fc.data_path=="rotation_euler": rot[fc.array_index]=round(math.degrees(fc.evaluate(f)),2)
        ev[str(f)]={"loc":loc,"rot":rot}
    rep["P08_CMP_%s"%k]={"action":ad.action.name,
        "paths":sorted(set(f.data_path for f in ad.action.fcurves)),
        "eval":ev,"static_loc":[round(v,3) for v in o.location]}
# cut-plane driver value
for k in "ABC":
    m=bpy.data.materials.get("MAT_P08_CMPSEC_%s"%k)
    if not m: rep["MAT_P08_CMPSEC_%s"%k]="MISSING"; continue
    nt=m.node_tree; ad=nt.animation_data
    cv={}
    if ad and ad.action:
        for fc in ad.action.fcurves:
            cv[fc.data_path]={str(f):round(fc.evaluate(f),3) for f in (3000,3026,3058,3094)}
    rep["MAT_P08_CMPSEC_%s"%k]={"has_CUT_VAL":"CUT_VAL" in nt.nodes,"keys":cv}
    rep["slots_%s"%k]=[(s.link,s.material.name if s.material else None) for s in bpy.data.objects["P08_CMP_%s"%k].material_slots]
print(json.dumps(rep,indent=1))
