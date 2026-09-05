import bpy, math, random
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SN = "05_SCN_P07_STRAP_RIG"
sc = bpy.data.scenes[SN]
FRAMES = [1, 40, 80, 120, 160]
NB = 220
SPECS = [("P07_STRAP_UPPER", (0.0589, -2.1837), 112.0, 360.0),
         ("P07_STRAP_LOWER", (0.0455, -2.3473), 110.0, 320.0)]
out = []
random.seed(7)

prev = bpy.context.window.scene
prevf = {s.name: s.frame_current for s in bpy.data.scenes}
try:
    bpy.context.window.scene = sc
    # body BVH (Male only - closed mesh - for inside/outside parity test)
    mb = bpy.data.objects["P07R_Male"]
    bmw = mb.matrix_world
    bverts = [bmw @ v.co for v in mb.data.vertices]
    bpolys = [list(p.vertices) for p in mb.data.polygons]
    bvh = BVHTree.FromPolygons(bverts, bpolys, all_triangles=False, epsilon=0.0)

    cache = {}
    for name, C, root, span in SPECS:
        ob = bpy.data.objects[name]; base = ob.data
        n = len(base.vertices)
        co = [0.0] * (n * 3); base.vertices.foreach_get("co", co)
        W = ob.matrix_world
        us = []
        for i in range(n):
            v = W @ Vector((co[3 * i], co[3 * i + 1], co[3 * i + 2]))
            a = math.degrees(math.atan2(v.y - C[1], v.x - C[0])) % 360.0
            us.append((a - root) % 360.0)
        ebuf = [0] * (len(base.edges) * 2); base.edges.foreach_get("vertices", ebuf)
        pairs = [(ebuf[2 * k], ebuf[2 * k + 1]) for k in range(len(base.edges))]
        random.shuffle(pairs)
        pairs = pairs[:40000]
        rl = []
        for a_, b_ in pairs:
            rl.append(math.dist((co[3*a_], co[3*a_+1], co[3*a_+2]), (co[3*b_], co[3*b_+1], co[3*b_+2])))
        samp = list(range(n)); random.shuffle(samp); samp = samp[:9000]
        cache[name] = (us, pairs, rl, samp, span)

    for fr in FRAMES:
        sc.frame_set(fr)
        dg = bpy.context.evaluated_depsgraph_get()
        for name, C, root, span in SPECS:
            us, pairs, rl, samp, _ = cache[name]
            ob = bpy.data.objects[name]
            ev = ob.evaluated_get(dg); me = ev.to_mesh()
            n = len(me.vertices)
            d = [0.0] * (n * 3); me.vertices.foreach_get("co", d)
            W = ob.matrix_world
            sca = W.to_scale()[0]
            # deformed world positions of sampled verts (and bin means)
            acc = [None] * NB; cnt = [0] * NB
            binw = span / NB
            for i in range(n):
                b = int(us[i] / binw)
                if b >= NB:
                    b = NB - 1
                p = W @ Vector((d[3 * i], d[3 * i + 1], d[3 * i + 2]))
                if acc[b] is None:
                    acc[b] = Vector((0, 0, 0))
                acc[b] += p; cnt[b] += 1
            cl = [(acc[b] / cnt[b]) if cnt[b] else None for b in range(NB)]
            idx = [b for b in range(NB) if cl[b] is not None]
            # scalloping: deviation of each centreline point from the chord of its +-K neighbours
            K = 9; devs = []
            for j in range(K, len(idx) - K):
                a = cl[idx[j - K]]; c = cl[idx[j + K]]; p = cl[idx[j]]
                ab = c - a
                if ab.length < 1e-9:
                    continue
                t = (p - a).dot(ab) / ab.length_squared
                devs.append((p - (a + ab * t)).length)
            # band width per bin (extent along the dominant spread direction)
            wid = []
            for b in idx[::7]:
                pass
            # stretch
            mx = 0.0; sm = 0.0; cntE = 0
            for k, (a_, b_) in enumerate(pairs):
                L = math.dist((d[3*a_], d[3*a_+1], d[3*a_+2]), (d[3*b_], d[3*b_+1], d[3*b_+2]))
                if rl[k] > 1e-9:
                    r = abs(L - rl[k]) / rl[k]
                    sm += r; cntE += 1
                    if r > mx:
                        mx = r
            # band width: Z extent of the deformed strap per bin
            zex = []
            zmin = [1e9] * NB; zmax = [-1e9] * NB
            for i in range(n):
                b = int(us[i] / binw)
                if b >= NB:
                    b = NB - 1
                z = (W @ Vector((d[3 * i], d[3 * i + 1], d[3 * i + 2]))).z
                if z < zmin[b]:
                    zmin[b] = z
                if z > zmax[b]:
                    zmax[b] = z
            for b in idx:
                if zmax[b] > -1e8:
                    zex.append(zmax[b] - zmin[b])
            # body penetration (parity ray test upward against the Male mesh)
            inside = 0; mind = 1e9
            for i in samp:
                p = W @ Vector((d[3 * i], d[3 * i + 1], d[3 * i + 2]))
                hit = bvh.find_nearest(p, 1.0)
                if hit and hit[0] is not None:
                    dd = (hit[0] - p).length
                    if dd < mind:
                        mind = dd
                cur = p + Vector((0, 0, 0.0))
                hits = 0
                origin = p.copy()
                for _ in range(24):
                    h = bvh.ray_cast(origin + Vector((0, 0, 1e-5)), Vector((0, 0, 1)), 40.0)
                    if h is None or h[0] is None:
                        break
                    hits += 1
                    origin = h[0]
                if hits % 2 == 1:
                    inside += 1
            ev.to_mesh_clear()
            out.append("f%-3d %-16s scallop max=%.4f mean=%.4f | stretch max=%.3f%% mean=%.4f%% | bandZ %.4f..%.4f (rest-ref) | body: inside=%d/%d mindist=%.4f"
                       % (fr, name.replace("P07_STRAP_", ""), max(devs) if devs else 0, sum(devs) / len(devs) if devs else 0,
                          mx * 100, (sm / cntE) * 100 if cntE else 0, min(zex), max(zex), inside, len(samp), mind))
    sc.frame_set(1)
finally:
    bpy.context.window.scene = prev
    for s in bpy.data.scenes:
        s.frame_current = prevf[s.name]
print("\n".join(out))
