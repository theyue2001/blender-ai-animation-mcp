import bpy, bmesh, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sc = bpy.data.scenes["SCN_P05_XRAY_MECHANISM"]
win = bpy.context.window; prev = win.scene
try:
    win.scene = sc; sc.frame_set(1434)
    dg = bpy.context.evaluated_depsgraph_get()
    cam = sc.camera; mw = cam.evaluated_get(dg).matrix_world; inv = mw.inverted()
    tr,br,bl,tl = cam.data.view_frame(scene=sc)
    def to_px(p):
        pc = inv @ p
        if pc.z >= -1e-6: return None
        s = -1.0/pc.z; x,y = pc.x*s, pc.y*s
        return ((x-tl.x)/(tr.x-tl.x)*1920.0, (tl.y-y)/(tl.y-bl.y)*1080.0)
    def tree(n):
        oe = sc.objects[n].evaluated_get(dg)
        bm = bmesh.new(); bm.from_mesh(oe.data); bm.transform(oe.matrix_world)
        bmesh.ops.triangulate(bm, faces=bm.faces); bm.faces.ensure_lookup_table()
        return BVHTree.FromBMesh(bm), bm
    tA, bmA = tree("X5_16_0.002")
    out = {}
    for other in ["X5_61.002","X5_56.002"]:
        tB, bmB = tree(other)
        ov = tA.overlap(tB)
        pts=[]; wpts=[]
        for fa,fb in ov:
            c = bmA.faces[fa].calc_center_median()
            px = to_px(c)
            if px: pts.append([round(px[0],1), round(px[1],1)])
            wpts.append([round(c.x,4), round(c.y,4), round(c.z,4)])
        xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
        wx=[p[0] for p in wpts]; wy=[p[1] for p in wpts]; wz=[p[2] for p in wpts]
        out[other] = dict(n=len(ov), px_bbox=[min(xs),min(ys),max(xs),max(ys)],
                          world_bbox=[min(wx),min(wy),min(wz),max(wx),max(wy),max(wz)], pts=pts[:4000])
        print("%s  n=%d  px=[%.0f,%.0f]-[%.0f,%.0f]  world X %.3f..%.3f Y %.3f..%.3f Z %.3f..%.3f" % (
            other, len(ov), min(xs),min(ys),max(xs),max(ys), min(wx),max(wx),min(wy),max(wy),min(wz),max(wz)))
    with open(r"d:\接案\26_0825_紅犀牛3D動畫\VScode\tmp\clip_fix_1434\overlap.json","w") as f:
        json.dump(out, f)
finally:
    win.scene = prev
