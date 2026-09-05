import bpy, math
from mathutils import Vector
def wmat(o):
    m=o.matrix_basis.copy(); p=o.parent; c=o
    while p:
        m=p.matrix_basis @ c.matrix_parent_inverse @ m; c=p; p=p.parent
    return m
L=[]
for mn in ("Rubber #4","Rubber #5"):
    m=bpy.data.materials[mn]
    ig=[n.name for n in m.node_tree.nodes if "IGNITION" in n.name]
    ad = m.node_tree.animation_data
    L.append("MAT %s ignition_nodes=%s anim=%s users=%d" % (mn, ig, bool(ad and ad.action), m.users))
for nm in ("P07R_Male","P07R_Underwear"):
    o=bpy.data.objects.get(nm)
    L.append("%s exists=%s hide_render=%s hide_viewport=%s hide_get_err=- loc=%s dim=%s" % (nm, bool(o), o.hide_render if o else '-', o.hide_viewport if o else '-', tuple(round(v,3) for v in o.location) if o else '-', tuple(round(v,3) for v in o.dimensions) if o else '-'))
# angular spans of buckles/brackets
CU=(0.0589,-2.1837); CL=(0.0455,-2.3473)
for nm,C in (("59.002",CU),("60.002",CU),("63.002",CL),("64.005",CL),("58.002",CU)):
    o=bpy.data.objects[nm]; M=wmat(o)
    angs=[math.degrees(math.atan2((M@Vector(c)).y-C[1],(M@Vector(c)).x-C[0]))%360 for c in o.bound_box]
    L.append("%s bbox angles %.1f .. %.1f" % (nm, min(angs), max(angs)))
# longitudinal vertex spacing for 64.002 near back (270deg)
o=bpy.data.objects["64.002"]; M=wmat(o); me=o.data
n=len(me.vertices); co=[0.0]*(n*3); me.vertices.foreach_get("co",co)
import collections
angset=collections.defaultdict(int)
for i in range(n):
    v=M@Vector((co[3*i],co[3*i+1],co[3*i+2]))
    a=math.degrees(math.atan2(v.y-CU[1],v.x-CU[0]))%360
    if 268<=a<272: angset[round(a,3)]+=1
ks=sorted(angset)
gaps=[ks[i+1]-ks[i] for i in range(len(ks)-1)]
L.append("upper strap 268-272deg: distinct angles=%d maxgap=%.4f deg avg=%.4f (arc gap at r=0.69 -> %.4f units)" % (len(ks), max(gaps), sum(gaps)/len(gaps), max(gaps)*math.pi/180*0.69))
print("\n".join(L))
