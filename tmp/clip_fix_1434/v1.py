import bpy, bmesh, json
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
    T = {n: tree(n) for n in ["X5_16_0.002","X5_61.002","X5_56.002","X5_62.002","X5_10.002",
                              "X5_2.002","X5_1.002","X5_40.002","X5_P04_Silver_Bezel_34.002","X5_32.002"]}
    print("--- overlaps with the cover after fix ---")
    for n,t in T.items():
        if n == "X5_16_0.002": continue
        ov = T["X5_16_0.002"].overlap(t)
        print("  X5_16_0.002 x %-28s tris=%d" % (n, len(ov)))
    # gap scan
    UP = Vector((0,0,1)); DOWN = Vector((0,0,-1))
    N=96; X0,X1,Y0,Y1 = -0.20,0.30,-0.62,-0.10
    grid=[]; vals=[]
    for iy in range(N):
        y = Y0+(Y1-Y0)*iy/(N-1); row=[]
        for ix in range(N):
            x = X0+(X1-X0)*ix/(N-1)
            rs = T["X5_16_0.002"].ray_cast(Vector((x,y,1.2)), DOWN)
            ra = T["X5_61.002"].ray_cast(Vector((x,y,0.20)), UP)
            if rs[0] is None or ra[0] is None: row.append(None)
            else:
                g = ra[0].z - rs[0].z; row.append(round(g,5)); vals.append(g)
        grid.append(row)
    json.dump(dict(N=N,X0=X0,X1=X1,Y0=Y0,Y1=Y1,grid=grid),
              open(r"d:\接案\26_0825_紅犀牛3D動畫\VScode\tmp\clip_fix_1434\gap_grid_after.json","w"))
    print("--- vertical gap arm-underside to cover ---")
    print("  cells=%d  min=%.5f  <0.0008: %d  0.0008-0.003: %d  >=0.003: %d" % (
        len(vals), min(vals), sum(1 for v in vals if v<0.0008),
        sum(1 for v in vals if 0.0008<=v<0.003), sum(1 for v in vals if v>=0.003)))
    # clearance to internals below the cover roof
    sh = sc.objects["X5_16_0.002"]; mw = sh.matrix_world
    worst = 9e9; wl=None
    for (x,y) in [(0.05,-0.30),(0.05,-0.20),(-0.05,-0.35),(0.15,-0.30),(0.05,-0.45),(0.10,-0.25),(0.0,-0.25)]:
        o=Vector((x,y,1.2)); hits=[]
        for k in range(6):
            r=T["X5_16_0.002"].ray_cast(o,DOWN)
            if r[0] is None: break
            hits.append(r[0].z); o=r[0]+DOWN*1e-5
        inner = hits[1] if len(hits)>1 else None
        rc = T["X5_10.002"].ray_cast(Vector((x,y,0.52)),DOWN)
        can = rc[0].z if rc[0] is not None else None
        if inner is not None and can is not None:
            gap = inner-can
            if gap < worst: worst, wl = gap, (x,y)
            print("  (%.2f,%.2f) cover inner roof %.4f  motor can top %.4f  gap %.4f" % (x,y,inner,can,gap))
    print("  worst cover-inner / motor-can gap: %.4f at %s" % (worst, wl))
    print("  wall thickness check:", ["%.4f"%(h) for h in []])
finally:
    win.scene = prev
