import bpy, math
from mathutils import Vector
src=bpy.data.scenes["SCN_P05_XRAY_MECHANISM"]
win=bpy.context.window; prev=win.scene
try:
    win.scene=src; src.frame_set(1080)     # rest pose
    dg=bpy.context.evaluated_depsgraph_get()
    o=src.objects["X5_8.002"].evaluated_get(dg); me=o.data; mw=o.matrix_world
    P=[mw@v.co for v in me.vertices]
    AX,AY=0.0493,-0.3201
    cx=sum(p.x for p in P)/len(P); cy=sum(p.y for p in P)/len(P)
    print("8.002 centroid = (%.4f, %.4f)   motor axis = (%.4f, %.4f)  offset=%.4f" % (
        cx,cy,AX,AY, math.hypot(cx-AX,cy-AY)))
    def hist(px,py,label):
        rs=sorted(math.hypot(p.x-px,p.y-py) for p in P)
        n=len(rs)
        # how concentrated are the outermost 15% of points? (the teeth)
        outer=rs[int(.85*n):]
        spread=outer[-1]-outer[0]
        print("  about %-12s r %.4f..%.4f   outer-15%% band width = %.4f" % (label, rs[0],rs[-1],spread))
        return spread
    s_axis = hist(AX,AY,"MOTOR AXIS")
    s_own  = hist(cx,cy,"OWN CENTRE")
    print("  => teeth are concentric with:", "MOTOR AXIS (sector gear on the crank)" if s_axis<s_own else "ITS OWN CENTRE (separate pinion)")
    # angular extent about whichever centre
    px,py = (AX,AY) if s_axis<s_own else (cx,cy)
    angs=sorted(math.degrees(math.atan2(p.y-py,p.x-px)) for p in P)
    print("  angular extent about that centre: %.1f .. %.1f deg (span %.1f)" % (angs[0],angs[-1],angs[-1]-angs[0]))
    # z of 8.002
    print("  z %.4f..%.4f" % (min(p.z for p in P), max(p.z for p in P)))
    # where is the body wall closest to the axis? (min radius of 1.002's outer surface per angle)
    o1=src.objects["X5_1.002"].evaluated_get(dg); mw1=o1.matrix_world
    Q=[mw1@v.co for v in o1.data.vertices]
    import collections
    bins=collections.defaultdict(list)
    for p in Q:
        if 0.21 <= p.z <= 0.29:
            a=int(math.degrees(math.atan2(p.y-AY,p.x-AX))//10*10)
            bins[a].append(math.hypot(p.x-AX,p.y-AY))
    print("  1.002 wall max-radius per 10deg sector (z 0.21-0.29):")
    ks=sorted(bins)
    line=""
    for k in ks:
        line += "%4d:%.3f  " % (k, max(bins[k]))
        if len(line)>92: print("     "+line); line=""
    if line: print("     "+line)
finally:
    src.frame_set(1434); win.scene=prev
