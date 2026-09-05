import bpy, heapq, time
from mathutils import Vector
out=[]
def wmat(o):
    m=o.matrix_basis.copy(); p=o.parent; c=o
    while p: m=p.matrix_basis@c.matrix_parent_inverse@m; c=p; p=p.parent
    return m
for src,A,B in (("64.002",(-0.250,-1.528),(-0.889,-1.879)),
                ("65.002",(-0.360,-1.530),(+0.470,-1.535))):
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
    out.append(""); out.append("### %s  %d shells"%(src,len(shells)))
    t0=time.time()
    for si,sh in enumerate(shells[:10]):
        S=set(sh)
        seeds=[i for i in sh if (P[i].x-A[0])**2+(P[i].y-A[1])**2 < 0.030**2]
        if not seeds:
            out.append("  shell %-2d nv=%-6d  NO seed near A"%(si,len(sh))); continue
        INF=1e18; d={i:INF for i in sh}; h=[]
        for i in seeds: d[i]=0.0; h.append((0.0,i))
        heapq.heapify(h)
        while h:
            du,u=heapq.heappop(h)
            if du>d[u]+1e-12: continue
            for v,w in adj[u]:
                nd=du+w
                if nd<d[v]-1e-12: d[v]=nd; heapq.heappush(h,(nd,v))
        dm=max(d.values()); unre=sum(1 for v in d.values() if v>=INF)
        far=max(sh,key=lambda i:d[i])
        out.append("  shell %-2d nv=%-6d seeds=%-5d maxgeo=%.4f unreached=%-5d far@(%.3f,%.3f) distB=%.3f"
                   %(si,len(sh),len(seeds),dm,unre,P[far].x,P[far].y,
                     ((P[far].x-B[0])**2+(P[far].y-B[1])**2)**0.5))
    out.append("  (%.1fs)"%(time.time()-t0))
print("\n".join(out))
