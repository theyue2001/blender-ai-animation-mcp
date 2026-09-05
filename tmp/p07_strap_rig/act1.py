import bpy, math
from mathutils import Vector
SN = "05_SCN_P07_STRAP_RIG"
sc = bpy.data.scenes[SN]
out = []

# ---- Act 1 = strap only: park the human reference (kept, not deleted) ----
bc = bpy.data.collections["P07_BODY_REF"]
bc.hide_render = True
bc.hide_viewport = True
lc = sc.view_layers[0].layer_collection.children["P07_STRAP_RIG"].children["P07_BODY_REF"]
lc.exclude = True
out.append("P07_BODY_REF: excluded from view layer, hide_render=True (re-enable for the body pass)")


def wmat(o):
    m = o.matrix_basis.copy(); p = o.parent; c = o
    while p:
        m = p.matrix_basis @ c.matrix_parent_inverse @ m; c = p; p = p.parent
    return m


def profile(name):
    o = bpy.data.objects[name]; M = wmat(o); me = o.data
    n = len(me.vertices); co = [0.0] * (n * 3); me.vertices.foreach_get("co", co)
    wp = [M @ Vector((co[3*i], co[3*i+1], co[3*i+2])) for i in range(n)]
    C = ((min(p.x for p in wp) + max(p.x for p in wp)) * .5,
         (min(p.y for p in wp) + max(p.y for p in wp)) * .5)
    B = 360; acc = [0.0]*B; cnt = [0]*B
    for p in wp:
        a = math.degrees(math.atan2(p.y - C[1], p.x - C[0])) % 360.0
        b = int(a)
        acc[b] += math.hypot(p.x - C[0], p.y - C[1]); cnt[b] += 1
    return [acc[b]/cnt[b] if cnt[b] else None for b in range(B)], C


for clean, worn in (("64.002", "P01_STRAP_UPPER"), ("65.002", "P01_STRAP_LOWER")):
    pc, Cc = profile(clean)
    pw, Cw = profile(worn)
    dif = [abs(pw[b] - pc[b]) for b in range(360) if pc[b] and pw[b]]
    sig = [(b, round(pw[b] - pc[b], 3)) for b in range(0, 360, 30) if pc[b] and pw[b]]
    out.append("%s vs %s : radius delta max=%.3f mean=%.3f (world units; strap thickness ~0.016)"
               % (clean, worn, max(dif), sum(dif) / len(dif)))
    out.append("    delta by angle (0=+X, 90=front): %s" % sig)

bpy.ops.wm.save_mainfile()
out.append("saved in place")
print("\n".join(out))
