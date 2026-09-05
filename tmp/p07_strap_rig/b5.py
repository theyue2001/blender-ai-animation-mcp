import bpy, math
from mathutils import Vector, Matrix
SN = "05_SCN_P07_STRAP_RIG"
sc = bpy.data.scenes[SN]; vl = sc.view_layers[0]
rig = bpy.data.collections["P07_RIG"]
log = []

SB = [0.0, 0.048, 0.13, 0.25, 0.38, 0.51, 0.63, 0.74, 0.845, 0.925, 1.0]
CTL = [("ROOT", 0.0), ("SIDE_A", 0.10), ("BACK_A", 0.22), ("BACK_B", 0.34), ("MID", 0.46),
       ("BACK_C", 0.58), ("SIDE_B", 0.70), ("BUCKLE", 0.815), ("ENTRY", 0.905), ("END", 1.0)]
HW_MIN, HW_MAX = 0.008, 0.045
BINS = 720

SPECS = [dict(obj="P07_STRAP_UPPER", tag="StrapUpper", C=(0.0589, -2.1837), root=112.0, span=360.0),
         dict(obj="P07_STRAP_LOWER", tag="StrapLower", C=(0.0455, -2.3473), root=110.0, span=320.0)]


def smoothstep(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def purge(name):
    o = bpy.data.objects.get(name)
    if o:
        d = o.data
        for c in list(o.users_collection):
            c.objects.unlink(o)
        bpy.data.objects.remove(o)
        if d and d.users == 0:
            if isinstance(d, bpy.types.Armature):
                bpy.data.armatures.remove(d)
            elif isinstance(d, bpy.types.Curve):
                bpy.data.curves.remove(d)


for S in SPECS:
    ob = bpy.data.objects[S["obj"]]; me = ob.data
    W = ob.matrix_world.copy(); Wi = W.inverted()
    C = S["C"]; root = S["root"]; span = S["span"]; tag = S["tag"]
    purge("NITE_" + tag + "_Armature"); purge("CRV_" + tag + "_Path")
    for md in list(ob.modifiers):
        if md.type == 'ARMATURE':
            ob.modifiers.remove(md)
    for vg in list(ob.vertex_groups):
        ob.vertex_groups.remove(vg)

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

    SS = [s for _, s in CTL]
    P = [at_s(s) for s in SS]
    m = len(P)
    # unit tangents of the centreline at each control point
    T = []
    for j in range(m):
        e = 0.004
        a0 = max(0.0, SS[j] - e); a1 = min(1.0, SS[j] + e)
        T.append((at_s(a1) - at_s(a0)).normalized())

    def bez(p0, h0, h1, p1, t):
        mt = 1 - t
        return p0 * (mt ** 3) + h0 * (3 * mt * mt * t) + h1 * (3 * mt * t * t) + p1 * (t ** 3)

    # least-squares handle magnitudes per segment (endpoints + tangent dirs fixed -> C1 kept)
    AL = [0.0] * (m - 1); BE = [0.0] * (m - 1)
    for j in range(m - 1):
        M = 80
        Q = [at_s(SS[j] + (SS[j + 1] - SS[j]) * (k / float(M))) for k in range(M + 1)]
        d = [0.0]
        for k in range(1, len(Q)):
            d.append(d[-1] + (Q[k] - Q[k - 1]).length)
        tp = [x / d[-1] for x in d]
        P0 = P[j]; P3 = P[j + 1]; T0 = T[j]; T1 = T[j + 1]
        alpha = beta = (P3 - P0).length / 3.0
        for _ in range(4):
            c11 = c12 = c22 = x1 = x2 = 0.0
            for k in range(len(Q)):
                t = tp[k]; mt = 1 - t
                A1 = T0 * (3 * mt * mt * t)
                A2 = -T1 * (3 * mt * t * t)
                base = P0 * (mt ** 3 + 3 * mt * mt * t) + P3 * (3 * mt * t * t + t ** 3)
                R = Q[k] - base
                c11 += A1.dot(A1); c12 += A1.dot(A2); c22 += A2.dot(A2)
                x1 += A1.dot(R); x2 += A2.dot(R)
            det = c11 * c22 - c12 * c12
            if abs(det) > 1e-12:
                a_ = (x1 * c22 - c12 * x2) / det
                b_ = (c11 * x2 - x1 * c12) / det
                lim = (P3 - P0).length * 1.6
                alpha = max(1e-4, min(lim, a_)); beta = max(1e-4, min(lim, b_))
            h0 = P0 + T0 * alpha; h1 = P3 - T1 * beta
            # Newton reparameterisation
            for k in range(len(Q)):
                t = tp[k]; mt = 1 - t
                B = bez(P0, h0, h1, P3, t)
                D1 = (h0 - P0) * (3 * mt * mt) + (h1 - h0) * (6 * mt * t) + (P3 - h1) * (3 * t * t)
                D2 = (h1 - h0 * 2 + P0) * (6 * mt) + (P3 - h1 * 2 + h0) * (6 * t)
                num = (B - Q[k]).dot(D1)
                den = D1.dot(D1) + (B - Q[k]).dot(D2)
                if abs(den) > 1e-12:
                    tp[k] = max(0.0, min(1.0, t - num / den))
        AL[j] = alpha; BE[j] = beta
    HR = [None] * m; HL = [None] * m
    for j in range(m - 1):
        HR[j] = P[j] + T[j] * AL[j]
        HL[j + 1] = P[j + 1] - T[j + 1] * BE[j]
    HL[0] = P[0] - T[0] * AL[0]
    HR[m - 1] = P[m - 1] + T[m - 1] * BE[m - 2]

    dense = []
    for j in range(m - 1):
        for k in range(0, 200):
            dense.append(bez(P[j], HR[j], HL[j + 1], P[j + 1], k / 200.0))
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

    # deviation: nearest distance from each dense curve sample to the centreline polyline
    devs = []
    for x in range(0, 401):
        p = on_curve(x / 400.0)
        best = 1e9
        c0 = max(0, int(x / 400.0 * (len(pts) - 1)) - 40)
        c1 = min(len(pts), int(x / 400.0 * (len(pts) - 1)) + 41)
        for q in pts[c0:c1]:
            dd = (p - q).length
            if dd < best:
                best = dd
        devs.append(best)
    dev = max(devs)

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
        ob.vertex_groups.new(name="DEF_%s_%02d" % (tag, i))
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
    md = ob.modifiers.new("ARM_" + tag, 'ARMATURE')
    md.object = ao; md.use_vertex_groups = True; md.use_bone_envelopes = False

    log.append("%s: centreline L=%.4f | curveL=%.4f | maxdev=%.5f meandev=%.5f | def=%d ctrl=%d verts=%d"
               % (tag, Lc, Ld, dev, sum(devs) / len(devs), NB, len(CTL), n))
    log.append("   bone world lengths: %s" % ["%.3f" % ((SB[i + 1] - SB[i]) * Ld) for i in range(NB)])
print("\n".join(log))
