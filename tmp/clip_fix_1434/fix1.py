import bpy, bmesh, json, math
from mathutils import Vector, kdtree
from mathutils.bvhtree import BVHTree

DELTA = 0.0035      # world units of gap to open  (~0.48 mm at 1u = 137.4 mm)
R     = 0.050       # world feather radius
ZFULL, ZZERO = 0.45, 0.35   # safety vertical fade (nothing below 0.35 moves)
OUT = r"d:\接案\26_0825_紅犀牛3D動畫\VScode\tmp\clip_fix_1434"

sc = bpy.data.scenes["SCN_P05_XRAY_MECHANISM"]
win = bpy.context.window; prev = win.scene
try:
    win.scene = sc; sc.frame_set(1434)
    dg = bpy.context.evaluated_depsgraph_get()
    sh  = sc.objects["X5_16_0.002"]
    arm = sc.objects["X5_61.002"]

    # ---- arm underside BVH (world) ----
    ae = arm.evaluated_get(dg)
    bm = bmesh.new(); bm.from_mesh(ae.data); bm.transform(ae.matrix_world)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    T_arm = BVHTree.FromBMesh(bm); bm.free()

    # ---- isolate mesh so other scenes stay untouched ----
    old_mesh = sh.data
    slot_links = [s.link for s in sh.material_slots]
    slot_mats  = [(s.link, s.material.name if s.material else None) for s in sh.material_slots]
    if old_mesh.users > 1:
        sh.data = old_mesh.copy()
        sh.data.name = "mesh.011_P05_ARMGAP"
        for i, s in enumerate(sh.material_slots):
            s.link = slot_links[i]
    me = sh.data
    report = ["mesh was %s (users %d) -> now %s (users %d)" % (old_mesh.name, old_mesh.users, me.name, me.users)]
    report.append("material slots after copy: %s" % [(s.link, s.material.name if s.material else None) for s in sh.material_slots])
    report.append("has_custom_normals=%s" % me.has_custom_normals)

    mw = sh.matrix_world
    UP = Vector((0,0,1))

    # ---- find contact footprint on the shell ----
    contact = []
    for v in me.vertices:
        wp = mw @ v.co
        if wp.z < 0.40: continue
        r = T_arm.ray_cast(wp + Vector((0,0,1e-5)), UP, 0.30)
        if r[0] is not None and (r[0].z - wp.z) < 0.002:
            contact.append(wp)
    report.append("contact footprint verts: %d" % len(contact))

    kd = kdtree.KDTree(len(contact))
    for i, p in enumerate(contact):
        kd.insert(Vector((p.x, p.y, 0.0)), i)
    kd.balance()

    # ---- displacement: world -Z  ==  local -Y  (matrix row2 = (0, s, 0, tz)) ----
    s_scale = mw[2][1]                    # 0.006636
    report.append("world_z = %.6f * local_y + %.6f" % (s_scale, mw[2][3]))

    def smoothstep(t):
        t = min(1.0, max(0.0, t)); return t*t*(3.0-2.0*t)

    backup = {}
    moved = 0; maxmove = 0.0
    for v in me.vertices:
        wp = mw @ v.co
        if wp.z <= ZZERO: continue
        _, _, d = kd.find(Vector((wp.x, wp.y, 0.0)))
        if d is None or d >= R: continue
        w  = 1.0 - smoothstep(d / R)
        wz = smoothstep((wp.z - ZZERO) / (ZFULL - ZZERO))
        disp = DELTA * w * wz
        if disp <= 1e-7: continue
        backup[str(v.index)] = [v.co.x, v.co.y, v.co.z]
        v.co.y -= disp / s_scale          # local -Y  ==  world -Z
        moved += 1; maxmove = max(maxmove, disp)
    me.update()
    report.append("vertices moved: %d   max world displacement: %.5f" % (moved, maxmove))

    json.dump(dict(object="X5_16_0.002", mesh=me.name, delta=DELTA, R=R,
                   coords=backup), open(OUT + r"\vert_backup.json","w"))
    report.append("backup written: vert_backup.json (%d verts)" % len(backup))
    print("\n".join(report))
finally:
    win.scene = prev
