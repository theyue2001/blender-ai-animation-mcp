import bpy
from mathutils import Vector
SN="05_SCN_P07_STRAP_RIG"; sc=bpy.data.scenes[SN]
out=[]; prev=bpy.context.window.scene
def wmat(o):
    m=o.matrix_basis.copy(); p=o.parent; c=o
    while p: m=p.matrix_basis@c.matrix_parent_inverse@m; c=p; p=p.parent
    return m
try:
    bpy.context.window.scene=sc
    tag="StrapUpper"
    cuo=bpy.data.objects["CRV_%s_Path"%tag]; ob=bpy.data.objects["P07_STRAP_UPPER"]
    me=ob.data; Mo=wmat(ob)
    vg=ob.vertex_groups["DEF_%s_23"%tag]
    tailv=[v.index for v in me.vertices if any(g.group==vg.index and g.weight>0.9 for g in v.groups)][:300]
    n=len(me.vertices)
    out.append("frame  curveL   chain=5.6095  tail-tip centroid        travel-from-rest")
    base=None
    for f in (1824,1848,1872,1896,1920,1944,1968,1992,2016):
        sc.frame_set(f)
        dg=bpy.context.evaluated_depsgraph_get()
        ev=cuo.evaluated_get(dg); tm=ev.to_mesh()
        dn=[cuo.matrix_world@v.co.copy() for v in tm.vertices]
        L=sum((dn[j]-dn[j-1]).length for j in range(1,len(dn))); ev.to_mesh_clear()
        evo=ob.evaluated_get(dg); m2=evo.to_mesh()
        d=[0.0]*(n*3); m2.vertices.foreach_get("co",d)
        pts=[Mo@Vector((d[3*i],d[3*i+1],d[3*i+2])) for i in tailv]
        cx=sum(p.x for p in pts)/len(pts); cy=sum(p.y for p in pts)/len(pts)
        evo.to_mesh_clear()
        if base is None: base=(cx,cy)
        tv=((cx-base[0])**2+(cy-base[1])**2)**0.5
        out.append("%-6d %.4f  slack=%+.4f  (%+.4f,%+.4f)  %.4f = %.1f band widths"
                   %(f,L,L-5.6095,cx,cy,tv,tv/0.232))
finally:
    bpy.context.window.scene=prev
print("\n".join(out))
