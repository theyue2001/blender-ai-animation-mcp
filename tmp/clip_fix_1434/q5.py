import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sc = bpy.data.scenes["SCN_P05_XRAY_MECHANISM"]
win = bpy.context.window; prev = win.scene
try:
    win.scene = sc; sc.frame_set(1434)
    dg = bpy.context.evaluated_depsgraph_get()
    cam = sc.camera
    mw = cam.evaluated_get(dg).matrix_world
    inv = mw.inverted()
    fr = cam.data.view_frame(scene=sc); tr,br,bl,tl = fr
    def to_px(p):
        pc = inv @ p
        if pc.z >= -1e-6: return None
        s = -1.0/pc.z
        x, y = pc.x*s, pc.y*s
        u = (x - tl.x)/(tr.x - tl.x)
        v = (tl.y - y)/(tl.y - bl.y)
        return (u*1920.0, v*1080.0)

    names = ["X5_16_0.002","X5_61.002","X5_10.002","X5_2.002","X5_1.002","X5_4.002","X5_8.002",
             "X5_56.002","X5_62.002","X5_40.002","X5_32.002","X5_38_0.002","X5_P04_Silver_Bezel_34.002",
             "X5_12.002","X5_6.002","X5_36_0.002"]
    trees = {}
    for n in names:
        o = sc.objects[n]
        oe = o.evaluated_get(dg)
        bm = bmesh.new(); bm.from_mesh(oe.data)
        bm.transform(oe.matrix_world)
        bmesh.ops.triangulate(bm, faces=bm.faces)
        trees[n] = (BVHTree.FromBMesh(bm), bm)
    L=[]
    for i in range(len(names)):
        for j in range(i+1, len(names)):
            a,b = names[i], names[j]
            ov = trees[a][0].overlap(trees[b][0])
            if not ov: continue
            # centroids of overlapping tris on A, in pixels
            bmA = trees[a][1]; bmA.faces.ensure_lookup_table()
            pts=[]
            for fa, fb in ov:
                f = bmA.faces[fa]
                c = f.calc_center_median()
                px = to_px(c)
                if px: pts.append((px, c))
            inreg = [p for p in pts if 1100 < p[0][0] < 1800 and 0 < p[0][1] < 620]
            zs = [c.z for _,c in pts]
            L.append("%-30s x %-30s tris=%5d  inUpperRight=%4d  world Z %.3f..%.3f" % (
                a.replace("X5_",""), b.replace("X5_",""), len(ov), len(inreg),
                min(zs) if zs else 0, max(zs) if zs else 0))
    print("\n".join(L) if L else "no overlaps")
finally:
    win.scene = prev
