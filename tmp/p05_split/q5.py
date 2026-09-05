import bpy, json
out = {}
def matinfo(o):
    r=[]
    for s in o.material_slots:
        m=s.material
        r.append([s.link, m.name if m else None, bool(m and m.node_tree and m.node_tree.animation_data and m.node_tree.animation_data.action)])
    return r
for cn in ["P05_XRAY_SHELL","P05_XRAY_INTERNAL"]:
    c = bpy.data.collections.get(cn)
    out[cn] = [[o.name, o.data.name, len(o.data.polygons), matinfo(o)] for o in c.objects] if cn=="P05_XRAY_SHELL" else [o.name for o in c.objects]
src = bpy.data.collections.get("SRC_OPENING_NITE_PRODUCT_LINKED")
out["src_opening_product_n"] = len(src.objects)
out["src_opening_product"] = [o.name for o in src.objects]
for n in ["Male","Underwear","P01_STRAP_UPPER","P01_STRAP_LOWER"]:
    o = bpy.data.objects.get(n)
    if o:
        out["mat_"+n] = matinfo(o)
        out["colls_"+n] = [c.name for c in o.users_collection]
        out["anim_"+n] = bool(o.animation_data and o.animation_data.action)
print(json.dumps(out, ensure_ascii=False, indent=1))
