import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sc = bpy.data.scenes["SCN_P05_XRAY_MECHANISM"]
win = bpy.context.window; prev = win.scene
try:
    win.scene = sc; sc.frame_set(1434)
    dg = bpy.context.evaluated_depsgraph_get()
    sh = sc.objects["X5_16_0.002"]; arm = sc.objects["X5_61.002"]
    print("shell loc=%s rot=%s scale=%s" % (tuple(round(v,5) for v in sh.location),
          tuple(round(v,6) for v in sh.rotation_euler), tuple(round(v,6) for v in sh.scale)))
    print("shell matrix_world:")
    for r in sh.matrix_world: print("   ", tuple(round(v,6) for v in r))
    print("arm  loc=%s rot=%s scale=%s" % (tuple(round(v,5) for v in arm.location),
          tuple(round(v,6) for v in arm.rotation_euler), tuple(round(v,6) for v in arm.scale)))
    print("shell parent:", sh.parent.name if sh.parent else None, " arm parent:", arm.parent.name if arm.parent else None)
    print("shell anim:", bool(sh.animation_data and sh.animation_data.action))
    # arm BVH in world
    ae = arm.evaluated_get(dg)
    bm = bmesh.new(); bm.from_mesh(ae.data); bm.transform(ae.matrix_world)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    T_arm = BVHTree.FromBMesh(bm); bm.free()
    UP = Vector((0,0,1))
    mw = sh.matrix_world
    me = sh.data
    n_under = 0; clear = []
    zs_under = []
    for v in me.vertices:
        wp = mw @ v.co
        if wp.z < 0.40: continue
        r = T_arm.ray_cast(wp + Vector((0,0,1e-5)), UP, 0.30)
        if r[0] is None: continue
        c = r[0].z - wp.z
        n_under += 1; clear.append(c); zs_under.append(wp.z)
    clear.sort()
    import statistics
    print("shell verts above z=0.40 that have arm overhead: %d / %d" % (n_under, len(me.vertices)))
    print("clearance min=%.5f  p05=%.5f  median=%.5f  p95=%.5f  max=%.5f" % (
        clear[0], clear[int(.05*len(clear))], clear[len(clear)//2], clear[int(.95*len(clear))], clear[-1]))
    for thr in (0.0005, 0.001, 0.002, 0.004, 0.006, 0.010, 0.020, 0.040):
        print("   clearance < %.4f : %d verts" % (thr, sum(1 for c in clear if c < thr)))
    print("world Z of those verts: %.4f .. %.4f" % (min(zs_under), max(zs_under)))
finally:
    win.scene = prev
