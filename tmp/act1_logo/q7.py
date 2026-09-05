import bpy, json
from mathutils import Vector
src = bpy.data.collections["SRC_OPENING_NITE_PRODUCT_LINKED"]
def wm(o):
    m=o.matrix_basis.copy(); cur=o
    while cur.parent is not None:
        m = cur.parent.matrix_basis @ cur.matrix_parent_inverse @ m; cur=cur.parent
    return m
# control panel is on the +Y face near the logo (0.049,-0.087,0.323); panel sits lower in Z
res=[]
for o in src.all_objects:
    if o.type!='MESH': continue
    M=wm(o)
    if not len(o.data.vertices): continue
    c=[M @ Vector(v) for v in o.bound_box]
    cx=sum(p.x for p in c)/8; cy=sum(p.y for p in c)/8; cz=sum(p.z for p in c)/8
    mnz=min(p.z for p in c); mxz=max(p.z for p in c)
    mny=min(p.y for p in c)
    # near the front face, below the logo
    if mny < 0.15 and mxz < 0.30 and mnz > -0.35 and abs(cx-0.05) < 0.35:
        res.append({"n":o.name,"ctr":[round(cx,3),round(cy,3),round(cz,3)],
                    "z":[round(mnz,3),round(mxz,3)],"y":round(mny,3),
                    "verts":len(o.data.vertices),
                    "mats":[(s.material.name if s.material else None, s.link) for s in o.material_slots],
                    "colls":[c2.name for c2 in o.users_collection]})
res.sort(key=lambda r:-r["verts"])
print(json.dumps(res[:30], ensure_ascii=False, indent=1))
