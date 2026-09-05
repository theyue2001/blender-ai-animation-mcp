import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sc = bpy.data.scenes["SCN_P05_XRAY_MECHANISM"]
win = bpy.context.window; prev = win.scene
try:
    win.scene = sc; sc.frame_set(1434)
    dg = bpy.context.evaluated_depsgraph_get()
    def tree(n):
        oe = sc.objects[n].evaluated_get(dg)
        bm = bmesh.new(); bm.from_mesh(oe.data); bm.transform(oe.matrix_world)
        bmesh.ops.triangulate(bm, faces=bm.faces)
        t = BVHTree.FromBMesh(bm); bm.free(); return t
    T_arm = tree("X5_61.002")
    sh = sc.objects["X5_16_0.002"]; mw = sh.matrix_world; UP=Vector((0,0,1))
    cl=[]
    for v in sh.data.vertices:
        wp = mw @ v.co
        if wp.z < 0.40: continue
        r = T_arm.ray_cast(wp+Vector((0,0,1e-5)), UP, 0.30)
        if r[0] is None: continue
        cl.append((r[0].z-wp.z, wp.copy()))
    cl.sort(key=lambda t:t[0])
    print("cover verts under the arm: %d" % len(cl))
    print("min clearance %.5f  p01 %.5f  p05 %.5f  median %.5f" % (
        cl[0][0], cl[int(.01*len(cl))][0], cl[int(.05*len(cl))][0], cl[len(cl)//2][0]))
    for thr in (0.0002,0.0005,0.001,0.002,0.003):
        print("   clearance < %.4f : %d verts" % (thr, sum(1 for c,_ in cl if c<thr)))
    print("  10 tightest, world pos:")
    for c,p in cl[:10]:
        print("     %.5f  (%.4f,%.4f,%.4f)" % (c,p.x,p.y,p.z))
    # wall thickness spot check
    T_sh = tree("X5_16_0.002"); DOWN=Vector((0,0,-1))
    print("  wall thickness at crown columns:")
    for (x,y) in [(0.05,-0.20),(-0.05,-0.35),(0.15,-0.30),(0.05,-0.45),(0.10,-0.25)]:
        o=Vector((x,y,1.2)); hits=[]
        for k in range(4):
            r=T_sh.ray_cast(o,DOWN)
            if r[0] is None: break
            hits.append(r[0].z); o=r[0]+DOWN*1e-5
        if len(hits)>1: print("     (%.2f,%.2f) outer %.4f inner %.4f  thickness %.4f" % (x,y,hits[0],hits[1],hits[0]-hits[1]))
finally:
    win.scene = prev
