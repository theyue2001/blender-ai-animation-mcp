import bpy, math
from mathutils import Vector
SN = "05_SCN_P07_STRAP_RIG"
sc = bpy.data.scenes[SN]
prev = bpy.context.window.scene
out = []
try:
    bpy.context.window.scene = sc
    dg = bpy.context.evaluated_depsgraph_get()
    for nm in ("P07_STRAP_UPPER", "P07_STRAP_LOWER"):
        ob = bpy.data.objects[nm]
        base = ob.data
        ev = ob.evaluated_get(dg)
        me = ev.to_mesh()
        n = len(base.vertices)
        assert len(me.vertices) == n, "vert count mismatch"
        a = [0.0] * (n * 3); base.vertices.foreach_get("co", a)
        b = [0.0] * (n * 3); me.vertices.foreach_get("co", b)
        sc_ = ob.matrix_world.to_scale()[0]
        mx = 0.0; tot = 0.0; over = 0
        for i in range(n):
            d = math.sqrt((a[3*i]-b[3*i])**2 + (a[3*i+1]-b[3*i+1])**2 + (a[3*i+2]-b[3*i+2])**2) * sc_
            tot += d
            if d > mx: mx = d
            if d > 0.002: over += 1
        ev.to_mesh_clear()
        out.append("%s rest-pose delta: max=%.5f mean=%.6f  verts>2mm=%d / %d" % (nm, mx, tot/n, over, n))
    # curve/hook sanity
    for nm in ("CRV_StrapUpper_Path", "CRV_StrapLower_Path"):
        c = bpy.data.objects[nm]
        out.append("%s hooks=%d spline_pts=%d" % (nm, len([m for m in c.modifiers if m.type=='HOOK']), len(c.data.splines[0].bezier_points)))
    for nm in ("NITE_StrapUpper_Armature", "NITE_StrapLower_Armature"):
        a = bpy.data.objects[nm]
        cons = [(pb.name, c.type, c.target.name if getattr(c,'target',None) else None, c.chain_count) for pb in a.pose.bones for c in pb.constraints]
        out.append("%s bones=%d deform=%d cons=%s" % (nm, len(a.data.bones), sum(1 for b in a.data.bones if b.use_deform), cons))
finally:
    bpy.context.window.scene = prev
print("\n".join(out))
