import bpy, bmesh, json, math, os
import numpy as np
from mathutils import Vector, kdtree
from mathutils.bvhtree import BVHTree

DELTA, R = 0.0035, 0.050
ZFULL, ZZERO = 0.45, 0.35
CELL = 0.0020
OUT = r"d:\接案\26_0825_紅犀牛3D動畫\VScode\tmp\clip_fix_1434"
sc = bpy.data.scenes["SCN_P05_XRAY_MECHANISM"]
win = bpy.context.window; prev = win.scene
log=[]
try:
    win.scene = sc; sc.frame_set(1434)
    sh = sc.objects["X5_16_0.002"]; me = sh.data; mw = sh.matrix_world
    # ---- 1. revert to the pristine coordinates ----
    orig = json.load(open(os.path.join(OUT,"vert_backup.json")))["coords"]
    for k,co in orig.items(): me.vertices[int(k)].co = co
    me.update(); log.append("reverted %d verts to original" % len(orig))

    dg = bpy.context.evaluated_depsgraph_get()
    ae = sc.objects["X5_61.002"].evaluated_get(dg)
    bm = bmesh.new(); bm.from_mesh(ae.data); bm.transform(ae.matrix_world)
    bmesh.ops.triangulate(bm, faces=bm.faces); T_arm = BVHTree.FromBMesh(bm); bm.free()
    UP = Vector((0,0,1))

    # ---- 2. contact footprint ----
    contact=[]
    for v in me.vertices:
        wp = mw @ v.co
        if wp.z < 0.40: continue
        r = T_arm.ray_cast(wp+Vector((0,0,1e-5)), UP, 0.30)
        if r[0] is not None and (r[0].z - wp.z) < 0.002: contact.append((wp.x, wp.y))
    log.append("contact verts: %d" % len(contact))

    # ---- 3. rasterise + close + fill holes so the knob bore counts as inside ----
    cx = np.array([p[0] for p in contact]); cy = np.array([p[1] for p in contact])
    PAD = 8
    x0, y0 = cx.min()-PAD*CELL, cy.min()-PAD*CELL
    nx = int((cx.max()-x0)/CELL)+PAD+2; ny = int((cy.max()-y0)/CELL)+PAD+2
    occ = np.zeros((nx,ny), bool)
    occ[((cx-x0)/CELL).astype(int), ((cy-y0)/CELL).astype(int)] = True
    def dilate(m, k):
        o = m.copy()
        for _ in range(k):
            p = np.zeros_like(o)
            p[1:,:] |= o[:-1,:]; p[:-1,:] |= o[1:,:]
            p[:,1:] |= o[:,:-1]; p[:,:-1] |= o[:,1:]
            o = o | p
        return o
    def erode(m, k): return ~dilate(~m, k)
    closed = erode(dilate(occ, 4), 4)
    # flood fill background from the border -> anything unreached is an interior hole
    outside = np.zeros_like(closed); free = ~closed
    stack = [(i,0) for i in range(nx) if free[i,0]] + [(i,ny-1) for i in range(nx) if free[i,ny-1]] \
          + [(0,j) for j in range(ny) if free[0,j]] + [(nx-1,j) for j in range(ny) if free[nx-1,j]]
    for i,j in stack: outside[i,j] = True
    while stack:
        i,j = stack.pop()
        for di,dj in ((1,0),(-1,0),(0,1),(0,-1)):
            a,b = i+di, j+dj
            if 0<=a<nx and 0<=b<ny and free[a,b] and not outside[a,b]:
                outside[a,b] = True; stack.append((a,b))
    filled = closed | (~outside & ~closed)
    log.append("footprint cells: raw %d -> closed %d -> hole-filled %d" % (occ.sum(), closed.sum(), filled.sum()))

    fi, fj = np.nonzero(filled)
    kd = kdtree.KDTree(len(fi))
    for n,(i,j) in enumerate(zip(fi,fj)):
        kd.insert(Vector((x0+(i+0.5)*CELL, y0+(j+0.5)*CELL, 0.0)), n)
    kd.balance()

    def smoothstep(t):
        t = min(1.0,max(0.0,t)); return t*t*(3.0-2.0*t)
    s_scale = mw[2][1]
    backup={}; moved=0; mx=0.0
    for v in me.vertices:
        wp = mw @ v.co
        if wp.z <= ZZERO: continue
        _,_,d = kd.find(Vector((wp.x, wp.y, 0.0)))
        d = max(0.0, d - CELL*0.7071)      # inside a filled cell -> 0
        if d >= R: continue
        disp = DELTA * (1.0-smoothstep(d/R)) * smoothstep((wp.z-ZZERO)/(ZFULL-ZZERO))
        if disp <= 1e-7: continue
        backup[str(v.index)] = [v.co.x, v.co.y, v.co.z]
        v.co.y -= disp/s_scale
        moved+=1; mx=max(mx,disp)
    me.update()
    log.append("v2: moved %d verts, max world disp %.5f" % (moved, mx))
    merged = dict(orig); merged.update(backup)
    json.dump(dict(object="X5_16_0.002", mesh=me.name, delta=DELTA, R=R, cell=CELL, coords=merged),
              open(os.path.join(OUT,"vert_backup.json"),"w"))
    log.append("merged original-coord backup: %d verts" % len(merged))
finally:
    win.scene = prev
print("\n".join(log))
