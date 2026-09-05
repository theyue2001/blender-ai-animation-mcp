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
ne=len(me.edges); ev=[0]*(ne*2); me.edges.foreach_get("vertices",ev)
adj=[[] for _ in range(n)]
for k in range(ne):
    a,b=ev[2*k],ev[2*k+1]; adj[a].append(b); adj[b].append(a)
seen=[False]*n; comps=[]
for s in range(n):
    if seen[s]: continue
    st=[s]; seen[s]=True; c=[]
    while st:
        q=st.pop(); c.append(q)
        for r in adj[q]:
            if not seen[r]: seen[r]=True; st.append(r)
    comps.append(c)
comps.sort(key=len, reverse=True)
out.append("64.002: %d shells"%len(comps))
out.append(" idx  nv     x-range         y-range         z-range      | arc(deg span) | note")
for i,c in enumerate(comps[:16]):
    pts=[P[v] for v in c]
    lo=Vector((min(p.x for p in pts),min(p.y for p in pts),min(p.z for p in pts)))
    hi=Vector((max(p.x for p in pts),max(p.y for p in pts),max(p.z for p in pts)))
    C=(0.059,-2.184)
    ang=sorted(math.degrees(math.atan2(p.y-C[1],p.x-C[0]))%360.0 for p in pts)
    # largest angular gap
    gaps=[(ang[(k+1)%len(ang)]-ang[k])%360.0 for k in range(len(ang))]
    g=max(gaps); gi=gaps.index(g)
    span=360.0-g
    st_=ang[(gi+1)%len(ang)]
    note=""
    if hi.x<-0.20 and lo.x>-1.0 and span<120: note="<-- TAIL candidate"
    out.append(" %-4d %-6d %+.3f..%+.3f  %+.3f..%+.3f  %+.3f..%+.3f | %6.1f from %5.1f | %s"
               %(i,len(c),lo.x,hi.x,lo.y,hi.y,lo.z,hi.z,span,st_,note))
print("\n".join(out))
