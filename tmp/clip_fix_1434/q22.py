import bpy, bmesh, math, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
sc = bpy.data.scenes["SCN_P05_XRAY_MECHANISM"]
win=bpy.context.window; prev=win.scene
try:
    win.scene=sc; sc.frame_set(1434)
    dg=bpy.context.evaluated_depsgraph_get(); cam=sc.camera.evaluated_get(dg)
    def tb(n):
        oe=sc.objects[n].evaluated_get(dg)
        bm=bmesh.new(); bm.from_mesh(oe.data); bm.transform(oe.matrix_world)
        bmesh.ops.triangulate(bm,faces=bm.faces); bm.faces.ensure_lookup_table()
        return BVHTree.FromBMesh(bm), bm
    out={}
    for a,b in [("X5_2.002","X5_10.002"),("X5_1.002","X5_2.002"),("X5_4.002","X5_12.002"),("X5_6.002","X5_10.002")]:
        TA,bmA=tb(a); TB,bmB=tb(b)
        ov=TA.overlap(TB)
        pts=[]; copl=[]
        for fa,fb in ov:
            f=bmA.faces[fa]; c=f.calc_center_median()
            co=world_to_camera_view(sc,cam,c)
            d=max(-1.0,min(1.0,f.normal.normalized().dot(bmB.faces[fb].normal.normalized())))
            ang=math.degrees(math.acos(abs(d)))
            pts.append([round(co.x*1920,1),round((1-co.y)*1080,1)])
            if ang<5.0: copl.append((c.copy(), f.normal.copy()))
        xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
        out["%s|%s"%(a,b)]=pts[:8000]
        print("%s x %s : %d tris, px x %.0f..%.0f y %.0f..%.0f" % (a,b,len(ov),min(xs),max(xs),min(ys),max(ys)))
        if copl:
            # orientation of the coplanar contact
            nz=[abs(n.z) for _,n in copl]
            cz=[c.z for c,_ in copl]
            rad=[math.hypot(c.x-0.0493, c.y+0.3201) for c,_ in copl]
            horiz=sum(1 for v in nz if v>0.9); vert=sum(1 for v in nz if v<0.1)
            print("    coplanar %d: normal|z|>0.9 (horizontal face) %d, |z|<0.1 (vertical wall) %d" % (len(copl),horiz,vert))
            print("    coplanar world Z %.4f..%.4f   radius-from-motor-axis %.4f..%.4f" % (min(cz),max(cz),min(rad),max(rad)))
    json.dump(out, open(r"d:\接案\26_0825_紅犀牛3D動畫\VScode\tmp\clip_fix_1434\ov2.json","w"))
finally:
    win.scene=prev
