import bpy, mathutils
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
L=[]
sc = bpy.data.scenes["03_SCN_P05_XRAY_MECHANISM"]
prev = bpy.context.window.scene
try:
    bpy.context.window.scene = sc
    sc.frame_set(1396)
    dg = bpy.context.evaluated_depsgraph_get()
    cam = sc.camera
    L.append("cam=%s  world=%s lens=%.1f" % (cam.name, tuple(round(v,3) for v in cam.matrix_world.translation), cam.data.lens))

    logo = bpy.data.objects["WRN_DECAL_NITE_R1_Logo"]
    le = logo.evaluated_get(dg)
    me = le.to_mesh()
    ws = [le.matrix_world @ v.co for v in me.vertices]
    ctr = sum(ws, Vector()) / len(ws)
    le.to_mesh_clear()
    L.append("logo verts=%d world_ctr=%s" % (len(ws), tuple(round(v,4) for v in ctr)))
    mn = Vector((min(v.x for v in ws), min(v.y for v in ws), min(v.z for v in ws)))
    mx = Vector((max(v.x for v in ws), max(v.y for v in ws), max(v.z for v in ws)))
    L.append("logo bbox size=%s" % (tuple(round(v,4) for v in (mx-mn)),))

    from bpy_extras.object_utils import world_to_camera_view
    RX, RY = sc.render.resolution_x, sc.render.resolution_y
    def proj(p):
        c = world_to_camera_view(sc, cam, p)
        return (round(c.x*RX), round((1-c.y)*RY), round(c.z,3))
    L.append("logo ctr px=%s  (res %dx%d)" % (proj(ctr), RX, RY))
    pxs = [proj(v) for v in ws]
    L.append("logo px bbox x=%d..%d y=%d..%d" % (min(p[0] for p in pxs), max(p[0] for p in pxs), min(p[1] for p in pxs), max(p[1] for p in pxs)))

    # occlusion: ray from camera to logo centre
    camloc = cam.matrix_world.translation
    d = (ctr - camloc); dist = d.length; d.normalize()
    hit, loc, nor, idx, obj, mtx = sc.ray_cast(dg, camloc, d, distance=dist*1.2)
    L.append("raycast cam->logo: hit=%s obj=%s at %s (t=%.4f, logo dist=%.4f)" % (hit, obj.name if obj else None, tuple(round(v,4) for v in loc) if hit else None, (loc-camloc).length if hit else -1, dist))

    # normal of the logo (average)
    lm = le.to_mesh() if False else None
    me2 = logo.data
    nrm = Vector()
    for p in me2.polygons: nrm += (logo.matrix_world.to_3x3() @ p.normal)
    nrm.normalize()
    L.append("logo avg world normal=%s   dot(to_cam)=%.3f" % (tuple(round(v,4) for v in nrm), nrm.dot((camloc-ctr).normalized())))

    L.append("")
    L.append("=== LIGHT LINKING ===")
    for o in sc.objects:
        if o.type != 'LIGHT': continue
        ll = o.light_linking
        rc = ll.receiver_collection.name if ll and ll.receiver_collection else None
        bc = ll.blocker_collection.name if ll and ll.blocker_collection else None
        L.append("  %-26s E=%-8s type=%-5s recv=%-24s block=%s" % (o.name, round(o.data.energy,2), o.data.type, rc, bc))
    L.append("")
    for cn in ["P05_LINK_WORN_RECV","P05_LINK_XRAY_RECV"]:
        c = bpy.data.collections.get(cn)
        L.append("  coll %s: %d objs -> %s" % (cn, len(c.objects) if c else -1, [x.name for x in c.objects][:60] if c else None))
finally:
    bpy.context.window.scene = prev
print("\n".join(L))
