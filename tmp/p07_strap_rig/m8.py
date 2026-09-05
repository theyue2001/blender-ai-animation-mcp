import bpy, math, heapq, time
from mathutils import Vector
out=[]
def wmat(o):
    m=o.matrix_basis.copy(); p=o.parent; c=o
    while p: m=p.matrix_basis@c.matrix_parent_inverse@m; c=p; p=p.parent
    return m

for src,ANCH,TIP in (("64.002",(-0.250,-1.528,1.000),(-0.889,-1.879,0.960)),
                     ("65.002",(-0.360,-1.530,0.229),(+0.470,-1.535,0.229))):
    t0=time.time()
    o=bpy.data.objects[src]; M=wmat(o); me=o.data
    n=len(me.vertices); co=[0.0]*(n*3); me.vertices.foreach_get("co",co)
    P=[M@Vector((co[3*i],co[3*i+1],co[3*i+2])) for i in range(n)]
    ne=len(me.edges); ev=[0]*(ne*2); me.edges.foreach_get("vertices",ev)
    adj=[[] for _ in range(n)]
    for k in range(ne):
        a,b=ev[2*k],ev[2*k+1]; w=(P[a]-P[b]).length
        adj[a].append((b,w)); adj[b].append((a,w))
    # connectivity
    seen=[False]*n; comps=[]
    for s in range(n):
        if seen[s]: continue
        st=[s]; seen[s]=True; c=0
        while st:
            q=st.pop(); c+=1
            for r,_ in adj[q]:
                if not seen[r]: seen[r]=True; st.append(r)
        comps.append(c)
    comps.sort(reverse=True)
    out.append("")
    out.append("### %s  n=%d  edges=%d  connected comps=%d sizes=%s"%(src,n,ne,len(comps),comps[:6]))
    # seed = verts near ANCH end cap
    A=Vector(ANCH)
    seeds=[i for i in range(n) if (P[i]-A).length<0.14]
    out.append("  anchor seeds within 0.14 of %s : %d"%(ANCH,len(seeds)))
    INF=1e18; d=[INF]*n; h=[]
    for i in seeds: d[i]=0.0; h.append((0.0,i))
    heapq.heapify(h)
    while h:
        du,u=heapq.heappop(h)
        if du>d[u]+1e-12: continue
        for v,w in adj[u]:
            nd=du+w
            if nd<d[v]-1e-12: d[v]=nd; heapq.heappush(h,(nd,v))
    reach=[i for i in range(n) if d[i]<INF]
    out.append("  reached %d / %d verts   max geodesic=%.4f   (%.1fs)"%(len(reach),n,max(d[i] for i in reach),time.time()-t0))
    T=Vector(TIP)
    tipv=[i for i in reach if (P[i]-T).length<0.10]
    if tipv: out.append("  geodesic at the TIP %s : %.4f .. %.4f"%(TIP,min(d[i] for i in tipv),max(d[i] for i in tipv)))
    D=max(d[i] for i in reach)
    # profile: centroid per geodesic bin
    NB=48; acc=[[0.0,0.0,0.0,0] for _ in range(NB)]
    for i in reach:
        b=min(NB-1,int(d[i]/D*NB))
        acc[b][0]+=P[i].x; acc[b][1]+=P[i].y; acc[b][2]+=P[i].z; acc[b][3]+=1
    out.append("   s      d      x       y       z    nv   | hardware")
    for b in range(NB):
        a=acc[b]
        if not a[3]: continue
        x,y,z=a[0]/a[3],a[1]/a[3],a[2]/a[3]
        hw=[]
        if -0.433<=x<=-0.063 and -1.583<=y<=-1.486 and 0.83<=z<=1.21: hw.append("60")
        if 0.033<=x<=0.501 and -1.593<=y<=-1.443 and 0.83<=z<=1.21: hw.append("59")
        if -0.320<=x<=-0.173 and -1.544<=y<=-1.485 and 0.12<=z<=0.36: hw.append("63")
        if 0.270<=x<=0.418 and -1.544<=y<=-1.485 and 0.12<=z<=0.36: hw.append("64k")
        out.append("  %.3f %6.3f %7.3f %7.3f %7.3f %5d | %s"%((b+0.5)/NB,(b+0.5)/NB*D,x,y,z,a[3]," ".join(hw)))
print("\n".join(out))
