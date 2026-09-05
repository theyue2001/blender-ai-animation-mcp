import bpy, math, random
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SN = "05_SCN_P07_STRAP_RIG"
sc = bpy.data.scenes[SN]
out = []
FRAMES = [1632, 1824, 1860, 1896, 1932, 1968, 1992, 2004, 2016, 2088, 2160]
HWNAMES = ["P07R_58.002", "P07R_59.002", "P07R_60.002", "P07R_63.002", "P07R_64.005"]


def wmat(o):
    m = o.matrix_basis.copy(); p = o.parent; c = o
    while p:
        m = p.matrix_basis @ c.matrix_parent_inverse @ m; c = p; p = p.parent
    return m


def bvh_of(names):
    V = []; F = []
    for nm in names:
        o = bpy.data.objects[nm]; M = wmat(o); me = o.data
        b = len(V)
        n = len(me.vertices); co = [0.0] * (n * 3); me.vertices.foreach_get("co", co)
        for i in range(n):
            V.append(M @ Vector((co[3 * i], co[3 * i + 1], co[3 * i + 2])))
        for pg in me.polygons:
            vs = list(pg.vertices)
            for k in range(1, len(vs) - 1):
                F.append((b + vs[0], b + vs[k], b + vs[k + 1]))
    return BVHTree.FromPolygons(V, F, all_triangles=True, epsilon=0.0)


prev = bpy.context.window.scene
try:
    bpy.context.window.scene = sc
    HW = bvh_of(HWNAMES)
    random.seed(7)
    STR = {}
    for tag, obn in (("UPPER", "P07_STRAP_UPPER"), ("LOWER", "P07_STRAP_LOWER")):
        ob = bpy.data.objects[obn]; base = ob.data
        used = set()
        for pg in base.polygons:
            for ek in pg.edge_keys:
                used.add(ek)
        eb = [0] * (len(base.edges) * 2); base.edges.foreach_get("vertices", eb)
        ed = [(eb[2 * k], eb[2 * k + 1]) for k in range(len(base.edges))
              if (min(eb[2 * k], eb[2 * k + 1]), max(eb[2 * k], eb[2 * k + 1])) in used]
        random.shuffle(ed)
        ed = ed[:30000]
        n = len(base.vertices); co = [0.0] * (n * 3); base.vertices.foreach_get("co", co)
        P0 = [Vector((co[3 * i], co[3 * i + 1], co[3 * i + 2])) for i in range(n)]
        L0 = [(P0[a] - P0[b]).length for a, b in ed]
        vs = random.sample(range(n), min(9000, n))
        STR[tag] = (ob, ed, L0, vs, n)

    for fr in FRAMES:
        sc.frame_set(fr)
        dg = bpy.context.evaluated_depsgraph_get()
        line = []
        for tag in ("UPPER", "LOWER"):
            ob, ed, L0, vs, n = STR[tag]
            evo = ob.evaluated_get(dg); me = evo.to_mesh()
            d = [0.0] * (n * 3); me.vertices.foreach_get("co", d)
            M = wmat(ob)
            P = [Vector((d[3 * i], d[3 * i + 1], d[3 * i + 2])) for i in range(n)]
            st = []
            for k, (a, b) in enumerate(ed):
                if L0[k] > 1e-7:
                    st.append(abs((P[a] - P[b]).length - L0[k]) / L0[k])
            zs = [p.z for p in P]
            # band width via angular bins of the world positions
            Pw = [M @ p for p in P]
            C = ((min(p.x for p in Pw) + max(p.x for p in Pw)) * 0.5,
                 (min(p.y for p in Pw) + max(p.y for p in Pw)) * 0.5)
            bins = {}
            for p in Pw:
                bi = int(math.degrees(math.atan2(p.y - C[1], p.x - C[0])) % 360.0 / 2.0)
                lo, hi = bins.get(bi, (9e9, -9e9))
                bins[bi] = (min(lo, p.z), max(hi, p.z))
            wd = sorted(hi - lo for lo, hi in bins.values())
            wd = wd[1:-1] if len(wd) > 4 else wd
            # hardware penetration: parity ray cast upward
            inside = 0; mind = 9e9
            for i in vs:
                o2 = M @ P[i]
                loc, nrm, idx, dist = HW.find_nearest(o2, 0.30)
                if loc is not None:
                    mind = min(mind, (loc - o2).length)
                c = 0; org = o2 + Vector((0, 0, 1e-5))
                while c < 64:
                    h = HW.ray_cast(org, Vector((0, 0, 1)), 40.0)
                    if h[0] is None:
                        break
                    org = h[0] + Vector((0, 0, 1e-5)); c += 1
                if c % 2 == 1:
                    inside += 1
            evo.to_mesh_clear()
            line.append("%s stretch max=%.2f%% mean=%.3f%% | width %.4f..%.4f | inside HW=%d/%d mindist=%.4f"
                        % (tag, max(st) * 100, sum(st) / len(st) * 100,
                           wd[0], wd[-1], inside, len(vs), mind))
        out.append("f%-5d %s" % (fr, line[0]))
        out.append("       %s" % line[1])
finally:
    bpy.context.window.scene = prev
print("\n".join(out))
