import bpy, math
from mathutils import Vector, kdtree
SN = "05_SCN_P07_STRAP_RIG"
sc = bpy.data.scenes[SN]; vl = sc.view_layers[0]
rig = bpy.data.collections["P07_RIG"]
log = []
DEV_TARGET = 0.020
NS = 4000

# ends measured from the CAD end-caps (m7.py boundary-component analysis)
SPECS = [dict(src="64.002", obj="P07_STRAP_UPPER", me="ME_P07_STRAP_UPPER",
              mat="MAT_P07_STRAP_UPPER", tag="StrapUpper", nb=32,
              A=(-0.250, -1.528), B=(-0.889, -1.879), taper=True),
         dict(src="65.002", obj="P07_STRAP_LOWER", me="ME_P07_STRAP_LOWER",
              mat="MAT_P07_STRAP_LOWER", tag="StrapLower", nb=24,
              A=(-0.360, -1.530), B=(+0.470, -1.535), taper=False)]

HW = {"59": ((0.033, 0.501), (-1.593, -1.443), (0.83, 1.21)),
      "60": ((-0.433, -0.063), (-1.583, -1.486), (0.83, 1.21)),
      "63": ((-0.320, -0.173), (-1.544, -1.485), (0.12, 0.36)),
      "64k": ((0.270, 0.418), (-1.544, -1.485), (0.12, 0.36))}


def wmat(o):
    m = o.matrix_basis.copy(); p = o.parent; c = o
    while p:
        m = p.matrix_basis @ c.matrix_parent_inverse @ m; c = p; p = p.parent
    return m


