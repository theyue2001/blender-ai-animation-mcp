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
ec={}
for pg in me.polygons:
    for e in pg.edge_keys: ec[e]=ec.get(e,0)+1
be=[e for e,c in ec.items() if c==1]
adj={}
for a,b in be:
    adj.setdefault(a,[]).append(b); adj.setdefault(b,[]).append(a)
seen=set(); loops=[]
for s in adj:
    if s in seen: continue
    st=[s]; seen.add(s); comp=[]
    while st:
        q=st.pop(); comp.append(q)
        for r in adj[q]:
            if r not in seen: seen.add(r); st.append(r)
    loops.append(comp)
loops.sort(key=len, reverse=True)
out.append("boundary edges=%d  components=%d  sizes=%s"%(len(be),len(loops),[len(l) for l in loops[:12]]))
# trace the biggest loop in order
big=set(loops[0])
start=min(loops[0], key=lambda i:(P[i].x))
path=[start]; prev=None; cur=start
while True:
    nx=[v for v in adj[cur] if v!=prev]
    if not nx: break
    nxt=nx[0]
    if nxt==start: break
    path.append(nxt); prev=cur; cur=nxt
    if len(path)>len(loops[0])+5: break
out.append("traced ordered path length=%d of component %d (closed=%s)"%(len(path),len(loops[0]),len(path)>=len(loops[0])-1))
L=0.0; ss=[0.0]
for i in range(1,len(path)):
    L+=(P[path[i]]-P[path[i-1]]).length; ss.append(L)
out.append("rim arc length total=%.4f"%L)
out.append("")
out.append("  s      s/L    x       y       z     | note")
prev_note=None
for k in range(0,len(path), max(1,len(path)//90)):
    p=P[path[k]]
    note=[]
    if -0.433<=p.x<=-0.063 and -1.583<=p.y<=-1.486: note.append("in60box")
    if -1.579<=p.y<=-1.549: note.append("IN-SLOT60")
    if 0.033<=p.x<=0.501 and -1.593<=p.y<=-1.443: note.append("in59box")
    out.append("%7.3f %6.3f %7.3f %7.3f %7.3f | %s"%(ss[k],ss[k]/L,p.x,p.y,p.z," ".join(note)))
print("\n".join(out))
