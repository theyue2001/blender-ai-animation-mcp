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
    T_arm = tree("X5_61.002"); T_shell = tree("X5_16_0.002"); T_shaft = tree("X5_56.002")
    sh = sc.objects["X5_16_0.002"]; mw = sh.matrix_world
    UP = Vector((0,0,1)); DOWN = Vector((0,0,-1))
    zs=[]
    for v in sh.data.vertices:
        wp = mw @ v.co
        if wp.z < 0.40: continue
        r = T_arm.ray_cast(wp+Vector((0,0,1e-5)), UP, 0.30)
        if r[0] is not None and (r[0].z - wp.z) < 0.0005: zs.append(wp.z)
    zs.sort()
    print("CONTACT verts (clearance<0.0005): n=%d  worldZ %.4f .. %.4f  (p05 %.4f, median %.4f)" % (
        len(zs), zs[0], zs[-1], zs[int(.05*len(zs))], zs[len(zs)//2]))
    # shell wall: cast down through crown, list all hits
    for (x,y) in [(0.05,-0.30),(0.05,-0.20),(-0.05,-0.35),(0.15,-0.30),(0.05,-0.45)]:
        o = Vector((x,y,1.2)); hits=[]
        for k in range(10):
            r = T_shell.ray_cast(o, DOWN)
            if r[0] is None: break
            hits.append(round(r[0].z,4)); o = r[0] + DOWN*1e-5
        print("  shell column at (%.2f,%.2f): hits z = %s" % (x,y,hits))
    # shaft vs shell bore radial clearance: sample horizontally at a few z
    print()
    ax, ay = 0.0493, -0.2705   # approx shaft axis from bbox of X5_56 (0.026..0.073 x, -0.294..-0.247 y)
    import math
    for z in (0.520, 0.535, 0.550, 0.560):
        rs=[]; rb=[]
        for k in range(16):
            a = 2*math.pi*k/16
            d = Vector((math.cos(a), math.sin(a), 0))
            o = Vector((ax, ay, z))
            r1 = T_shaft.ray_cast(o, d, 0.2)
            r2 = T_shell.ray_cast(o, d, 0.2)
            if r1[0] is not None: rs.append((r1[0]-o).length)
            if r2[0] is not None: rb.append((r2[0]-o).length)
        if rs and rb:
            print("  z=%.3f shaft r %.4f..%.4f   shell-bore r %.4f..%.4f   min radial gap %.4f" % (
                z, min(rs), max(rs), min(rb), max(rb), min(rb)-max(rs)))
        else:
            print("  z=%.3f shaft hits=%d shell hits=%d" % (z, len(rs), len(rb)))
finally:
    win.scene = prev
