import bpy, bmesh, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
sc = bpy.data.scenes["SCN_P05_XRAY_MECHANISM"]
win = bpy.context.window; prev = win.scene
try:
    win.scene = sc; sc.frame_set(1434)
    dg = bpy.context.evaluated_depsgraph_get()
    cam = sc.camera.evaluated_get(dg)
    print("view_frame:", [tuple(round(v,4) for v in p) for p in sc.camera.data.view_frame(scene=sc)])
    print("cam matrix_world translation", tuple(round(v,4) for v in cam.matrix_world.translation))
    RX, RY = 1920.0, 1080.0
    def to_px(p):
        co = world_to_camera_view(sc, cam, p)
        return (co.x*RX, (1.0-co.y)*RY, co.z)
    def tree(n):
        oe = sc.objects[n].evaluated_get(dg)
        bm = bmesh.new(); bm.from_mesh(oe.data); bm.transform(oe.matrix_world)
        bmesh.ops.triangulate(bm, faces=bm.faces); bm.faces.ensure_lookup_table()
        return BVHTree.FromBMesh(bm), bm
    tA, bmA = tree("X5_16_0.002")
    out={}
    for other in ["X5_61.002","X5_56.002","X5_P04_Silver_Bezel_34.002","X5_1.002","X5_40.002"]:
        tB, bmB = tree(other)
        ov = tA.overlap(tB)
        pts=[]
        for fa,fb in ov:
            c = bmA.faces[fa].calc_center_median()
            px = to_px(c)
            pts.append([round(px[0],1), round(px[1],1)])
        xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
        out[other]=dict(n=len(ov), pts=pts[:6000])
        print("%-28s n=%5d  px x %.0f..%.0f  y %.0f..%.0f" % (other, len(ov), min(xs),max(xs),min(ys),max(ys)))
    json.dump(out, open(r"d:\接案\26_0825_紅犀牛3D動畫\VScode\tmp\clip_fix_1434\overlap2.json","w"))
finally:
    win.scene = prev