def smoothstep(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def purge_obj(name):
    o = bpy.data.objects.get(name)
    if o:
        d = o.data
        for c in list(o.users_collection):
            c.objects.unlink(o)
        bpy.data.objects.remove(o)
        if d and d.users == 0:
            for coll in (bpy.data.armatures, bpy.data.curves, bpy.data.meshes):
                try:
                    coll.remove(d); break
                except Exception:
                    pass


def clean_mat(src, newname):
    m = bpy.data.materials.get(newname)
    if m:
        return m
    m = src.copy(); m.name = newname
    if m.node_tree.animation_data:
        m.node_tree.animation_data_clear()
    if m.animation_data:
        m.animation_data_clear()
    nt = m.node_tree
    out = [x for x in nt.nodes if x.type == 'OUTPUT_MATERIAL'][0]
    pr = [x for x in nt.nodes if x.type == 'BSDF_PRINCIPLED'][0]
    for l in list(out.inputs['Surface'].links):
        nt.links.remove(l)
    nt.links.new(pr.outputs[0], out.inputs['Surface'])
    for nd in [x for x in nt.nodes if "IGNITION" in x.name]:
        nt.nodes.remove(nd)
    return m


def resample(poly, N):
    cl = [0.0]
    for j in range(1, len(poly)):
        cl.append(cl[-1] + (poly[j] - poly[j - 1]).length)
    L = cl[-1]
    out = []
    for k in range(N):
        t = k / (N - 1.0) * L
        lo, hi = 0, len(cl) - 1
        while hi - lo > 1:
            m = (lo + hi) // 2
            if cl[m] <= t:
                lo = m
            else:
                hi = m
        d = cl[hi] - cl[lo]
        out.append(poly[lo].lerp(poly[hi], 0.0 if d < 1e-12 else (t - cl[lo]) / d))
    return out, L


def centreline(me, W, A, B):
    # Trace the flat top-face outline, split it at the two real end caps, and
    # average the two long edges.  This follows the folded-back free tail,
    # which angular binning cannot.
    n = len(me.vertices); co = [0.0] * (n * 3); me.vertices.foreach_get("co", co)
    P = [W @ Vector((co[3 * i], co[3 * i + 1], co[3 * i + 2])) for i in range(n)]
    zmid = (min(p.z for p in P) + max(p.z for p in P)) * 0.5
    ec = {}
    for pg in me.polygons:
        for e in pg.edge_keys:
            ec[e] = ec.get(e, 0) + 1
    adj = {}
    for a, b in [e for e, c in ec.items() if c == 1]:
        adj.setdefault(a, []).append(b); adj.setdefault(b, []).append(a)
    seen = set(); comps = []
    for s in adj:
        if s in seen:
            continue
        st = [s]; seen.add(s); c = []
        while st:
            q = st.pop(); c.append(q)
            for r in adj[q]:
                if r not in seen:
                    seen.add(r); st.append(r)
        comps.append(c)
    cand = []
    for c in comps:
        pp = [P[v] for v in c]
        dz = max(p.z for p in pp) - min(p.z for p in pp)
        dx = max(p.x for p in pp) - min(p.x for p in pp)
        if dz < 0.002 and dx > 1.5:
            cand.append((sum(p.z for p in pp) / len(pp), len(c), c))
    cand.sort(reverse=True, key=lambda t: (t[0], t[1]))
    comp = cand[0][2]
    start = comp[0]; path = [start]; prev = None; cur = start
    while True:
        nx = [v for v in adj[cur] if v != prev]
        if not nx or nx[0] == start:
            break
        path.append(nx[0]); prev = cur; cur = nx[0]
        if len(path) > len(comp) + 5:
            break
    M = len(path)

    def cap_index(T):
        d = [((P[path[k]].x - T[0]) ** 2 + (P[path[k]].y - T[1]) ** 2, k) for k in range(M)]
        d.sort()
        near = sorted(k for _, k in d[:max(4, M // 60)])
        gaps = [(near[(j + 1) % len(near)] - near[j]) % M for j in range(len(near))]
        gi = gaps.index(max(gaps))
        run = [near[(gi + 1 + j) % len(near)] for j in range(len(near))]
        return run[len(run) // 2]

    ia, ib = cap_index(A), cap_index(B)
    arc1 = [P[path[(ia + k) % M]] for k in range(((ib - ia) % M) + 1)]
    arc2 = [P[path[(ib + k) % M]] for k in range(((ia - ib) % M) + 1)]
    arc2.reverse()
    N = 1400
    r1, L1 = resample(arc1, N)
    r2, L2 = resample(arc2, N)
    raw = [Vector(((r1[k].x + r2[k].x) * 0.5, (r1[k].y + r2[k].y) * 0.5, zmid)) for k in range(N)]
    K = 5
    sm = [sum(raw[max(0, j - K):min(N, j + K + 1)], Vector((0, 0, 0))) /
          len(raw[max(0, j - K):min(N, j + K + 1)]) for j in range(N)]
    for j in range(N):
        sm[j].z = zmid
    return sm, L1, L2, M, ia, ib, P


prev = bpy.context.window.scene
try:
    bpy.context.window.scene = sc
    for S in SPECS:
        tag = S["tag"]
        for nm in ("NITE_%s_Armature" % tag, "CRV_%s_Path" % tag, S["obj"]):
            purge_obj(nm)
        a = bpy.data.actions.get("P07_TESTPOSES_" + tag)
        if a:
            bpy.data.actions.remove(a)

    for S in SPECS:
        src = bpy.data.objects[S["src"]]; tag = S["tag"]; NBONES = S["nb"]
        W = wmat(src); Wi = W.inverted(); SCA = W.to_scale()[0]
        me = src.data.copy(); me.name = S["me"]
        ob = bpy.data.objects.new(S["obj"], me); ob.matrix_world = W
        rig.objects.link(ob)
        mat = clean_mat(src.material_slots[0].material, S["mat"])
        ob.material_slots[0].link = 'OBJECT'; ob.material_slots[0].material = mat
        with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob],
                                       selected_editable_objects=[ob], scene=sc, view_layer=vl):
            if me.has_custom_normals:
                bpy.ops.mesh.customdata_custom_splitnormals_clear()
            bpy.ops.object.shade_smooth_by_angle(angle=math.radians(30))

        pts, L1, L2, M, ia, ib, wp = centreline(me, W, S["A"], S["B"])
        n = len(wp)
        cl = [0.0]
        for j in range(1, len(pts)):
            cl.append(cl[-1] + (pts[j] - pts[j - 1]).length)
        Lc = cl[-1]

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
            return pts[lo].lerp(pts[hi], 0.0 if d < 1e-12 else (t - cl[lo]) / d)

        dense_s = [i / (NS - 1.0) for i in range(NS)]
        cpts = [at_s(s) for s in dense_s]
        hits = {k: [] for k in HW}
        for i, p in enumerate(cpts):
            for k, (bx, by, bz) in HW.items():
                if bx[0] <= p.x <= bx[1] and by[0] <= p.y <= by[1] and bz[0] <= p.z <= bz[1]:
                    hits[k].append(dense_s[i])
        runs = {}
        for k, ss in hits.items():
            if not ss:
                continue
            gr = [[ss[0]]]
            for v in ss[1:]:
                if v - gr[-1][-1] > 0.02:
                    gr.append([v])
                else:
                    gr[-1].append(v)
            runs[k] = [(g[0], g[-1]) for g in gr]
        log.append("%s hardware along centreline: %s" %
                   (tag, dict((k, ["%.3f-%.3f" % r for r in v]) for k, v in runs.items())))

        if S["taper"]:
            lock = runs.get("59", [(0.85, 0.90)])[-1]
            keep = runs.get("60", [(0.93, 0.97)])[-1]
            SEM = [("ROOT", 0.0),
                   ("SIDE_A", lock[0] * 0.30),
                   ("MID", lock[0] * 0.56),
                   ("SIDE_B", lock[0] * 0.82),
                   ("BUCKLE", (lock[0] + lock[1]) * 0.5),
                   ("ENTRY", (keep[0] + keep[1]) * 0.5),
                   ("END", 1.0)]
        else:
            SEM = [("ROOT", 0.0), ("SIDE_A", 0.17), ("MID", 0.34), ("SIDE_B", 0.50),
                   ("BUCKLE", 0.66), ("ENTRY", 0.83), ("END", 1.0)]

        ND = 4000
        if S["taper"]:
            dn = [1.0 + 2.2 * (1.0 - smoothstep(j / ND / 0.05))
                  + 1.6 * smoothstep((j / ND - 0.70) / 0.18) for j in range(ND + 1)]
        else:
            dn = [1.0 + 2.2 * (1.0 - smoothstep(j / ND / 0.05))
                  + 2.2 * smoothstep((j / ND - 0.94) / 0.05) for j in range(ND + 1)]
        cum = [0.0]
        for j in range(1, ND + 1):
            cum.append(cum[-1] + (dn[j] + dn[j - 1]) * 0.5)
        tot = cum[-1]
        SB = []
        for i in range(NBONES + 1):
            tgt = tot * i / NBONES
            lo, hi = 0, ND
            while hi - lo > 1:
                m = (lo + hi) // 2
                if cum[m] <= tgt:
                    lo = m
                else:
                    hi = m
            d = cum[hi] - cum[lo]
            SB.append((lo + (0.0 if d < 1e-12 else (tgt - cum[lo]) / d)) / ND)
        SB[0] = 0.0; SB[-1] = 1.0

        cuname = "CRV_" + tag + "_Path"
        cu = bpy.data.curves.new(cuname, 'CURVE'); cu.dimensions = '3D'; cu.resolution_u = 48
        cuo = bpy.data.objects.new(cuname, cu); cuo.matrix_world = W
        rig.objects.link(cuo); cuo.hide_render = True
        best = None
        for NCP in (20, 26, 32, 40, 48):
            cu.splines.clear()
            sp = cu.splines.new('BEZIER'); sp.bezier_points.add(NCP - 1)
            css = [i / (NCP - 1.0) for i in range(NCP)]
            for j, bp in enumerate(sp.bezier_points):
                bp.co = Wi @ at_s(css[j])
                bp.handle_left_type = 'AUTO'; bp.handle_right_type = 'AUTO'
            dg = bpy.context.evaluated_depsgraph_get()
            evc = cuo.evaluated_get(dg); tm = evc.to_mesh()
            dense = [v.co.copy() for v in tm.vertices]
            evc.to_mesh_clear()
            dl = [0.0]
            for j in range(1, len(dense)):
                dl.append(dl[-1] + (dense[j] - dense[j - 1]).length)
            devs = []
            for x in range(6, 395):
                t = x / 400.0 * dl[-1]
                lo, hi = 0, len(dl) - 1
                while hi - lo > 1:
                    k = (lo + hi) // 2
                    if dl[k] <= t:
                        lo = k
                    else:
                        hi = k
                dd = dl[hi] - dl[lo]
                p = W @ dense[lo].lerp(dense[hi], 0.0 if dd < 1e-12 else (t - dl[lo]) / dd)
                c0 = max(0, int(x / 400.0 * (len(pts) - 1)) - 60)
                c1 = min(len(pts), int(x / 400.0 * (len(pts) - 1)) + 61)
                devs.append(min((p - q).length for q in pts[c0:c1]))
            best = (NCP, css, dense, dl, max(devs), sum(devs) / len(devs))
            if max(devs) <= DEV_TARGET:
                break
        NCP, css, dense, dl, devmax, devmean = best
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
            return dense[lo].lerp(dense[hi], 0.0 if d < 1e-12 else (t - dl[lo]) / d)

        aname = "NITE_" + tag + "_Armature"
        ad = bpy.data.armatures.new(aname); ao = bpy.data.objects.new(aname, ad)
        ao.matrix_world = W; rig.objects.link(ao); ao.show_in_front = True
        vl.objects.active = ao
        bpy.ops.object.mode_set(mode='EDIT')
        upl = (Wi.to_3x3() @ Vector((0, 0, 1))).normalized()
        CPLEN, CPOFF = 16.0, 8.0
        CTLLEN, CTLOFF = 30.0, 30.0
        joints = [on_curve(s) for s in SB]
        mb = ad.edit_bones.new(tag + "_MASTER")
        mb.head = joints[0] - upl * 18.0; mb.tail = mb.head + upl * 60.0
        mb.use_deform = False
        for nm, s in SEM:
            p = on_curve(s)
            b = ad.edit_bones.new("%s_%s_CTRL" % (tag, nm))
            b.head = p + upl * CTLOFF; b.tail = p + upl * (CTLOFF + CTLLEN)
            b.use_deform = False; b.parent = mb; b.use_connect = False
        owner = []
        for j, s in enumerate(css):
            nm = min(SEM, key=lambda kv: abs(kv[1] - s))[0]
            owner.append(nm)
            p = on_curve(s)
            b = ad.edit_bones.new("%s_CP_%02d" % (tag, j))
            b.head = p + upl * CPOFF; b.tail = p + upl * (CPOFF + CPLEN)
            b.use_deform = False
            b.parent = ad.edit_bones["%s_%s_CTRL" % (tag, nm)]
            b.use_connect = False
        defb = []
        for i in range(NBONES):
            d = ad.edit_bones.new("DEF_%s_%02d" % (tag, i))
            d.head = joints[i]; d.tail = joints[i + 1]
            d.align_roll(upl); d.use_deform = True
            d.parent = mb if i == 0 else defb[-1]
            d.use_connect = (i > 0)
            defb.append(d)
        bpy.ops.object.mode_set(mode='OBJECT')
        for cname in ("CTRL", "CP", "DEF"):
            if cname not in [c.name for c in ad.collections_all]:
                ad.collections.new(cname)
        for bn in list(ad.bones):
            g = "DEF" if bn.name.startswith("DEF_") else ("CP" if "_CP_" in bn.name else "CTRL")
            ad.collections[g].assign(ad.bones[bn.name])
        ad.collections["DEF"].is_visible = False
        pbn = ao.pose.bones["DEF_%s_%02d" % (tag, NBONES - 1)]
        con = pbn.constraints.new('SPLINE_IK')
        con.name = "SPLINE_IK_" + tag
        con.target = cuo; con.chain_count = NBONES
        con.y_scale_mode = 'BONE_ORIGINAL'; con.xz_scale_mode = 'NONE'
        con.use_curve_radius = False; con.use_even_divisions = False; con.use_chain_offset = False
        for j in range(NCP):
            bname = "%s_CP_%02d" % (tag, j)
            h = cuo.modifiers.new("HOOK_CP_%02d" % j, 'HOOK')
            h.object = ao; h.subtarget = bname
            h.falloff_type = 'NONE'; h.strength = 1.0
            h.matrix_inverse = ad.bones[bname].matrix_local.inverted()
            h.vertex_indices_set([3 * j, 3 * j + 1, 3 * j + 2])

        kd = kdtree.KDTree(NS)
        for i, p in enumerate(cpts):
            kd.insert(Vector((p.x, p.y, 0.0)), i)
        kd.balance()
        # End caps and the sewn fold-backs sit off the side of the centreline
        # ends; snap them rigidly onto the first / last deform bone instead of
        # letting nearest-point drop them onto a bone further along the belt.
        E0, E1 = cpts[0], cpts[-1]
        sv = [0.0] * n; far = 0; snapped = 0; dmax = 0.0
        for i in range(n):
            _, idx, dist = kd.find(Vector((wp[i].x, wp[i].y, 0.0)))
            s = idx / (NS - 1.0)
            if dist > 0.025:
                d0 = math.hypot(wp[i].x - E0.x, wp[i].y - E0.y)
                d1 = math.hypot(wp[i].x - E1.x, wp[i].y - E1.y)
                if min(d0, d1) < 0.20:
                    s = 0.0 if d0 <= d1 else 1.0
                    snapped += 1
                else:
                    far += 1
                    if dist > dmax:
                        dmax = dist
            sv[i] = s
        for i in range(NBONES):
            ob.vertex_groups.new(name="DEF_%s_%02d" % (tag, i))
        hw = []
        for j in range(1, NBONES):
            base = min(SB[j] - SB[j - 1], SB[j + 1] - SB[j]) * 0.45
            hw.append(base * (0.45 + 0.55 * SB[j]))
        buckets = [dict() for _ in range(NBONES)]
        for i in range(n):
            s = sv[i]
            k = NBONES - 1
            for j in range(NBONES):
                if s < SB[j + 1]:
                    k = j; break
            w = {k: 1.0}
            if k > 0 and s < SB[k] + hw[k - 1]:
                t = smoothstep((s - (SB[k] - hw[k - 1])) / (2 * hw[k - 1]))
                w = {k - 1: 1.0 - t, k: t}
            elif k < NBONES - 1 and s > SB[k + 1] - hw[k]:
                t = smoothstep((s - (SB[k + 1] - hw[k])) / (2 * hw[k]))
                w = {k: 1.0 - t, k + 1: t}
            for bi, wt in w.items():
                if wt <= 0.0005:
                    continue
                buckets[bi].setdefault(round(wt, 3), []).append(i)
        for bi in range(NBONES):
            vg = ob.vertex_groups["DEF_%s_%02d" % (tag, bi)]
            for q, idxs in buckets[bi].items():
                vg.add(idxs, q, 'REPLACE')
        md = ob.modifiers.new("ARM_" + tag, 'ARMATURE')
        md.object = ao; md.use_vertex_groups = True; md.use_bone_envelopes = False

        log.append("%s src=%s  rim walk M=%d  caps at idx %d / %d  edge lengths %.4f / %.4f" %
                   (tag, S["src"], M, ia, ib, L1, L2))
        log.append("   centreline L=%.4f | curve %d CPs L=%.4f dev max=%.4f mean=%.4f" %
                   (Lc, NCP, Ld * SCA, devmax, devmean))
        log.append("   %d DEF bones, world len %.3f..%.3f | end-snapped %d, unresolved %d (worst %.4f)" %
                   (NBONES, min(SB[i + 1] - SB[i] for i in range(NBONES)) * Ld * SCA,
                    max(SB[i + 1] - SB[i] for i in range(NBONES)) * Ld * SCA, snapped, far, dmax))
        log.append("   SEM: %s" % ["%s=%.3f" % (a, b) for a, b in SEM])
        log.append("   CP->CTRL: %s" % dict((nm, owner.count(nm)) for nm, _ in SEM))
finally:
    bpy.context.window.scene = prev
print("\n".join(log))
