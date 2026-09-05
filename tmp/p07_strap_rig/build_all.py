import bpy, bmesh, math
from mathutils import Vector, Matrix
SN = "05_SCN_P07_STRAP_RIG"
sc = bpy.data.scenes[SN]; vl = sc.view_layers[0]
rig = bpy.data.collections["P07_RIG"]
log = []

NBONES = 24
S_ROOT = 0.048
SB = [0.0, S_ROOT] + [S_ROOT + (1.0 - S_ROOT) * i / (NBONES - 1) for i in range(1, NBONES)]
CTL = [("ROOT", 0.0), ("SIDE_A", 0.10), ("BACK_A", 0.22), ("BACK_B", 0.34), ("MID", 0.46),
       ("BACK_C", 0.58), ("SIDE_B", 0.70), ("BUCKLE", 0.815), ("ENTRY", 0.905), ("END", 1.0)]
BINS = 720

SPECS = [dict(src="P01_STRAP_UPPER", obj="P07_STRAP_UPPER", me="ME_P07_STRAP_UPPER",
              mat="MAT_P07_STRAP_UPPER", tag="StrapUpper", cutpt=(-0.248, -1.535)),
         dict(src="P01_STRAP_LOWER", obj="P07_STRAP_LOWER", me="ME_P07_STRAP_LOWER",
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
    out = [n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'][0]
    pr = [n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'][0]
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
        W = wmat(src); Wi = W.inverted()
        me = src.data.copy(); me.name = S["me"]
        ob = bpy.data.objects.new(S["obj"], me); ob.matrix_world = W
        rig.objects.link(ob)
        mat = clean_mat(src.material_slots[0].material, S["mat"])
        ob.material_slots[0].link = 'OBJECT'; ob.material_slots[0].material = mat
        ctx = dict(object=ob, active_object=ob, selected_objects=[ob],
                   selected_editable_objects=[ob], scene=sc, view_layer=vl)
        with bpy.context.temp_override(**ctx):
            if me.has_custom_normals:
                bpy.ops.mesh.customdata_custom_splitnormals_clear()
            bpy.ops.object.shade_smooth_by_angle(angle=math.radians(30))

        n = len(me.vertices); co = [0.0] * (n * 3); me.vertices.foreach_get("co", co)
        wp = [W @ Vector((co[3 * i], co[3 * i + 1], co[3 * i + 2])) for i in range(n)]
        C = ((min(p.x for p in wp) + max(p.x for p in wp)) * 0.5,
             (min(p.y for p in wp) + max(p.y for p in wp)) * 0.5)
        ang = [math.degrees(math.atan2(p.y - C[1], p.x - C[0])) % 360.0 for p in wp]

        # ---- open the loop / find the free ends --------------------------
        occ = [0] * BINS
        for a in ang:
            occ[int(a / (360.0 / BINS))] += 1
        empty_runs = []
        i = 0
        while i < BINS:
            if occ[i] == 0:
                j = i
                while j < BINS and occ[j] == 0:
                    j += 1
                empty_runs.append((j - i, i, j))
                i = j
            else:
                i += 1
        if S["cutpt"] is not None:
            cut = math.degrees(math.atan2(S["cutpt"][1] - C[1], S["cutpt"][0] - C[0])) % 360.0
            aa = math.radians(cut)
            rad_w = Vector((math.cos(aa), math.sin(aa), 0.0))
            tan_w = Vector((-math.sin(aa), math.cos(aa), 0.0))
            co_l = Wi @ Vector((C[0], C[1], 0.0))
            R3 = Wi.to_3x3()
            no_l = (R3 @ tan_w).normalized(); rad_l = (R3 @ rad_w).normalized()
            bm = bmesh.new(); bm.from_mesh(me)
            res = bmesh.ops.bisect_plane(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
                                         dist=1e-4, plane_co=co_l, plane_no=no_l,
                                         clear_outer=False, clear_inner=False)
            ce = [g for g in res['geom_cut'] if isinstance(g, bmesh.types.BMEdge)
                  and ((g.verts[0].co + g.verts[1].co) * 0.5 - co_l).dot(rad_l) > 0.0]
            bmesh.ops.split_edges(bm, edges=ce)
            bm.to_mesh(me); bm.free()
            n = len(me.vertices); co = [0.0] * (n * 3); me.vertices.foreach_get("co", co)
            wp = [W @ Vector((co[3 * i], co[3 * i + 1], co[3 * i + 2])) for i in range(n)]
            ang = [math.degrees(math.atan2(p.y - C[1], p.x - C[0])) % 360.0 for p in wp]
            root = cut; span = 360.0
            info = "cut@%.1fdeg (%d edges)" % (cut, len(ce))
        else:
            g = max(empty_runs)
            root = (g[2]) * (360.0 / BINS)
            span = 360.0 - g[0] * (360.0 / BINS)
            info = "open band, gap %.1f..%.1f deg" % (g[1] * 360.0 / BINS, root)
        us = [(a - root) % 360.0 for a in ang]

        # ---- centreline --------------------------------------------------
        binw = span / BINS
        acc = [None] * BINS; cnt = [0] * BINS
        for i in range(n):
            b = int(us[i] / binw)
            if 0 <= b < BINS:
                if acc[b] is None:
                    acc[b] = Vector((0, 0, 0))
                acc[b] += wp[i]; cnt[b] += 1
        filled = [b for b in range(BINS) if cnt[b] > 0]
        pts = [acc[b] / cnt[b] for b in filled]
        K = 6
        pts = [sum(pts[max(0, j - K):min(len(pts), j + K + 1)], Vector((0, 0, 0))) /
               len(pts[max(0, j - K):min(len(pts), j + K + 1)]) for j in range(len(pts))]
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

        # ---- control curve: bezier through the centreline, AUTO handles ---
        P = [at_s(s) for _, s in CTL]
        cuname = "CRV_" + tag + "_Path"
        cu = bpy.data.curves.new(cuname, 'CURVE'); cu.dimensions = '3D'; cu.resolution_u = 64
        sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(P) - 1)
        for j, bp in enumerate(sp.bezier_points):
            bp.co = Wi @ P[j]
            bp.handle_left_type = 'AUTO'; bp.handle_right_type = 'AUTO'
        cuo = bpy.data.objects.new(cuname, cu); cuo.matrix_world = W
        rig.objects.link(cuo); cuo.hide_render = True

        dg = bpy.context.evaluated_depsgraph_get()
        evc = cuo.evaluated_get(dg); tm = evc.to_mesh()
        dense = [v.co.copy() for v in tm.vertices]
        evc.to_mesh_clear()
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

        devs = []
        for x in range(401):
            p = W @ on_curve(x / 400.0)
            c0 = max(0, int(x / 400.0 * (len(pts) - 1)) - 45)
            c1 = min(len(pts), int(x / 400.0 * (len(pts) - 1)) + 46)
            devs.append(min((p - q).length for q in pts[c0:c1]))

        # ---- armature ------------------------------------------------------
        aname = "NITE_" + tag + "_Armature"
        ad = bpy.data.armatures.new(aname); ao = bpy.data.objects.new(aname, ad)
        ao.matrix_world = W; rig.objects.link(ao); ao.show_in_front = True
        vl.objects.active = ao
        bpy.ops.object.mode_set(mode='EDIT')
        upl = (Wi.to_3x3() @ Vector((0, 0, 1))).normalized()
        CTLLEN = 27.0; MASTLEN = 55.0; CTLOFF = 14.0
        joints = [on_curve(s) for s in SB]
        mb = ad.edit_bones.new(tag + "_MASTER")
        mb.head = joints[0] - upl * (MASTLEN * 0.25); mb.tail = mb.head + upl * MASTLEN
        mb.use_deform = False
        defb = []
        for i in range(NBONES):
            d = ad.edit_bones.new("DEF_%s_%02d" % (tag, i))
            d.head = joints[i]; d.tail = joints[i + 1]
            d.align_roll(upl); d.use_deform = True
            d.parent = mb if i == 0 else defb[-1]
            d.use_connect = (i > 0)
            defb.append(d)
        for cn, cs in CTL:
            p = on_curve(cs)
            cb = ad.edit_bones.new("%s_%s_CTRL" % (tag, cn))
            cb.head = p + upl * CTLOFF; cb.tail = p + upl * (CTLOFF + CTLLEN)
            cb.use_deform = False; cb.parent = mb; cb.use_connect = False
        bpy.ops.object.mode_set(mode='OBJECT')
        for cname in ("CTRL", "DEF"):
            if cname not in [c.name for c in ad.collections_all]:
                ad.collections.new(cname)
        for bn in list(ad.bones):
            ad.collections["DEF" if bn.name.startswith("DEF_") else "CTRL"].assign(ad.bones[bn.name])
        ad.collections["DEF"].is_visible = False
        pb = ao.pose.bones["DEF_%s_%02d" % (tag, NBONES - 1)]
        con = pb.constraints.new('SPLINE_IK')
        con.name = "SPLINE_IK_" + tag
        con.target = cuo; con.chain_count = NBONES
        con.y_scale_mode = 'BONE_ORIGINAL'; con.xz_scale_mode = 'NONE'
        con.use_curve_radius = False; con.use_even_divisions = False; con.use_chain_offset = False

        for j, (cn, cs) in enumerate(CTL):
            bname = "%s_%s_CTRL" % (tag, cn)
            h = cuo.modifiers.new("HOOK_" + cn, 'HOOK')
            h.object = ao; h.subtarget = bname
            h.falloff_type = 'NONE'; h.strength = 1.0
            h.matrix_inverse = ad.bones[bname].matrix_local.inverted()
            h.vertex_indices_set([3 * j, 3 * j + 1, 3 * j + 2])

        # ---- weights --------------------------------------------------------
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

        log.append("%s src=%s C=(%.4f,%.4f) %s | centreL=%.4f curveL=%.4f dev max=%.4f mean=%.4f | bones=%d ctrl=%d verts=%d"
                   % (tag, S["src"], C[0], C[1], info, Lc, Ld * W.to_scale()[0],
                      max(devs), sum(devs) / len(devs), NBONES, len(CTL), n))
        log.append("   bone len (world) min=%.3f max=%.3f | blend halfwidth min=%.4f max=%.4f"
                   % (min((SB[i + 1] - SB[i]) for i in range(NBONES)) * Ld * W.to_scale()[0],
                      max((SB[i + 1] - SB[i]) for i in range(NBONES)) * Ld * W.to_scale()[0],
                      min(hw), max(hw)))
finally:
    bpy.context.window.scene = prev
print("\n".join(log))
