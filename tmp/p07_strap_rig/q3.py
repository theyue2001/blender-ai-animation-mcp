import bpy
from mathutils import Vector
def wmat(o):
    m = o.matrix_basis.copy(); p=o.parent; c=o
    while p:
        m = p.matrix_basis @ c.matrix_parent_inverse @ m
        c=p; p=p.parent
    return m
# region of interest: upper strap band
rois = {"UPPER_Z": (0.80,1.20), "LOWER_Z": (0.08,0.38)}
res=[]
for o in bpy.data.objects:
    if o.type!='MESH': continue
    if o.name.startswith(("EXP_","P08_","X5_","WRN_","P05_","P06_","P09_")): continue
    M=wmat(o)
    bb=[M @ Vector(c) for c in o.bound_box]
    zs=[v.z for v in bb]; xs=[v.x for v in bb]; ys=[v.y for v in bb]
    for k,(z0,z1) in rois.items():
        if max(zs)>z0 and min(zs)<z1 and max(xs)>-1.3 and min(xs)<1.3 and max(ys)>-3.4 and min(ys)<-1.3:
            res.append((k,o.name,o.data.name,len(o.data.vertices),round(min(xs),3),round(max(xs),3),round(min(ys),3),round(max(ys),3),round(min(zs),3),round(max(zs),3)))
res.sort()
for r in res: print(r)
print("TOTAL", len(res))
