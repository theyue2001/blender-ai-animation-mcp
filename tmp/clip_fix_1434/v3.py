import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
sc = bpy.data.scenes["SCN_P05_XRAY_MECHANISM"]
win = bpy.context.window; prev = win.scene
try:
    win.scene = sc; sc.frame_set(1434)
    dg = bpy.context.evaluated_depsgraph_get()
    print("--- animation on the parts involved ---")
    for n in ["X5_16_0.002","X5_61.002","X5_56.002","X5_62.002","CAM_P05_XRAY"]:
        o = sc.objects[n]
        ad = o.animation_data
        cons = [(c.type, getattr(c,'target',None).name if getattr(c,'target',None) else '') for c in o.constraints]
        print("  %-16s action=%s  constraints=%s" % (n, ad.action.name if ad and ad.action else None, cons))
    def tree(n):
        oe = sc.objects[n].evaluated_get(dg)
        bm = bmesh.new(); bm.from_mesh(oe.data); bm.transform(oe.matrix_world)
        bmesh.ops.triangulate(bm, faces=bm.faces); bm.faces.ensure_lookup_table()
        return BVHTree.FromBMesh(bm), bm
    tA, bmA = tree("X5_16_0.002")
    cam = sc.camera.evaluated_get(dg)
    print("--- remaining cover overlaps: coplanar or true crossing? ---")
    for other in ["X5_56.002","X5_P04_Silver_Bezel_34.002","X5_1.002","X5_40.002"]:
        tB, bmB = tree(other)
        ov = tA.overlap(tB)
        if not ov: 
            print("  %-28s none" % other); continue
        # for each overlapping shell tri, measure angle between the two face normals
        bmB.faces.ensure_lookup_table()
        import math
        ang=[]
        for fa,fb in ov:
            na = bmA.faces[fa].normal; nb = bmB.faces[fb].normal
            d = max(-1.0,min(1.0, na.dot(nb)))
            a = math.degrees(math.acos(abs(d)))
            ang.append(a)
        ang.sort()
        copl = sum(1 for a in ang if a < 5.0)
        pts=[bmA.faces[fa].calc_center_median() for fa,_ in ov]
        px=[world_to_camera_view(sc,cam,p) for p in pts]
        xs=[p.x*1920 for p in px]; ys=[(1-p.y)*1080 for p in px]
        print("  %-28s tris=%4d  near-parallel(<5deg)=%4d (%.0f%%)  median angle %.1f deg  px x %.0f..%.0f y %.0f..%.0f" % (
            other, len(ov), copl, 100.0*copl/len(ov), ang[len(ang)//2], min(xs),max(xs),min(ys),max(ys)))
finally:
    win.scene = prev
