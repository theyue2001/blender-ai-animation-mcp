import bpy, math
from mathutils import Vector
o=bpy.data.objects["P07_STRAP_UPPER"]; me=o.data; W=o.matrix_world
nb=sum(1 for e in me.edges if e.is_loose)
# boundary edges = edges used by exactly 1 face
cnt={}
for p in me.polygons:
    for ek in p.edge_keys:
        cnt[ek]=cnt.get(ek,0)+1
bnd=[k for k,v in cnt.items() if v==1]
print("boundary edges:", len(bnd))
C=(0.0589,-2.1837)
angs=[]
for ek in bnd:
    for vi in ek:
        v=W @ me.vertices[vi].co
        angs.append(math.degrees(math.atan2(v.y-C[1], v.x-C[0]))%360)
if angs:
    import collections
    h=collections.Counter(int(a//5)*5 for a in angs)
    print("boundary edge angle histogram (5deg bins):", sorted(h.items())[:20])
# connectivity: can we walk from 200deg to 20deg?
import array
buf=[0]*(len(me.edges)*2); me.edges.foreach_get("vertices",buf)
n=len(me.vertices); par=list(range(n))
def find(a):
    while par[a]!=a: par[a]=par[par[a]]; a=par[a]
    return a
for i in range(0,len(buf),2):
    a=find(buf[i]); b=find(buf[i+1])
    if a!=b: par[a]=b
from collections import defaultdict
comp=defaultdict(list)
for i in range(n): comp[find(i)].append(i)
items=sorted(comp.items(), key=lambda kv:-len(kv[1]))
print("components:", len(comp))
for k,idx in items[:6]:
    aa=[]
    for i in idx:
        v=W @ me.vertices[i].co
        aa.append(math.degrees(math.atan2(v.y-C[1],v.x-C[0]))%360)
    aa.sort()
    gaps=[(aa[j+1]-aa[j],aa[j]) for j in range(len(aa)-1)]
    g=max(gaps) if gaps else (0,0)
    # gap measured relative to cut at 112
    sh=sorted(((a-112.0)%360) for a in aa)
    print("  n=%6d ang %.1f..%.1f  shifted(s from 112) %.2f..%.2f" % (len(idx),aa[0],aa[-1],sh[0],sh[-1]))
