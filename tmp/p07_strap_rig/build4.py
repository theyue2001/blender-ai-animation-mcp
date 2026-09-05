import bpy, bmesh, math
from mathutils import Vector, Matrix
SN = "05_SCN_P07_STRAP_RIG"
sc = bpy.data.scenes[SN]; vl = sc.view_layers[0]
rig = bpy.data.collections["P07_RIG"]
log = []

NBONES = 24
S_ROOT = 0.048
SB = [0.0, S_ROOT] + [S_ROOT + (1.0 - S_ROOT) * i / (NBONES - 1) for i in range(1, NBONES)]
SEM = [("ROOT", 0.0), ("SIDE_A", 0.23), ("MID", 0.46), ("SIDE_B", 0.69),
       ("BUCKLE", 0.815), ("ENTRY", 0.905), ("END", 1.0)]
BINS = 720
DEV_TARGET = 0.020

SPECS = [dict(src="64.002", obj="P07_STRAP_UPPER", me="ME_P07_STRAP_UPPER",
              mat="MAT_P07_STRAP_UPPER", tag="StrapUpper", cutpt=(-0.014, -1.490)),
         dict(src="65.002", obj="P07_STRAP_LOWER", me="ME_P07_STRAP_LOWER",
              mat="MAT_P07_STRAP_LOWER", tag="StrapLower", cutpt=None)]


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
        src = bpy.data.objects[S["src"]]; tag = S["tag"]
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

        def sample():
            k = len(me.vertices); c = [0.0] * (k * 3); me.vertices.foreach_get("co", c)
            return k, [W @ Vector((c[3 * i], c[3 * i + 1], c[3 * i + 2])) for i in range(k)]

        n, wp = sample()
        C = ((min(p.x for p in wp) + max(p.x for p in wp)) * 0.5,
             (min(p.y for p in wp) + max(p.y for p in wp)) * 0.5)
        ang = [math.degrees(math.atan2(p.y - C[1], p.x - C[0])) % 360.0 for p in wp]
        occ = [0] * BINS
        for a in ang:
            occ[int(a / (360.0 / BINS))] += 1
        runs = []
        i = 0
        while i < BINS:
            if occ[i] == 0:
                j = i
                while j < BINS and occ[j] == 0:
                    j += 1
                runs.append((j - i, i, j)); i = j
            else:
                i += 1
        if S["cutpt"] is not None:
            cut = math.degrees(math.atan2(S["cutpt"][1] - C[1], S["cutpt"][0] - C[0])) % 360.0
            aa = math.radians(cut)
            R3 = Wi.to_3x3()
            co_l = Wi @ Vector((C[0], C[1], 0.0))
            no_l = (R3 @ Vector((-math.sin(aa), math.cos(aa), 0.0))).normalized()
            rad_l = (R3 @ Vector((math.cos(aa), math.sin(aa), 0.0))).normalized()
            bm = bmesh.new(); bm.from_mesh(me)
            res = bmesh.ops.bisect_plane(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
                                         dist=1e-4, plane_co=co_l, plane_no=no_l,
                                         clear_outer=False, clear_inner=False)
            ce = [g for g in res['geom_cut'] if isinstance(g, bmesh.types.BMEdge)
                  and ((g.verts[0].co + g.verts[1].co) * 0.5 - co_l).dot(rad_l) > 0.0]
            bmesh.ops.split_edges(bm, edges=ce)
            bm.to_mesh(me); bm.free()
            n, wp = sample()
            ang = [math.degrees(math.atan2(p.y - C[1], p.x - C[0])) % 360.0 for p in wp]
            root = cut; span = 360.0
            info = "closed ring cut open @%.1f deg (%d edges split)" % (cut, len(ce))
        else:
            g = max(runs)
            root = g[2] * (360.0 / BINS); span = 360.0 - g[0] * (360.0 / BINS)
            info = "open band, free ends at %.1f / %.1f deg" % (g[1] * 360.0 / BINS, root)
        us = [(a - root) % 360.0 for a in ang]

        # Resolve the seam. Vertices sitting exactly on the cut are ambiguous:
        # the anchored root end and the free tail end differ only by float noise
        # in the angle, so label them by mesh connectivity instead of by angle.
        TH = 0.25
        namb = 0; nun = 0
        if span >= 359.0:
            amb = [i for i in range(n) if us[i] < TH or us[i] > 360.0 - TH]
            namb = len(amb)
            adj = [[] for _ in range(n)]
            for pg in me.polygons:
                vs = list(pg.vertices)
                for q in range(len(vs)):
                    a1 = vs[q]; b1 = vs[(q + 1) % len(vs)]
                    adj[a1].append(b1); adj[b1].append(a1)
            lab = [-1] * n
            ambset = set(amb)
            for i in range(n):
                if i not in ambset:
                    lab[i] = 0 if us[i] < 180.0 else 1
            from collections import deque
            dq = deque()
            for i in range(n):
                if lab[i] >= 0:
                    for j in adj[i]:
                        if lab[j] < 0:
                            dq.append((j, lab[i]))
            while dq:
                i, l = dq.popleft()
                if lab[i] >= 0:
                    continue
                lab[i] = l
                for j in adj[i]:
                    if lab[j] < 0:
                        dq.append((j, l))
            for i in amb:
                dd = min(us[i], 360.0 - us[i])
                if lab[i] == 1:
                    us[i] = 360.0 - dd
                elif lab[i] == 0:
                    us[i] = dd
                else:
                    # island entirely on the cut plane: keep it with the anchored
                    # root end so it can never tear away from the device
                    us[i] = dd
                    nun += 1
            # face-less wire edges cannot be separated by a face split - drop the
            # ones that would otherwise tie the root bone to the tail bone
            bm = bmesh.new(); bm.from_mesh(me)
            bm.verts.ensure_lookup_table()
            wire = [e for e in bm.edges if not e.link_faces
                    and abs(us[e.verts[0].index] - us[e.verts[1].index]) > 180.0]
            if wire:
                bmesh.ops.delete(bm, geom=wire, context='EDGES')
                bm.to_mesh(me)
            bm.free()
            info += " ; seam: %d verts relabelled by connectivity (%d unresolved), %d seam wire edges removed" % (namb, nun, len(wire))

        binw = span / BINS
        acc = [None] * BINS; cnt = [0] * BINS
        for i in range(n):
            b = int(us[i] / binw)
            if 0 <= b < BINS:
                if acc[b] is None:
                    acc[b] = Vector((0, 0, 0))
                acc[b] += wp[i]; cnt[b] += 1
        filled = [b for b in range(BINS) if cnt[b] > 0]
        raw = [acc[b] / cnt[b] for b in filled]
        K = 6
        pts = [sum(raw[max(0, j - K):min(len(raw), j + K + 1)], Vector((0, 0, 0))) /
               len(raw[max(0, j - K):min(len(raw), j + K + 1)]) for j in range(len(raw))]
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
            return (cl[lo] + (u - ub[lo]) / (ub[hi] - ub[lo]) * (cl[hi] - cl[lo])) / Lc

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

        # ---- semantic controls placed on the real hardware ----------------
        HW = {"59": ((0.033, 0.501), (-1.593, -1.443), (0.83, 1.21)),
              "60": ((-0.433, -0.063), (-1.583, -1.486), (0.83, 1.21)),
              "63": ((-0.320, -0.173), (-1.544, -1.485), (0.12, 0.36)),
              "64k": ((0.270, 0.418), (-1.544, -1.485), (0.12, 0.36))}
        hits = {}
        for q in range(1200):
            sq = q / 1199.0
            pq = at_s(sq)
            for k, (bx, by, bz) in HW.items():
                if bx[0] <= pq.x <= bx[1] and by[0] <= pq.y <= by[1] and bz[0] <= pq.z <= bz[1]:
                    hits.setdefault(k, []).append(sq)
        runs = {}
        for k, ss in hits.items():
            gr = [[ss[0]]]
            for v in ss[1:]:
                (gr.append([v]) if v - gr[-1][-1] > 0.02 else gr[-1].append(v))
            runs[k] = [(g[0], g[-1]) for g in gr]
        if tag == "StrapUpper":
            lk = runs.get("59", [(0.88, 0.99)])[-1]
            SEM = [("ROOT", 0.0), ("SIDE_A", lk[0] * 0.28), ("MID", lk[0] * 0.53),
                   ("SIDE_B", lk[0] * 0.78), ("BUCKLE", lk[0]),
                   ("ENTRY", (lk[0] + lk[1]) * 0.5), ("END", 1.0)]
        else:
            SEM = [("ROOT", 0.0), ("SIDE_A", 0.17), ("MID", 0.34), ("SIDE_B", 0.50),
                   ("BUCKLE", 0.66), ("ENTRY", 0.83), ("END", 1.0)]
        log.append("%s hardware along centreline: %s" %
                   (tag, dict((k, ["%.3f-%.3f" % r for r in v]) for k, v in runs.items())))
        log.append("   SEM: %s" % ["%s=%.3f" % (a, b) for a, b in SEM])

        # ---- adaptive control-point count so the AUTO-handle curve fits -----
        cuname = "CRV_" + tag + "_Path"
        cu = bpy.data.curves.new(cuname, 'CURVE'); cu.dimensions = '3D'; cu.resolution_u = 48
        cuo = bpy.data.objects.new(cuname, cu); cuo.matrix_world = W
        rig.objects.link(cuo); cuo.hide_render = True
        best = None
        for NCP in (16, 20, 26, 32):
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
            for x in range(16, 397):
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
                c0 = max(0, int(x / 400.0 * (len(pts) - 1)) - 50)
                c1 = min(len(pts), int(x / 400.0 * (len(pts) - 1)) + 51)
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

        # ---- armature: MASTER > 7 semantic CTRLs > CP bones + DEF chain -----
        aname = "NITE_" + tag + "_Armature"
        ad = bpy.data.armatures.new(aname); ao = bpy.data.objects.new(aname, ad)
        ao.matrix_world = W; rig.objects.link(ao); ao.show_in_front = True
        vl.objects.active = ao
        bpy.ops.object.mode_set(mode='EDIT')
        upl = (Wi.to_3x3() @ Vector((0, 0, 1))).normalized()
        CPLEN, CPOFF = 16.0, 8.0
        CTLLEN, CTLOFF = 30.0, 30.0
        MASTLEN = 60.0
        joints = [on_curve(s) for s in SB]
        mb = ad.edit_bones.new(tag + "_MASTER")
        mb.head = joints[0] - upl * (MASTLEN * 0.3); mb.tail = mb.head + upl * MASTLEN
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
        pb = ao.pose.bones["DEF_%s_%02d" % (tag, NBONES - 1)]
        con = pb.constraints.new('SPLINE_IK')
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

        for i in range(NBONES):
            ob.vertex_groups.new(name="DEF_%s_%02d" % (tag, i))
        hw = []
        for j in range(1, NBONES):
            base = min(SB[j] - SB[j - 1], SB[j + 1] - SB[j]) * 0.45
            hw.append(base * (0.45 + 0.55 * SB[j]))
        buckets = [dict() for _ in range(NBONES)]
        for i in range(n):
            s = u2s(us[i])
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

        log.append("%s  src=%s  %s" % (tag, S["src"], info))
        log.append("   centreline L=%.4f | curve: %d CPs, L=%.4f, dev max=%.4f mean=%.4f" %
                   (Lc, NCP, Ld * SCA, devmax, devmean))
        log.append("   bones: %d deform (len %.3f..%.3f world) + %d CP + %d semantic CTRL + MASTER ; verts=%d" %
                   (NBONES, min(SB[i + 1] - SB[i] for i in range(NBONES)) * Ld * SCA,
                    max(SB[i + 1] - SB[i] for i in range(NBONES)) * Ld * SCA, NCP, len(SEM), n))
        log.append("   CP->CTRL groups: %s" % {nm: owner.count(nm) for nm, _ in SEM})
finally:
    bpy.context.window.scene = prev
print("\n".join(log))
