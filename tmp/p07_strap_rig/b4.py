import bpy, math
from mathutils import Vector, Matrix
SN = "05_SCN_P07_STRAP_RIG"
sc = bpy.data.scenes[SN]; vl = sc.view_layers[0]
rig = bpy.data.collections["P07_RIG"]
log = []

SB = [0.0, 0.048, 0.13, 0.25, 0.38, 0.51, 0.63, 0.74, 0.845, 0.925, 1.0]
CTL = [("ROOT", 0.0), ("MID1", 0.13), ("MID2", 0.28), ("MID", 0.43), ("MID3", 0.58),
       ("MID4", 0.72), ("BUCKLE", 0.845), ("ENTRY", 0.925), ("END", 1.0)]
HW_MIN, HW_MAX = 0.008, 0.045
BINS = 720

SPECS = [dict(obj="P07_STRAP_UPPER", tag="StrapUpper", C=(0.0589, -2.1837), root=112.0, span=360.0),
         dict(obj="P07_STRAP_LOWER", tag="StrapLower", C=(0.0455, -2.3473), root=110.0, span=320.0)]


def smoothstep(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


for S in SPECS:
    ob = bpy.data.objects[S["obj"]]; me = ob.data
    W = ob.matrix_world.copy(); Wi = W.inverted()
    C = S["C"]; root = S["root"]; span = S["span"]; tag = S["tag"]
    n = len(me.vertices); co = [0.0] * (n * 3); me.vertices.foreach_get("co", co)

    binw = span / BINS
    acc = [None] * BINS; cnt = [0] * BINS
    us = [0.0] * n
    for i in range(n):
        v = W @ Vector((co[3 * i], co[3 * i + 1], co[3 * i + 2]))
        a = math.degrees(math.atan2(v.y - C[1], v.x - C[0])) % 360.0
        u = (a - root) % 360.0
        us[i] = u
        b = int(u / binw)
        if 0 <= b < BINS:
            if acc[b] is None:
                acc[b] = Vector((0, 0, 0))
            acc[b] += v; cnt[b] += 1
    filled = [b for b in range(BINS) if cnt[b] > 0]
    pts = [acc[b] / cnt[b] for b in filled]
    K = 6; sm = []
    for j in range(len(pts)):
        a0 = max(0, j - K); a1 = min(len(pts), j + K + 1)
        sm.append(sum(pts[a0:a1], Vector((0, 0, 0))) / (a1 - a0))
    pts = sm
    cl = [0.0]
    for j in range(1, len(pts)):
        cl.append(cl[-1] + (pts[j] - pts[j - 1]).length)
    Lc = cl[-1]
    ub = [(filled[j] + 0.5) * binw for j in range(len(filled))]

    def u2s(u, ub=ub, cl=cl, Lc=Lc):
        if u <= ub[0]:
            return 0.0
        if u >= ub[-1]:
            return 1.0
        lo, hi = 0, len(ub) - 1
        while hi - lo > 1:
            m = (lo + hi) // 2
            if ub[m] <= u:
                lo = m
            else:
                hi = m
        f = (u - ub[lo]) / (ub[hi] - ub[lo])
        return (cl[lo] + f * (cl[hi] - cl[lo])) / Lc

    def at_s(s, pts=pts, cl=cl, Lc=Lc):
        t = max(0.0, min(1.0, s)) * Lc
        lo, hi = 0, len(cl) - 1
        while hi - lo > 1:
            m = (lo + hi) // 2
            if cl[m] <= t:
                lo = m
            else:
                hi = m
        d = cl[hi] - cl[lo]
        f = 0.0 if d < 1e-12 else (t - cl[lo]) / d
        return pts[lo].lerp(pts[hi], f)

    P = [at_s(s) for _, s in CTL]
    m = len(P); HR = [None] * m; HL = [None] * m
    for j in range(m):
        if j == 0:
            T = (P[1] - P[0])
        elif j == m - 1:
            T = (P[m - 1] - P[m - 2])
        else:
            T = (P[j + 1] - P[j - 1]) * 0.5
        dprev = (P[j] - P[j - 1]).length if j > 0 else T.length
        dnext = (P[j + 1] - P[j]).length if j < m - 1 else T.length
        Tn = T.normalized()
        HL[j] = P[j] - Tn * (dprev / 3.0)
        HR[j] = P[j] + Tn * (dnext / 3.0)

    def bez(p0, h0, h1, p1, t):
        mt = 1 - t
        return p0 * (mt ** 3) + h0 * (3 * mt * mt * t) + h1 * (3 * mt * t * t) + p1 * (t ** 3)

    dense = []
    for j in range(m - 1):
        for k in range(0, 120):
            dense.append(bez(P[j], HR[j], HL[j + 1], P[j + 1], k / 120.0))
    dense.append(P[-1])
    dl = [0.0]
    for j in range(1, len(dense)):
        dl.append(dl[-1] + (dense[j] - dense[j - 1]).length)
    Ld = dl[-1]

    def on_curve(f, dense=dense, dl=dl, Ld=Ld):
        t = max(0.0, min(1.0, f)) * Ld
        lo, hi = 0, len(dl) - 1
        while hi - lo > 1:
            k = (lo + hi) // 2
            if dl[k] <= t:
                lo = k
            else:
                hi = k
        d = dl[hi] - dl[lo]
        g = 0.0 if d < 1e-12 else (t - dl[lo]) / d
        return dense[lo].lerp(dense[hi], g)

    dev = max((on_curve(x / 200.0) - at_s(x / 200.0)).length for x in range(201))

    cuname = "CRV_" + tag + "_Path"
    cu = bpy.data.curves.new(cuname, 'CURVE'); cu.dimensions = '3D'; cu.resolution_u = 32
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(m - 1)
    for j, bp in enumerate(sp.bezier_points):
        bp.handle_left_type = 'FREE'; bp.handle_right_type = 'FREE'
        bp.co = Wi @ P[j]; bp.handle_left = Wi @ HL[j]; bp.handle_right = Wi @ HR[j]
    cuo = bpy.data.objects.new(cuname, cu); cuo.matrix_world = W
    rig.objects.link(cuo); cuo.hide_render = True

    aname = "NITE_" + tag + "_Armature"
    ad = bpy.data.armatures.new(aname); ao = bpy.data.objects.new(aname, ad)
    ao.matrix_world = W; rig.objects.link(ao); ao.show_in_front = True
    ad.display_type = 'OCTAHEDRAL'
    prev = bpy.context.window.scene
    try:
        bpy.context.window.scene = sc
        vl.objects.active = ao
        bpy.ops.object.mode_set(mode='EDIT')
        upl = (Wi.to_3x3() @ Vector((0, 0, 1))).normalized()
        CTLLEN = 27.0; MASTLEN = 55.0; CTLOFF = 14.0
        joints = [Wi @ on_curve(s) for s in SB]
        b = ad.edit_bones.new(tag + "_MASTER")
        b.head = joints[0] - upl * (MASTLEN * 0.25); b.tail = b.head + upl * MASTLEN
        b.use_deform = False
        master = b
        defb = []
        for i in range(len(SB) - 1):
            d = ad.edit_bones.new("DEF_%s_%02d" % (tag, i))
            d.head = joints[i]; d.tail = joints[i + 1]
            d.align_roll(upl); d.use_deform = True
            if i == 0:
                d.parent = master; d.use_connect = False
            else:
                d.parent = defb[-1]; d.use_connect = True
            defb.append(d)
        for cn, cs in CTL:
            p = Wi @ on_curve(cs)
            cb = ad.edit_bones.new("%s_%s_CTRL" % (tag, cn))
            cb.head = p + upl * CTLOFF; cb.tail = p + upl * (CTLOFF + CTLLEN)
            cb.use_deform = False; cb.parent = master; cb.use_connect = False
        bpy.ops.object.mode_set(mode='OBJECT')
        for cname in ("CTRL", "DEF"):
            if cname not in [c.name for c in ad.collections_all]:
                ad.collections.new(cname)
        for bn in list(ad.bones):
            tgt = "DEF" if bn.name.startswith("DEF_") else "CTRL"
            ad.collections[tgt].assign(ad.bones[bn.name])
            bn.color.palette = 'THEME03' if bn.name.startswith("DEF_") else 'THEME04'
        ad.collections["DEF"].is_visible = False
        ad.bones[tag + "_MASTER"].color.palette = 'THEME09'
        pb = ao.pose.bones["DEF_%s_%02d" % (tag, len(SB) - 2)]
        con = pb.constraints.new('SPLINE_IK')
        con.name = "SPLINE_IK_" + tag
        con.target = cuo; con.chain_count = len(SB) - 1
        con.y_scale_mode = 'BONE_ORIGINAL'; con.xz_scale_mode = 'NONE'
        con.use_curve_radius = False; con.use_even_divisions = False; con.use_chain_offset = False
    finally:
        bpy.context.window.scene = prev

    for j, (cn, cs) in enumerate(CTL):
        bname = "%s_%s_CTRL" % (tag, cn)
        h = cuo.modifiers.new("HOOK_" + cn, 'HOOK')
        h.object = ao; h.subtarget = bname
        h.falloff_type = 'NONE'; h.strength = 1.0
        h.matrix_inverse = ao.data.bones[bname].matrix_local.inverted()
        h.vertex_indices_set([3 * j, 3 * j + 1, 3 * j + 2])

    NB = len(SB) - 1
    for i in range(NB):
        gn = "DEF_%s_%02d" % (tag, i)
        if gn in ob.vertex_groups:
            ob.vertex_groups.remove(ob.vertex_groups[gn])
        ob.vertex_groups.new(name=gn)
    hw = []
    for j in range(1, NB):
        h = HW_MIN + (HW_MAX - HW_MIN) * SB[j]
        h = min(h, 0.45 * (SB[j] - SB[j - 1]), 0.45 * (SB[j + 1] - SB[j]))
        hw.append(h)
    buckets = [dict() for _ in range(NB)]
    for i in range(n):
        s = u2s(us[i])
        k = NB - 1
        for j in range(NB):
            if s < SB[j + 1]:
                k = j; break
        w = {k: 1.0}
        if k > 0 and s < SB[k] + hw[k - 1]:
            t = smoothstep((s - (SB[k] - hw[k - 1])) / (2 * hw[k - 1]))
            w = {k - 1: 1.0 - t, k: t}
        elif k < NB - 1 and s > SB[k + 1] - hw[k]:
            t = smoothstep((s - (SB[k + 1] - hw[k])) / (2 * hw[k]))
            w = {k: 1.0 - t, k + 1: t}
        for bi, wt in w.items():
            if wt <= 0.0005:
                continue
            buckets[bi].setdefault(round(wt, 3), []).append(i)
    for bi in range(NB):
        vg = ob.vertex_groups["DEF_%s_%02d" % (tag, bi)]
        for q, idxs in buckets[bi].items():
            vg.add(idxs, q, 'REPLACE')
    md = ob.modifiers.get("ARM_" + tag)
    if not md:
        md = ob.modifiers.new("ARM_" + tag, 'ARMATURE')
    md.object = ao; md.use_vertex_groups = True; md.use_bone_envelopes = False

    log.append("%s: centreline L=%.4f bins=%d | curveL=%.4f maxdev=%.5f | defbones=%d ctrls=%d verts=%d"
               % (tag, Lc, len(filled), Ld, dev, NB, len(CTL), n))
    log.append("   bone world lengths: %s" % ["%.3f" % ((SB[i + 1] - SB[i]) * Ld) for i in range(NB)])
    log.append("   blend halfwidths(s): %s" % ["%.4f" % x for x in hw])
print("\n".join(log))
