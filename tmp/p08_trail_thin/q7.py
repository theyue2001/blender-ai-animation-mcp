import bpy, json
sc=bpy.data.scenes["04_SCN_P08_SLEEVE_TUNNEL"]
out={}
out["use_nodes"]=sc.use_nodes
if sc.node_tree:
    out["comp"]=[(n.type,n.name,[ (i.name, (round(i.default_value,3) if isinstance(i.default_value,float) else None)) for i in n.inputs if hasattr(i,'default_value')]) for n in sc.node_tree.nodes]
out["view"]={"vt":sc.view_settings.view_transform,"look":sc.view_settings.look,"exp":round(sc.view_settings.exposure,3)}
def mat(nm):
    m=bpy.data.materials.get(nm)
    if not m: return "MISSING"
    d={"users":m.users,"nodes":[]}
    for n in m.node_tree.nodes:
        e={"type":n.type,"name":n.name}
        if n.type=='EMISSION':
            e["color"]=[round(v,3) for v in n.inputs['Color'].default_value]
            e["strength"]=round(n.inputs['Strength'].default_value,3)
        if n.type=='BSDF_PRINCIPLED':
            e["base"]=[round(v,3) for v in n.inputs['Base Color'].default_value]
            e["rough"]=round(n.inputs['Roughness'].default_value,3)
            e["metal"]=round(n.inputs['Metallic'].default_value,3)
            for k in ("Emission Color","Emission Strength","Transmission Weight","Alpha","Subsurface Weight"):
                if k in n.inputs:
                    v=n.inputs[k].default_value
                    e[k]=[round(x,3) for x in v] if hasattr(v,'__len__') else round(v,3)
        d["nodes"].append(e)
    ad=m.node_tree.animation_data
    d["keys"]=sorted(set(f.data_path for f in ad.action.fcurves)) if (ad and ad.action) else None
    return d
for nm in ["MAT_P08_FXDOT_BLUE","MAT_P08_FXDOT_PINK","MAT_P08_TRAIL_BLUE","MAT_P08_TRAIL_PINK",
           "MAT_P08_SLEEVE_A","MAT_P08_SLEEVE_B","MAT_P08_SLEEVE_C"]:
    out[nm]=mat(nm)
out["all_p08_mats"]=[m.name for m in bpy.data.materials if m.name.startswith("MAT_P08")]
out["fx_objs"]=[o.name for o in bpy.data.collections["P08_FX"].objects]
print(json.dumps(out,indent=1,ensure_ascii=False))
