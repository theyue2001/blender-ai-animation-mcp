import bpy, math, collections
from mathutils import Vector
import bmesh
from mathutils.bvhtree import BVHTree
src=bpy.data.scenes["SCN_P05_XRAY_MECHANISM"]
win=bpy.context.window; prev=win.scene
try:
    win.scene=src; src.frame_set(1080)
    dg=bpy.context.evaluated_depsgraph_get()
    def teeth(name, cx, cy, zlo, zhi):
        o=src.objects[name].evaluated_get(dg); mw=o.matrix_world
        P=[mw@v.co for v in o.data.vertices]
        P=[p for p in P if zlo<=p.z<=zhi]
        if not P: return None
        rs=sorted(math.hypot(p.x-cx,p.y-cy) for p in P)
        rtip=rs[-1]
        tips=[p for p in P if math.hypot(p.x-cx,p.y-cy) > rtip*0.985]
        angs=sorted(math.degrees(math.atan2(p.y-cy,p.x-cx))%360 for p in tips)
        # cluster angles
        clusters=1
        for i in range(1,len(angs)):
            if angs[i]-angs[i-1] > 3.0: clusters+=1
        if angs and (angs[0]+360-angs[-1])<=3.0 and clusters>1: clusters-=1
        return rtip, len(tips), clusters
    print("=== gear metrology (rest pose) ===")
    r8=teeth("X5_8.002", 0.0493,-0.4501, 0.213,0.290)
    r6=teeth("X5_6.002", 0.0493,-0.3201, 0.220,0.293)
    r4=teeth("X5_4.002", 0.0493,-0.3201, 0.112,0.250)
    for n,r in (("8.002 (pinion)",r8),("6.002 (on motor axis)",r6),("4.002 (crank web)",r4)):
        print("   %-24s tip radius %.4f  tip verts %d  tooth clusters ~%s" % (n, r[0], r[1], r[2]) if r else n)
    C = math.hypot(0.0493-0.0493, -0.4501+0.3201)
    print("   centre distance 6.002<->8.002 = %.4f" % C)
    if r6 and r8:
        m=(r6[0]+r8[0]-C)/2.0
        print("   implied module m=%.5f -> N6=%.1f  N8=%.1f  ratio=%.4f" % (
            m, 2*r6[0]/m-2, 2*r8[0]/m-2, (2*r6[0]/m-2)/(2*r8[0]/m-2)))
    print()
    print("=== rest-pose collisions of 8.002 ===")
    def tb(n):
        oe=src.objects[n].evaluated_get(dg)
        bm=bmesh.new(); bm.from_mesh(oe.data); bm.transform(oe.matrix_world)
        bmesh.ops.triangulate(bm,faces=bm.faces); t=BVHTree.FromBMesh(bm); bm.free(); return t
    T8=tb("X5_8.002")
    for n in ["X5_1.002","X5_2.002","X5_4.002","X5_6.002","X5_10.002","X5_12.002","X5_16_0.002"]:
        print("   8.002 x %-12s %d tris" % (n.replace("X5_",""), len(T8.overlap(tb(n)))))
    ms=src.objects["X5_MOTOR_SPIN"]
    print()
    print("=== MOTOR_SPIN rest matrix ===")
    print("   loc=%s rot=%s scale=%s parent=%s" % (tuple(round(v,5) for v in ms.location),
          tuple(round(math.degrees(v),3) for v in ms.rotation_euler),
          tuple(round(v,5) for v in ms.scale), ms.parent))
    o8=src.objects["X5_8.002"]
    print("   X5_8.002 basis loc=%s rot=%s scale=%s" % (tuple(round(v,5) for v in o8.location),
          tuple(round(math.degrees(v),3) for v in o8.rotation_euler), tuple(round(v,6) for v in o8.scale)))
    print("   X5_8.002 matrix_parent_inverse:")
    for r in o8.matrix_parent_inverse: print("     ", tuple(round(v,6) for v in r))
    # full motor spin curve
    act=ms.animation_data.action
    for fc in act.fcurves:
        if fc.data_path=="rotation_euler" and fc.array_index==2:
            ks=fc.keyframe_points
            print("   MOTOR_SPIN rot_z keys: n=%d  first=(%d, %.2f deg)  last=(%d, %.2f deg)" % (
                len(ks), ks[0].co[0], math.degrees(ks[0].co[1]), ks[-1].co[0], math.degrees(ks[-1].co[1])))
            print("   extrapolation=%s  interp of first key=%s" % (fc.extrapolation, ks[0].interpolation))
finally:
    src.frame_set(1434); win.scene=prev
