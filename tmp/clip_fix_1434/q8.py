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
    T_shell = tree("X5_16_0.002"); T_arm = tree("X5_61.002")
    DOWN = Vector((0,0,-1)); UP = Vector((0,0,1))
    def first_hit(T, org, d):
        r = T.ray_cast(org, d)
        return r[0].z if r[0] is not None else None
    print("  Y \ X      " + "".join("%8.3f"%x for x in [-0.14+0.05*i for i in range(9)]))
    rows=[]
    maxpen = 0.0; maxloc=None
    for iy in range(11):
        y = -0.56 + (0.42)*iy/10.0    # -0.56 .. -0.14
        cells=[]
        for ix in range(9):
            x = -0.14 + 0.05*ix
            p = Vector((x,y,1.2))
            sz = first_hit(T_shell, p, DOWN)
            az = first_hit(T_arm, p, DOWN)          # arm TOP
            # arm bottom: cast up from below the arm
            ab = None
            r = T_arm.ray_cast(Vector((x,y,0.30)), UP)
            if r[0] is not None: ab = r[0].z
            if sz is None or ab is None:
                cells.append("   .    ")
            else:
                pen = sz - ab
                cells.append("%8.4f"%pen)
                if pen > maxpen: maxpen, maxloc = pen, (x,y,sz,ab)
        rows.append("%7.3f  %s" % (y, "".join(cells)))
    print("\n".join(rows))
    print()
    print("max penetration (shellTopZ - armBottomZ) = %.4f at x=%.3f y=%.3f shellTop=%.4f armBottom=%.4f" % (
        maxpen, maxloc[0], maxloc[1], maxloc[2], maxloc[3]) if maxloc else "none")
finally:
    win.scene = prev
