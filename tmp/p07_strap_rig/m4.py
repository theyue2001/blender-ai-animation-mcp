import bpy, math
from mathutils import Vector
out=[]
def wmat(o):
    m=o.matrix_basis.copy(); p=o.parent; c=o
    while p: m=p.matrix_basis@c.matrix_parent_inverse@m; c=p; p=p.parent
    return m
o=bpy.data.objects["64.002"]; M=wmat(o); me=o.data
n=len(me.vertices); co=[0.0]*(n*3); me.vertices.foreach_get("co",co)
P=[M@Vector((co[3*i],co[3*i+1],co[3*i+2])) for i in range(n)]
# how many Y-layers at each x, sampled on the z mid-band, across the back-centre region
out.append("layer scan along X (z near band centre 1.000, tol 0.004):")
zc=1.000
band=[p for p in P if abs(p.z-zc)<0.004]
out.append("  band verts=%d"%len(band))
for xi in range(-50,56,2):
    x=xi/100.0
    col=sorted(p.y for p in band if abs(p.x-x)<0.006)
    if len(col)<2: continue
    grp=[[col[0]]]
    for y in col[1:]:
        if y-grp[-1][-1]>0.010: grp.append([y])
        else: grp[-1].append(y)
    out.append("  x=%+.2f  n=%-4d layers=%d  y=%s"%(x,len(col),len(grp),
               ["%.3f"%(sum(g)/len(g)) for g in grp]))
out.append("")
out.append("full-ring layer count by angle (z mid, every 5 deg):")
C=((min(p.x for p in P)+max(p.x for p in P))*.5,(min(p.y for p in P)+max(p.y for p in P))*.5)
import collections
bins=collections.defaultdict(list)
for p in band:
    a=math.degrees(math.atan2(p.y-C[1],p.x-C[0]))%360.0
    bins[int(a/5)].append(math.hypot(p.x-C[0],p.y-C[1]))
multi=[]
for b in sorted(bins):
    r=sorted(bins[b])
    if len(r)<2: continue
    g=[[r[0]]]
    for v in r[1:]:
        if v-g[-1][-1]>0.010: g.append([v])
        else: g[-1].append(v)
    if len(g)>1: multi.append("%d-%d deg: %d layers r=%s"%(b*5,b*5+5,len(g),["%.3f"%(sum(x)/len(x)) for x in g]))
out.append("  angles with >1 radial layer: %d"%len(multi))
for s in multi[:40]: out.append("   "+s)
print("\n".join(out))
