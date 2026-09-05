import bpy, bmesh, json, math, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OUT = r"d:\接案\26_0825_紅犀牛3D動畫\VScode\tmp\clip_fix_1434"
sc = bpy.data.scenes["SCN_P05_XRAY_MECHANISM"]
win=bpy.context.window; prev=win.scene
try:
    win.scene=sc; sc.frame_set(1434)
    dg = bpy.context.evaluated_depsgraph_get()
    def tree(n):
        oe = sc.objects[n].evaluated_get(dg)
        bm=bmesh.new(); bm.from_mesh(oe.data); bm.transform(oe.matrix_world)
        bmesh.ops.triangulate(bm,faces=bm.faces); t=BVHTree.FromBMesh(bm); bm.free(); return t
    T_arm=tree("X5_61.002"); T_sh=tree("X5_16_0.002")
    print("cover x arm intersecting triangle pairs: %d" % len(T_sh.overlap(T_arm)))
    ob=sc.objects["X5_16_0.002"]; me=ob.data; mw=ob.matrix_world; UP=Vector((0,0,1))
    cl=[]
    for v in me.vertices:
        wp=mw@v.co
        if wp.z<0.40: continue
        r=T_arm.ray_cast(wp+Vector((0,0,1e-5)),UP,0.30)
        if r[0] is not None: cl.append(r[0].z-wp.z)
    cl.sort()
    print("clearance over %d verts: min %.5f  p01 %.5f  p05 %.5f  median %.5f" % (
        len(cl), cl[0], cl[int(.01*len(cl))], cl[int(.05*len(cl))], cl[len(cl)//2]))
    print("   <0.0005: %d   <0.001: %d   <0.002: %d" % (
        sum(1 for c in cl if c<0.0005), sum(1 for c in cl if c<0.001), sum(1 for c in cl if c<0.002)))
    # normal rotation vs original
    bk={int(k):Vector(v) for k,v in json.load(open(os.path.join(OUT,"vert_backup.json")))["coords"].items()}
    def newell(pts):
        n=Vector((0,0,0))
        for i in range(len(pts)):
            a=pts[i]; b=pts[(i+1)%len(pts)]
            n.x+=(a.y-b.y)*(a.z+b.z); n.y+=(a.z-b.z)*(a.x+b.x); n.z+=(a.x-b.x)*(a.y+b.y)
        return n
    angs=[]
    for p in me.polygons:
        vs=list(p.vertices)
        if not any(v in bk for v in vs): continue
        na=newell([me.vertices[v].co for v in vs]); nb=newell([bk.get(v,me.vertices[v].co) for v in vs])
        if na.length<1e-12 or nb.length<1e-12: continue
        d=max(-1.0,min(1.0,na.normalized().dot(nb.normalized())))
        angs.append(math.degrees(math.acos(d)))
    angs.sort()
    print("face-normal rotation: n=%d  median %.3f  p95 %.3f  p99 %.3f  max %.3f" % (
        len(angs), angs[len(angs)//2], angs[int(.95*len(angs))], angs[int(.99*len(angs))], angs[-1]))
    for t in (2.0,5.0,10.0):
        print("   > %.0f deg: %d (%.2f%%)" % (t, sum(1 for a in angs if a>t), 100.0*sum(1 for a in angs if a>t)/len(angs)))
    # wall thickness
    DOWN=Vector((0,0,-1))
    for (x,y) in [(0.05,-0.20),(-0.05,-0.35),(0.15,-0.30),(0.05,-0.45),(0.10,-0.25)]:
        o=Vector((x,y,1.2)); hits=[]
        for k in range(4):
            r=T_sh.ray_cast(o,DOWN)
            if r[0] is None: break
            hits.append(r[0].z); o=r[0]+DOWN*1e-5
        if len(hits)>1: print("   thickness (%.2f,%.2f): %.4f" % (x,y,hits[0]-hits[1]))
finally:
    win.scene=prev
