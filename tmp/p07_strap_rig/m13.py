import bpy, heapq
from mathutils import Vector
out=[]
def wmat(o):
    m=o.matrix_basis.copy(); p=o.parent; c=o
    while p: m=p.matrix_basis@c.matrix_parent_inverse@m; c=p; p=p.parent
    return m
src="64.002"
o=bpy.data.objects[src]; M=wmat(o); me=o.data
n=len(me.vertices); co=[0.0]*(n*3); me.vertices.foreach_get("co",co)
P=[M@Vector((co[3*i],co[3*i+1],co[3*i+2])) for i in range(n)]
ne=len(me.edges); ev=[0]*(ne*2); me.edges.foreach_get("vertices",ev)
adj=[[] for _ in range(n)]
for k in range(ne):
    a,b=ev[2*k],ev[2*k+1]; w=(P[a]-P[b]).length
    adj[a].append((b,w)); adj[b].append((a,w))
seenv=[False]*n; shells=[]
for s in range(n):
    if seenv[s]: continue
    st=[s]; seenv[s]=True; c=[]
    while st:
        q=st.pop(); c.append(q)
        for r,_ in adj[q]:
            if not seenv[r]: seenv[r]=True; st.append(r)
    shells.append(c)
shells.sort(key=len,reverse=True)
HW={"59":((0.033,0.501),(-1.593,-1.443)),"60":((-0.433,-0.063),(-1.583,-1.486))}
for si in (0,1):
    sh=shells[si]
    sh2=sorted(sh,key=lambda i:(P[i].x+0.26)**2+(P[i].y+1.53)**2)
    seeds=sh2[:250]
    out.append("")
    out.append("### shell %d nv=%d  seed centroid=(%.3f,%.3f) spread z %.3f..%.3f"
               %(si,len(sh),sum(P[i].x for i in seeds)/250,sum(P[i].y for i in seeds)/250,
                 min(P[i].z for i in seeds),max(P[i].z for i in seeds)))
    INF=1e18; d={i:INF for i in sh}; h=[]
    for i in seeds: d[i]=0.0; h.append((0.0,i))
    heapq.heapify(h)
    while h:
        du,u=heapq.heappop(h)
        if du>d[u]+1e-12: continue
        for v,w in adj[u]:
            nd=du+w
            if nd<d[v]-1e-12: d[v]=nd; heapq.heappush(h,(nd,v))
    D=max(d.values())
    out.append("  max geodesic = %.4f"%D)
    NB=40; acc=[[0.0,0.0,0.0,0] for _ in range(NB)]
    for i in sh:
        b=min(NB-1,int(d[i]/D*NB)); acc[b][0]+=P[i].x; acc[b][1]+=P[i].y; acc[b][2]+=P[i].z; acc[b][3]+=1
    out.append("    d      x       y     nv    | hw")
    for b in range(NB):
        a=acc[b]
        if not a[3]: continue
        x,y=a[0]/a[3],a[1]/a[3]
        hw=[k for k,(bx,by) in HW.items() if bx[0]<=x<=bx[1] and by[0]<=y<=by[1]]
        out.append("  %6.3f %7.3f %7.3f %6d | %s"%((b+0.5)/NB*D,x,y,a[3]," ".join(hw)))
print("\n".join(out))
