import bpy, math
from mathutils import Vector, kdtree
out=[]
def wmat(o):
    m=o.matrix_basis.copy(); p=o.parent; c=o
    while p: m=p.matrix_basis@c.matrix_parent_inverse@m; c=p; p=p.parent
    return m
NS=4000
for tag,ob_n in (("StrapUpper","P07_STRAP_UPPER"),("StrapLower","P07_STRAP_LOWER")):
    cuo=bpy.data.objects["CRV_"+tag+"_Path"]; W=cuo.matrix_world
    dg=bpy.context.evaluated_depsgraph_get()
    tm=cuo.evaluated_get(dg).to_mesh()
    dn=[W@v.co.copy() for v in tm.vertices]
    cuo.evaluated_get(dg).to_mesh_clear()
    dl=[0.0]
    for j in range(1,len(dn)): dl.append(dl[-1]+(dn[j]-dn[j-1]).length)
    L=dl[-1]
    kd=kdtree.KDTree(len(dn))
    for i,p in enumerate(dn): kd.insert(Vector((p.x,p.y,0.0)),i)
    kd.balance()
    ob=bpy.data.objects[ob_n]; me=ob.data; M=wmat(ob)
    n=len(me.vertices); co=[0.0]*(n*3); me.vertices.foreach_get("co",co)
    far=[]
    for i in range(n):
        p=M@Vector((co[3*i],co[3*i+1],co[3*i+2]))
        _,idx,d=kd.find(Vector((p.x,p.y,0.0)))
        if d>0.028: far.append((d,p,dl[idx]/L))
    out.append("")
    out.append("%s: %d/%d verts >28mm from centreline (XY)"%(tag,len(far),n))
    if far:
        far.sort(reverse=True,key=lambda t:t[0])
        # cluster by s
        ss=sorted(f[2] for f in far)
        gr=[[ss[0]]]
        for v in ss[1:]:
            if v-gr[-1][-1]>0.02: gr.append([v])
            else: gr[-1].append(v)
        out.append("  clusters by s: %s"%["%.3f-%.3f n=%d"%(g[0],g[-1],len(g)) for g in gr])
        for d,p,s in far[:6]:
            out.append("   worst d=%.4f at (%.3f,%.3f,%.3f) s=%.3f"%(d,p.x,p.y,p.z,s))
print("\n".join(out))
