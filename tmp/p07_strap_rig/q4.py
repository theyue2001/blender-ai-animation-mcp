import bpy, math
from mathutils import Vector
def wmat(o):
    m=o.matrix_basis.copy(); p=o.parent; c=o
    while p:
        m=p.matrix_basis @ c.matrix_parent_inverse @ m; c=p; p=p.parent
    return m
out=[]
for name in ("64.002","65.002"):
    o=bpy.data.objects[name]; M=wmat(o); me=o.data
    n=len(me.vertices)
    par=list(range(n))
    def find(a):
        while par[a]!=a:
            par[a]=par[par[a]]; a=par[a]
        return a
    ek=me.edges.foreach_get
    import array
    ev=array.array('i',[0])*0
    buf=[0]*(len(me.edges)*2)
    me.edges.foreach_get("vertices", buf)
    for i in range(0,len(buf),2):
        a=find(buf[i]); b=find(buf[i+1])
        if a!=b: par[a]=b
    from collections import defaultdict
    comp=defaultdict(list)
    for i in range(n): comp[find(i)].append(i)
    co=[0.0]*(n*3); me.vertices.foreach_get("co", co)
    out.append("=== %s  verts=%d components=%d ===" % (name,n,len(comp)))
    items=sorted(comp.items(), key=lambda kv:-len(kv[1]))
    # global center
    allw=[M @ Vector((co[3*i],co[3*i+1],co[3*i+2])) for i in range(n)]
    cx=(min(v.x for v in allw)+max(v.x for v in allw))/2
    cy=(min(v.y for v in allw)+max(v.y for v in allw))/2
    out.append(" loop center approx (%.4f, %.4f)" % (cx,cy))
    for k,idxs in items[:12]:
        ws=[allw[i] for i in idxs]
        angs=sorted(math.degrees(math.atan2(v.y-cy, v.x-cx))%360 for v in ws)
        # find largest angular gap
        gaps=[(angs[i+1]-angs[i], angs[i], angs[i+1]) for i in range(len(angs)-1)]
        gaps.append((angs[0]+360-angs[-1], angs[-1], angs[0]+360))
        g=max(gaps)
        out.append("  comp n=%6d  X %.3f..%.3f Y %.3f..%.3f Z %.3f..%.3f  maxAngGap=%.1f deg (%.1f -> %.1f)" % (
            len(idxs), min(v.x for v in ws),max(v.x for v in ws),min(v.y for v in ws),max(v.y for v in ws),
            min(v.z for v in ws),max(v.z for v in ws), g[0],g[1],g[2]))
print("\n".join(out))
