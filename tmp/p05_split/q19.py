import bpy, json
from mathutils import Vector
def wm(o):
    return o.matrix_basis.copy() if o.parent is None else wm(o.parent) @ o.matrix_parent_inverse @ o.matrix_basis
def bb(o):
    m=wm(o); p=[m@Vector(c) for c in o.bound_box]
    return [[round(min(q[i] for q in p),3) for i in range(3)],[round(max(q[i] for q in p),3) for i in range(3)]]
out={}
for n in ("X5_mesh.002","X5_25.002","X5_30_0_0.002","X5_30_0_1.002","X5_30_1.002",
          "X5_56.002","X5_62.002","X5_20.002","X5_48.002","X5_22.002","X5_23.002"):
    o=bpy.data.objects.get(n)
    if o: out[n]={"bb":bb(o),"mat":[s.material.name for s in o.material_slots],"polys":len(o.data.polygons)}
m=bpy.data.materials["MAT_P05_Silicone_White"]
out["silicone_users"]={"users":m.users,
   "objects":[o.name for o in bpy.data.objects for s in o.material_slots if s.material is m],
   "data_link":[o.name for o in bpy.data.objects for i,s in enumerate(o.material_slots) if s.material is m and s.link=='DATA']}
out["product_bb_Y"]=[-1.523,0.1]
print(json.dumps(out, ensure_ascii=False, indent=1))
