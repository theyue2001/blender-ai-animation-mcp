import bpy, math
from mathutils import Vector
def wmat(o):
    m=o.matrix_basis.copy(); p=o.parent; c=o
    while p:
        m=p.matrix_basis @ c.matrix_parent_inverse @ m; c=p; p=p.parent
    return m
out=[]
for name,C in (("64.002",(0.0589,-2.1837)),("65.002",(0.0455,-2.3473))):
    o=bpy.data.objects[name]; M=wmat(o); me=o.data
    n=len(me.vertices); co=[0.0]*(n*3); me.vertices.foreach_get("co",co)
    bins={}
    for i in range(n):
        v=M @ Vector((co[3*i],co[3*i+1],co[3*i+2]))
        a=math.degrees(math.atan2(v.y-C[1], v.x-C[0]))%360
        r=math.hypot(v.x-C[0], v.y-C[1])
        b=int(a//5)
        bins.setdefault(b,[]).append(r)
    out.append("=== %s  (radial profile per 5deg bin) ===" % name)
    for b in range(72):
        rs=bins.get(b)
        if not rs:
            out.append(" %3d-%3d : EMPTY" % (b*5,b*5+5)); continue
        rs.sort()
        # cluster gaps
        gaps=[(rs[i+1]-rs[i], rs[i]) for i in range(len(rs)-1)]
        g=max(gaps) if gaps else (0,0)
        out.append(" %3d-%3d : n=%5d r %.3f..%.3f span %.3f  maxRadGap %.3f @%.3f" % (
            b*5,b*5+5,len(rs),rs[0],rs[-1],rs[-1]-rs[0],g[0],g[1]))
print("\n".join(out))
