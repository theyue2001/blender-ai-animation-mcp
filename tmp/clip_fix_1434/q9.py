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
    T_shell = tree("X5_16_0.002"); T_arm = tree("X5_61.002"); T_knob = tree("X5_56.002")
    DOWN = Vector((0,0,-1)); UP = Vector((0,0,1))
    N = 96
    X0,X1 = -0.20, 0.30
    Y0,Y1 = -0.62, -0.10
    grid = []
    for iy in range(N):
        y = Y0 + (Y1-Y0)*iy/(N-1)
        row=[]
        for ix in range(N):
            x = X0 + (X1-X0)*ix/(N-1)
            rs = T_shell.ray_cast(Vector((x,y,1.2)), DOWN)
            ra = T_arm.ray_cast(Vector((x,y,0.20)), UP)   # arm underside
            if rs[0] is None or ra[0] is None:
                row.append(None)
            else:
                row.append(round(ra[0].z - rs[0].z, 5))   # + = gap, - = shell pokes through arm
        grid.append(row)
    json.dump(dict(N=N, X0=X0,X1=X1,Y0=Y0,Y1=Y1, grid=grid),
              open(r"d:\接案\26_0825_紅犀牛3D動畫\VScode\tmp\clip_fix_1434\gap_grid.json","w"))
    vals=[v for r in grid for v in r if v is not None]
    import statistics
    neg=[v for v in vals if v < -0.0002]
    tiny=[v for v in vals if -0.0002 <= v <= 0.0008]
    print("cells with arm data: %d" % len(vals))
    print("shell POKES THROUGH arm (gap<-0.0002): %d cells, worst %.5f" % (len(neg), min(vals)))
    print("COINCIDENT (|gap|<=0.0008): %d cells" % len(tiny))
    print("gap>0.0008: %d cells, max %.4f" % (len([v for v in vals if v>0.0008]), max(vals)))
finally:
    win.scene = prev
