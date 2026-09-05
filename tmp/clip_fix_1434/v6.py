import bpy, bmesh, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
src=bpy.data.scenes["SCN_P05_XRAY_MECHANISM"]
win=bpy.context.window; prev=win.scene
try:
    win.scene=src
    AX,AY=0.0493,-0.3201
    print("frame | gearZ(deg) | 8x1 | 8x2 | 8x6 | 12x1 | maxX(8.002) vs body 0.2584 | breach")
    worst=-9
    for f in range(1080,1801,45):
        src.frame_set(f)
        dg=bpy.context.evaluated_depsgraph_get()
        def tb(n):
            oe=src.objects[n].evaluated_get(dg)
            bm=bmesh.new(); bm.from_mesh(oe.data); bm.transform(oe.matrix_world)
            bmesh.ops.triangulate(bm,faces=bm.faces); t=BVHTree.FromBMesh(bm); bm.free(); return t
        T8=tb("X5_8.002"); T1=tb("X5_1.002")
        o8=src.objects["X5_8.002"].evaluated_get(dg)
        bb=[o8.matrix_world@Vector(c) for c in o8.bound_box]
        mxx=max(p.x for p in bb)
        gz=math.degrees(src.objects["X5_GEAR_SPIN"].evaluated_get(dg).matrix_world.to_euler().z)
        n81=len(T8.overlap(T1)); n82=len(T8.overlap(tb("X5_2.002"))); n86=len(T8.overlap(tb("X5_6.002")))
        n121=len(tb("X5_12.002").overlap(T1))
        br = mxx-0.2584
        worst=max(worst,br)
        print(" %4d | %10.1f | %3d | %3d | %3d | %4d | %.4f | %+.4f %s" % (
            f, gz, n81, n82, n86, n121, mxx, br, "<<< BREACH" if br>0 else ""))
    print()
    print("worst outer-surface breach across the range: %+.4f (negative = fully inside)" % worst)
finally:
    src.frame_set(1434); win.scene=prev
