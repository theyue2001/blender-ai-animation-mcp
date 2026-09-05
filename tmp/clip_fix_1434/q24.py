import bpy, math
from mathutils import Vector
sc = bpy.data.scenes["SCN_P05_XRAY_MECHANISM"]
win=bpy.context.window; prev=win.scene
try:
    win.scene=sc
    print("=== transforms / animation ===")
    for n in ["X5_1.002","X5_2.002","X5_4.002","X5_6.002","X5_8.002","X5_10.002","X5_12.002",
              "X5_MOTOR_SPIN","X5_CARRIAGE"]:
        o=sc.objects.get(n)
        if not o: print("  %s MISSING"%n); continue
        ad=o.animation_data
        act=ad.action.name if ad and ad.action else None
        drv = len(ad.drivers) if ad else 0
        print("  %-15s parent=%-14s action=%-22s drivers=%d constraints=%s" % (
            n, o.parent.name if o.parent else "-", str(act), drv,
            [c.type for c in o.constraints]))
    print()
    print("=== does the protrusion change over the P05 range? (X5_8.002 vs X5_1.002 outer wall) ===")
    import bmesh
    from mathutils.bvhtree import BVHTree
    for f in (1080,1200,1260,1350,1434,1500,1620,1700,1800):
        sc.frame_set(f)
        dg=bpy.context.evaluated_depsgraph_get()
        def tb(n):
            oe=sc.objects[n].evaluated_get(dg)
            bm=bmesh.new(); bm.from_mesh(oe.data); bm.transform(oe.matrix_world)
            bmesh.ops.triangulate(bm,faces=bm.faces); t=BVHTree.FromBMesh(bm); bm.free(); return t
        T8=tb("X5_8.002"); T1=tb("X5_1.002")
        ov=T8.overlap(T1)
        o8=sc.objects["X5_8.002"].evaluated_get(dg)
        bb=[o8.matrix_world @ Vector(c) for c in o8.bound_box]
        mxx=max(p.x for p in bb)
        o1=sc.objects["X5_1.002"].evaluated_get(dg)
        bb1=[o1.matrix_world @ Vector(c) for c in o1.bound_box]
        mxx1=max(p.x for p in bb1)
        rot=tuple(round(math.degrees(v),1) for v in o8.matrix_world.to_euler())
        print("  frame %4d: 8x1 tris=%5d  8.002 maxX=%.4f  1.002 maxX=%.4f  protrusion=%+.4f  8.002 rot=%s" % (
            f, len(ov), mxx, mxx1, mxx-mxx1, rot))
finally:
    sc.frame_set(1434); win.scene=prev
