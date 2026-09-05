import bpy, math
from mathutils import Vector
out=[]
def wmat(o):
    m=o.matrix_basis.copy(); p=o.parent; c=o
    while p: m=p.matrix_basis@c.matrix_parent_inverse@m; c=p; p=p.parent
    return m
for src in ("64.002","65.002"):
    o=bpy.data.objects[src]; M=wmat(o); me=o.data
    n=len(me.vertices); co=[0.0]*(n*3); me.vertices.foreach_get("co",co)
    P=[M@Vector((co[3*i],co[3*i+1],co[3*i+2])) for i in range(n)]
    ec={}
    for pg in me.polygons:
        for e in pg.edge_keys: ec[e]=ec.get(e,0)+1
    be=[e for e,c in ec.items() if c==1]
    adj={}
    for a,b in be:
        adj.setdefault(a,[]).append(b); adj.setdefault(b,[]).append(a)
    seen=set(); comps=[]
    for s in adj:
        if s in seen: continue
        st=[s]; seen.add(s); c=[]
        while st:
            q=st.pop(); c.append(q)
            for r in adj[q]:
                if r not in seen: seen.add(r); st.append(r)
        comps.append(c)
    comps.sort(key=len, reverse=True)
    out.append("")
    out.append("### %s : %d boundary comps"%(src,len(comps)))
    out.append("  idx  nv    dx     dy     dz    | ctr(x,y,z)              | shape")
    for i,c in enumerate(comps):
        pts=[P[v] for v in c]
        lo=Vector((min(p.x for p in pts),min(p.y for p in pts),min(p.z for p in pts)))
        hi=Vector((max(p.x for p in pts),max(p.y for p in pts),max(p.z for p in pts)))
        d=hi-lo; ctr=(lo+hi)*0.5
        sh=""
        if d.z>0.20 and max(d.x,d.y)<0.10: sh="<<< CUT END (full-width, thin)"
        elif d.z<0.01: sh="flat rim (const z)"
        out.append("  %-4d %-5d %.3f  %.3f  %.3f | (%+.3f,%+.3f,%+.3f) | %s"%(i,len(c),d.x,d.y,d.z,ctr.x,ctr.y,ctr.z,sh))
        if i>25: out.append("   ... (%d more)"%(len(comps)-i-1)); break
print("\n".join(out))
