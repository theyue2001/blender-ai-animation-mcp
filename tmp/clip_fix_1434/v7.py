import bpy, bmesh, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
src=bpy.data.scenes["SCN_P05_XRAY_MECHANISM"]
win=bpy.context.window; prev=win.scene
try:
    win.scene=src
    for f in (1080,1434):
        src.frame_set(f)
        dg=bpy.context.evaluated_depsgraph_get()
        o=src.objects["X5_8.002"].evaluated_get(dg)
        loc=o.matrix_world.translation; rot=o.matrix_world.to_euler()
        print("frame %d  X5_8.002 world loc=(%.5f,%.5f,%.5f) rotZ=%.3f deg" % (
            f, loc.x,loc.y,loc.z, math.degrees(rot.z)))
        def tb(n):
            oe=src.objects[n].evaluated_get(dg)
            bm=bmesh.new(); bm.from_mesh(oe.data); bm.transform(oe.matrix_world)
            bmesh.ops.triangulate(bm,faces=bm.faces); t=BVHTree.FromBMesh(bm); bm.free(); return t
        T8=tb("X5_8.002")
        for n in ["X5_1.002","X5_2.002","X5_4.002","X5_6.002","X5_10.002","X5_16_0.002"]:
            print("     8.002 x %-11s %d" % (n.replace("X5_",""), len(T8.overlap(tb(n)))))
    # crank arm 12.002 : does it breach the OUTER surface anywhere?
    print()
    print("=== 12.002 (crank arm, still orbiting - correct) outer-surface check ===")
    AX,AY=0.0493,-0.3201
    worst=-9; wf=None
    for f in range(1080,1801,20):
        src.frame_set(f)
        dg=bpy.context.evaluated_depsgraph_get()
        o=src.objects["X5_12.002"].evaluated_get(dg); mw=o.matrix_world
        # sample verts, find max radius at heights where 1.002's wall exists
        mx=-9
        for v in o.data.vertices:
            p=mw@v.co
            if 0.085<=p.z<=0.288:
                mx=max(mx, math.hypot(p.x-AX,p.y-AY))
        if mx>worst: worst,wf=mx,f
    print("   max radius of 12.002 within the body's z-range = %.4f at frame %s" % (worst,wf))
    print("   body 1.002 minimum wall radius in that band = 0.208  ->  %s" % (
        "BREACH" if worst>0.208 else "clear"))
finally:
    src.frame_set(1434); win.scene=prev
