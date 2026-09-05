import bpy
from mathutils import Vector
out=[]
for tag in ("StrapUpper","StrapLower"):
    cuo=bpy.data.objects["CRV_"+tag+"_Path"]; W=cuo.matrix_world
    dg=bpy.context.evaluated_depsgraph_get()
    ev=cuo.evaluated_get(dg); tm=ev.to_mesh()
    dn=[W@v.co.copy() for v in tm.vertices]; ev.to_mesh_clear()
    out.append("")
    out.append("%s curve: %d evaluated pts"%(tag,len(dn)))
    out.append("  first 12:")
    for p in dn[:12]: out.append("    (%+.4f,%+.4f,%+.4f)"%(p.x,p.y,p.z))
    out.append("  last 12:")
    for p in dn[-12:]: out.append("    (%+.4f,%+.4f,%+.4f)"%(p.x,p.y,p.z))
    # local curvature spikes
    bad=[]
    for i in range(2,len(dn)-2):
        a=(dn[i]-dn[i-2]).normalized(); b=(dn[i+2]-dn[i]).normalized()
        d=a.dot(b)
        if d<0.90: bad.append((i,i/(len(dn)-1.0),round(d,3),tuple(round(x,3) for x in dn[i])))
    out.append("  sharp turns (dot<0.90): %d  %s"%(len(bad),bad[:10]))
print("\n".join(out))
