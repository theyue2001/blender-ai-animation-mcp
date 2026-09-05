import bpy, math, random
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SN = "05_SCN_P07_STRAP_RIG"
sc = bpy.data.scenes[SN]
FRAMES = [1, 40, 80, 120, 160]
NB = 240
BINS = 720
out = []
random.seed(11)

prev = bpy.context.window.scene
prevf = {s.name: s.frame_current for s in bpy.data.scenes}
try:
    bpy.context.window.scene = sc
    body = []
    for bn in ("P07R_Male", "P07R_Underwear"):
        o = bpy.data.objects[bn]
        base = len(body)
        body.append(None)
    mb = bpy.data.objects["P07R_Male"]
    bverts = [mb.matrix_world @ v.co for v in mb.data.vertices]
    bpolys = [list(p.vertices) for p in mb.data.polygons]
    bvh = BVHTree.FromPolygons(bverts, bpolys, all_triangles=False, epsilon=0.0)
    dv = []; dp = []
    for dn in ("P07R_58.002", "P07R_59.002", "P07R_60.002", "P07R_63.002", "P07R_64.005"):
        do = bpy.data.objects[dn]; off = len(dv)
        dv += [do.matrix_world @ v.co for v in do.data.vertices]
        dp += [[i + off for i in pg.vertices] for pg in do.data.polygons]
    bvhd = BVHTree.FromPolygons(dv, dp, all_triangles=False, epsilon=0.0)
    uw = bpy.data.objects["P07R_Underwear"]
    uverts = [uw.matrix_world @ v.co for v in uw.data.vertices]
    upolys = [list(p.vertices) for p in uw.data.polygons]
    bvhu = BVHTree.FromPolygons(uverts, upolys, all_triangles=False, epsilon=0.0)

    cache = {}
    for name in ("P07_STRAP_UPPER", "P07_STRAP_LOWER"):
        ob = bpy.data.objects[name]; base = ob.data
        n = len(base.vertices); co = [0.0] * (n * 3); base.vertices.foreach_get("co", co)
        W = ob.matrix_world; SCA = W.to_scale()[0]
        wp = [W @ Vector((co[3 * i], co[3 * i + 1], co[3 * i + 2])) for i in range(n)]
        C = ((min(p.x for p in wp) + max(p.x for p in wp)) * 0.5,
             (min(p.y for p in wp) + max(p.y for p in wp)) * 0.5)
        ang = [math.degrees(math.atan2(p.y - C[1], p.x - C[0])) % 360.0 for p in wp]
        occ = [0] * BINS
        for a in ang:
            occ[int(a / (360.0 / BINS))] += 1
        runs = []; i = 0
        while i < BINS:
            if occ[i] == 0:
                j = i
                while j < BINS and occ[j] == 0:
                    j += 1
                runs.append((j - i, i, j)); i = j
            else:
                i += 1
        if runs and max(runs)[0] > 20:
            g = max(runs); root = g[2] * 360.0 / BINS; span = 360.0 - g[0] * 360.0 / BINS
        else:
            # ring cut open: seam is where the deform chain starts - find via DEF_00 weights
            vg = ob.vertex_groups[[v.name for v in ob.vertex_groups][0]]
            idx = []
            for v in base.vertices:
                for gg in v.groups:
                    if gg.group == vg.index and gg.weight > 0.99:
                        idx.append(v.index); break
            aa = sorted(ang[i] for i in idx)
            gaps = [(aa[k + 1] - aa[k], aa[k]) for k in range(len(aa) - 1)]
            gaps.append((aa[0] + 360 - aa[-1], aa[-1]))
            root = (max(gaps)[1] + max(gaps)[0]) % 360.0
            span = 360.0
        us = [(a - root) % 360.0 for a in ang]
        eb = [0] * (len(base.edges) * 2); base.edges.foreach_get("vertices", eb)
        used = set()
        for pgn in base.polygons:
            for ek in pgn.edge_keys:
                used.add(ek)
        pr = [(eb[2 * k], eb[2 * k + 1]) for k in range(len(base.edges))
              if (min(eb[2*k], eb[2*k+1]), max(eb[2*k], eb[2*k+1])) in used]
        random.shuffle(pr)
        keep = []
        for a_, b_ in pr:
            L = math.dist((co[3*a_], co[3*a_+1], co[3*a_+2]), (co[3*b_], co[3*b_+1], co[3*b_+2]))
            if L * SCA > 0.001:
                keep.append((a_, b_, L))
            if len(keep) >= 40000:
                break
        samp = list(range(n)); random.shuffle(samp); samp = samp[:9000]
        cache[name] = (us, keep, samp, span, SCA, root)

    for fr in FRAMES:
        sc.frame_set(fr)
        dg = bpy.context.evaluated_depsgraph_get()
        for name in ("P07_STRAP_UPPER", "P07_STRAP_LOWER"):
            us, keep, samp, span, SCA, root = cache[name]
            ob = bpy.data.objects[name]; W = ob.matrix_world
            ev = ob.evaluated_get(dg); me = ev.to_mesh()
            n = len(me.vertices); d = [0.0] * (n * 3); me.vertices.foreach_get("co", d)
            wpos = [W @ Vector((d[3 * i], d[3 * i + 1], d[3 * i + 2])) for i in range(n)]
            binw = span / NB
            acc = [None] * NB; cnt = [0] * NB
            zmin = [1e9] * NB; zmax = [-1e9] * NB
            for i in range(n):
                b = min(NB - 1, int(us[i] / binw))
                p = wpos[i]
                if acc[b] is None:
                    acc[b] = Vector((0, 0, 0))
                acc[b] += p; cnt[b] += 1
                if p.z < zmin[b]:
                    zmin[b] = p.z
                if p.z > zmax[b]:
                    zmax[b] = p.z
            idx = [b for b in range(NB) if cnt[b]]
            cl = [acc[b] / cnt[b] for b in idx]
            K = 6; devs = []
            for j in range(K, len(cl) - K):
                a = cl[j - K]; c = cl[j + K]; p = cl[j]
                ab = c - a
                if ab.length < 1e-9:
                    continue
                t = (p - a).dot(ab) / ab.length_squared
                devs.append((p - (a + ab * t)).length)
            mx = 0.0; sm = 0.0
            for a_, b_, L0 in keep:
                L = math.dist((d[3*a_], d[3*a_+1], d[3*a_+2]), (d[3*b_], d[3*b_+1], d[3*b_+2]))
                r = abs(L - L0) / L0
                sm += r
                if r > mx:
                    mx = r
            zex = [zmax[b] - zmin[b] for b in idx[1:-1]]
            inside = 0; mind = 1e9; dmind = 1e9; dhit = 0
            for i in samp:
                p = wpos[i]
                hd = bvhd.find_nearest(p, 0.8)
                if hd and hd[0] is not None:
                    ddd = (hd[0] - p).length
                    if ddd < dmind:
                        dmind = ddd
                    if ddd < 0.004:
                        dhit += 1
                for bb in (bvh, bvhu):
                    h = bb.find_nearest(p, 1.2)
                    if h and h[0] is not None:
                        dd = (h[0] - p).length
                        if dd < mind:
                            mind = dd
                hits = 0; o2 = p.copy()
                for _ in range(24):
                    h = bvh.ray_cast(o2 + Vector((0, 0, 1e-5)), Vector((0, 0, 1)), 40.0)
                    if h is None or h[0] is None:
                        break
                    hits += 1; o2 = h[0]
                if hits % 2 == 1:
                    inside += 1
            ev.to_mesh_clear()
            extra = ""
            if fr == 40:
                a = cl[0]; c = cl[-1]; ab = c - a
                dv = []
                for p in cl:
                    t = (p - a).dot(ab) / ab.length_squared
                    dv.append((p - (a + ab * t)).length)
                extra = " | straightness dev max=%.4f mean=%.4f" % (max(dv), sum(dv) / len(dv))
            out.append("f%-4d %-6s scallop max=%.4f mean=%.4f | stretch max=%.2f%% mean=%.3f%% | width %.4f..%.4f | body inside=%d/%d mindist=%.4f | device mindist=%.4f contact<4mm=%d%s"
                       % (fr, name[10:], max(devs), sum(devs) / len(devs), mx * 100,
                          sm / len(keep) * 100, min(zex), max(zex), inside, len(samp), mind, dmind, dhit, extra))
    sc.frame_set(1)
finally:
    bpy.context.window.scene = prev
    for s in bpy.data.scenes:
        s.frame_current = prevf[s.name]
print("\n".join(out))
