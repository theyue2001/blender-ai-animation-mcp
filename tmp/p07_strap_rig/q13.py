import bpy, math
from mathutils import Vector
SN = "05_SCN_P07_STRAP_RIG"
sc = bpy.data.scenes[SN]
out = []
prev = bpy.context.window.scene
try:
    bpy.context.window.scene = sc
    sc.frame_set(40)
    dg = bpy.context.evaluated_depsgraph_get()
    ob = bpy.data.objects["P07_STRAP_UPPER"]; base = ob.data; W = ob.matrix_world
    SCA = W.to_scale()[0]
    n = len(base.vertices); co = [0.0] * (n * 3); base.vertices.foreach_get("co", co)
    wp = [W @ Vector((co[3*i], co[3*i+1], co[3*i+2])) for i in range(n)]
    C = ((min(p.x for p in wp) + max(p.x for p in wp)) * 0.5,
         (min(p.y for p in wp) + max(p.y for p in wp)) * 0.5)
    ang = [math.degrees(math.atan2(p.y - C[1], p.x - C[0])) % 360.0 for p in wp]
    ev = ob.evaluated_get(dg); me = ev.to_mesh()
    d = [0.0] * (n * 3); me.vertices.foreach_get("co", d)
    eb = [0] * (len(base.edges) * 2); base.edges.foreach_get("vertices", eb)
    bad = []
    for k in range(len(base.edges)):
        a_, b_ = eb[2*k], eb[2*k+1]
        L0 = math.dist((co[3*a_], co[3*a_+1], co[3*a_+2]), (co[3*b_], co[3*b_+1], co[3*b_+2]))
        if L0 * SCA <= 0.001:
            continue
        L1 = math.dist((d[3*a_], d[3*a_+1], d[3*a_+2]), (d[3*b_], d[3*b_+1], d[3*b_+2]))
        r = abs(L1 - L0) / L0
        if r > 0.5:
            bad.append((r, a_, b_, L0 * SCA, L1 * SCA))
    ev.to_mesh_clear()
    bad.sort(reverse=True)
    out.append("edges with >50%% length change at pose A: %d of %d" % (len(bad), len(base.edges)))
    vgn = [g.name for g in ob.vertex_groups]
    for r, a_, b_, L0, L1 in bad[:12]:
        ga = {vgn[g.group]: round(g.weight, 3) for g in base.vertices[a_].groups}
        gb = {vgn[g.group]: round(g.weight, 3) for g in base.vertices[b_].groups}
        out.append("  r=%.0f%%  restlen=%.5f -> %.5f | angA=%.1f angB=%.1f | wA=%s wB=%s"
                   % (r * 100, L0, L1, ang[a_], ang[b_], ga, gb))
    # how many verts fall in the seam region
    seam = [i for i in range(n) if ang[i] > 108 and ang[i] < 120]
    out.append("verts in 108-120 deg band: %d" % len(seam))
    sc.frame_set(1)
finally:
    bpy.context.window.scene = prev
print("\n".join(out))
