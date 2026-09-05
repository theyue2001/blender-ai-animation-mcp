import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sc = bpy.data.scenes["SCN_P05_XRAY_MECHANISM"]
win=bpy.context.window; prev=win.scene
try:
    win.scene=sc; sc.frame_set(1434)
    dg=bpy.context.evaluated_depsgraph_get()
    def tree(n):
        oe=sc.objects[n].evaluated_get(dg)
        bm=bmesh.new(); bm.from_mesh(oe.data); bm.transform(oe.matrix_world)
        bmesh.ops.triangulate(bm,faces=bm.faces); t=BVHTree.FromBMesh(bm); bm.free(); return t
    print("file           :", bpy.data.filepath)
    print("unsaved changes:", bpy.data.is_dirty)
    print("cover mesh     :", sc.objects["X5_16_0.002"].data.name)
    print("cover x arm    :", len(tree("X5_16_0.002").overlap(tree("X5_61.002"))), "intersecting triangle pairs")
    T=tree("X5_61.002"); ob=sc.objects["X5_16_0.002"]; mw=ob.matrix_world; UP=Vector((0,0,1))
    cl=[]
    for v in ob.data.vertices:
        wp=mw@v.co
        if wp.z<0.40: continue
        r=T.ray_cast(wp+Vector((0,0,1e-5)),UP,0.30)
        if r[0] is not None: cl.append(r[0].z-wp.z)
    cl.sort()
    print("min gap        : %.5f world  (= %.3f mm at 1u=137.4mm)" % (cl[0], cl[0]*137.4))
    print("typical gap    : %.5f world  (= %.3f mm)" % (cl[int(.05*len(cl))], cl[int(.05*len(cl))]*137.4))
finally:
    win.scene=prev
