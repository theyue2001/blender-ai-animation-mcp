import bpy
from mathutils import Vector
sc = bpy.data.scenes["SCN_P05_XRAY_MECHANISM"]
win = bpy.context.window
prev = win.scene
try:
    win.scene = sc
    sc.frame_set(1434)
    dg = bpy.context.evaluated_depsgraph_get()
    cam = sc.camera
    mw = cam.evaluated_get(dg).matrix_world
    # camera view frame in camera space at depth 1
    fr = cam.data.view_frame(scene=sc)   # 4 corners, order: TR, BR, BL, TL
    tr, br, bl, tl = fr
    org = mw.translation
    RES = 1920, 1080
    # region of interest in the 960x540 crop coords -> normalized
    # crop box was (590,10,920,340) in 960x540
    import itertools
    pts = []
    N = 11
    for iy in range(N):
        for ix in range(N):
            u = (590 + 330*ix/(N-1)) / 960.0
            v = (10  + 330*iy/(N-1)) / 540.0
            # u: 0..1 left->right ; v: 0..1 top->bottom
            top = tl.lerp(tr, u)
            bot = bl.lerp(br, u)
            p_cam = top.lerp(bot, v)
            p_world = mw @ p_cam
            d = (p_world - org).normalized()
            pts.append((ix, iy, u, v, d))
    from collections import Counter
    seq = {}
    for ix, iy, u, v, d in pts:
        o = org.copy()
        chain = []
        for k in range(8):
            hit, loc, nor, idx, obj, m = sc.ray_cast(dg, o, d)
            if not hit: break
            chain.append((obj.name, (loc-org).length))
            o = loc + d*1e-4
        seq[(ix,iy)] = chain
    # summarize
    L=[]
    for iy in range(N):
        row=[]
        for ix in range(N):
            c = seq[(ix,iy)]
            row.append(c[0][0].replace("X5_","") if c else "-")
        L.append("y%02d " % iy + " | ".join("%-14s"%r for r in row))
    print("\n".join(L))
    print()
    cnt = Counter()
    for c in seq.values():
        for n,_ in c: cnt[n]+=1
    print("ALL HIT OBJECTS in region:", cnt.most_common())
finally:
    win.scene = prev
