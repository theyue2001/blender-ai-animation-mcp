import bpy, json
from mathutils import Vector
out={}
def wbb(o):
    m=o.matrix_basis if o.parent is None else None
    # copies are parented to root at identity, so world = root_basis @ basis; root is identity now
    mw = o.matrix_world if o.parent is None else (o.parent.matrix_basis @ o.matrix_parent_inverse @ o.matrix_basis)
    pts=[mw @ Vector(c) for c in o.bound_box]
    return [[round(min(p[i] for p in pts),3) for i in range(3)],[round(max(p[i] for p in pts),3) for i in range(3)]]
for n in ["Male","Underwear","P01_STRAP_UPPER","P01_STRAP_LOWER"]:
    o=bpy.data.objects[n]
    out[n]={"loc":[round(v,4) for v in o.location],"scale":[round(v,4) for v in o.scale],
            "rot":[round(v,4) for v in o.rotation_euler],"bb":wbb(o)}
for n in ["WRN_Male","WRN_Underwear","WRN_STRAP_UPPER","WRN_16_0.002","WRN_49.002","WRN_Disc.002","WRN_mesh.002","WRN_20.002"]:
    o=bpy.data.objects.get(n)
    if o: out[n]={"parent":o.parent.name if o.parent else None, "bb":wbb(o)}
# whole worn product bbox and whole X-ray product bbox
def group_bb(objs):
    mn=[1e9]*3; mx=[-1e9]*3
    for o in objs:
        if o.type!='MESH': continue
        b=wbb(o)
        for i in range(3):
            mn[i]=min(mn[i],b[0][i]); mx[i]=max(mx[i],b[1][i])
    return [[round(v,3) for v in mn],[round(v,3) for v in mx]]
out["WORN_PRODUCT_bb"]=group_bb(bpy.data.collections["P05_WORN_PRODUCT"].objects)
out["WORN_BODY_bb"]=group_bb(bpy.data.collections["P05_WORN_BODY"].objects)
xr=[o for o in bpy.data.collections["P05_XRAY_SHELL"].objects]+[o for o in bpy.data.collections["P05_XRAY_INTERNAL"].objects]
out["XRAY_bb"]=group_bb(xr)
print(json.dumps(out, ensure_ascii=False, indent=1))
