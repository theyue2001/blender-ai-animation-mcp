import bpy, math
from mathutils import Vector
out = []
SN = "05_SCN_P07_STRAP_RIG"
sc = bpy.data.scenes[SN]


def wm(o):
    m = o.matrix_basis.copy(); p = o.parent; c = o
    while p:
        m = p.matrix_basis @ c.matrix_parent_inverse @ m; c = p; p = p.parent
    return m


out.append("=== %s objects (70) ===" % SN)
for o in sorted(sc.objects, key=lambda x: x.name):
    nv = len(o.data.vertices) if o.type == 'MESH' else '-'
    mats = ",".join("%s[%s]" % (sl.material.name if sl.material else None, sl.link)
                    for sl in o.material_slots) if o.type == 'MESH' else ''
    vis = o.visible_get(view_layer=sc.view_layers[0]) if o.name in sc.objects else '?'
    out.append("  %-44s %-9s v=%-7s hr=%s vis=%s %s" % (o.name, o.type, nv, o.hide_render, vis, mats[:70]))

out.append("")
out.append("=== P07_BODY_REF collection ===")
c = bpy.data.collections.get("P07_BODY_REF")
if c:
    for o in c.objects:
        M = wm(o)
        bb = [M @ Vector(cc) for cc in o.bound_box]
        out.append("  %-34s %-8s v=%-7s hr=%s hv=%s" %
                   (o.name, o.type, len(o.data.vertices) if o.type == 'MESH' else '-',
                    o.hide_render, o.hide_viewport))
        out.append("      world bbox x %.3f..%.3f  y %.3f..%.3f  z %.3f..%.3f" %
                   (min(p.x for p in bb), max(p.x for p in bb),
                    min(p.y for p in bb), max(p.y for p in bb),
                    min(p.z for p in bb), max(p.z for p in bb)))
        out.append("      loc=%s scale=%s rot=%s" %
                   (tuple(round(v, 4) for v in M.translation),
                    tuple(round(v, 4) for v in M.to_scale()),
                    tuple(round(math.degrees(v), 2) for v in M.to_euler())))
        out.append("      in scenes: %s" % [s.name for s in bpy.data.scenes if o.name in s.objects])
        out.append("      mats: %s" % [sl.material.name if sl.material else None for sl in o.material_slots])
    # layer-collection exclusion state in this scene
    def find_lc(lc, nm):
        if lc.collection.name == nm:
            return lc
        for ch in lc.children:
            r = find_lc(ch, nm)
            if r:
                return r
        return None
    for vl in sc.view_layers:
        lc = find_lc(vl.layer_collection, "P07_BODY_REF")
        out.append("      layer_collection in %s: exclude=%s hide_viewport=%s holdout=%s indirect=%s"
                   % (vl.name, lc.exclude, lc.hide_viewport, lc.holdout, lc.indirect_only) if lc
                   else "      NOT in view layer %s" % vl.name)
else:
    out.append("  MISSING")

# ---- geometry of the male body --------------------------------------------
out.append("")
out.append("=== Male body geometry (as placed in P07 if present, else source) ===")
cand = [o for o in bpy.data.objects if o.name.startswith("Male") or o.name == "Male"]
for o in cand:
    M = wm(o)
    me = o.data
    n = len(me.vertices)
    co = [0.0] * (n * 3); me.vertices.foreach_get("co", co)
    P = [M @ Vector((co[3 * i], co[3 * i + 1], co[3 * i + 2])) for i in range(n)]
    zmin = min(p.z for p in P); zmax = max(p.z for p in P)
    xmin = min(p.x for p in P); xmax = max(p.x for p in P)
    ymin = min(p.y for p in P); ymax = max(p.y for p in P)
    out.append("  %s  n=%d  scenes=%s" % (o.name, n, [s.name for s in bpy.data.scenes if o.name in s.objects]))
    out.append("    x %.3f..%.3f   y %.3f..%.3f   z %.3f..%.3f   H=%.3f" %
               (xmin, xmax, ymin, ymax, zmin, zmax, zmax - zmin))
    # Z-slices: x-extent per slice reveals arms/hands/pose
    NB = 24
    out.append("    z-slice profile (frac of height : nverts : x-extent : y-extent):")
    for b in range(NB):
        lo = zmin + (zmax - zmin) * b / NB
        hi = zmin + (zmax - zmin) * (b + 1) / NB
        sl = [p for p in P if lo <= p.z < hi]
        if not sl:
            out.append("      %4.2f  (empty)" % (b / NB))
            continue
        out.append("      %4.2f  n=%-5d x %7.3f..%7.3f (%6.3f)  y %7.3f..%7.3f (%6.3f)"
                   % (b / NB, len(sl), min(p.x for p in sl), max(p.x for p in sl),
                      max(p.x for p in sl) - min(p.x for p in sl),
                      min(p.y for p in sl), max(p.y for p in sl),
                      max(p.y for p in sl) - min(p.y for p in sl)))
    # extreme +x / -x verts = fingertips if arms are out
    Px = sorted(P, key=lambda p: p.x)
    out.append("    most -X verts: %s" % [tuple(round(v, 2) for v in q) for q in Px[:4]])
    out.append("    most +X verts: %s" % [tuple(round(v, 2) for v in q) for q in Px[-4:]])
    Pz = sorted(P, key=lambda p: p.z)
    out.append("    lowest verts : %s" % [tuple(round(v, 2) for v in q) for q in Pz[:3]])
    out.append("    highest verts: %s" % [tuple(round(v, 2) for v in q) for q in Pz[-3:]])

# ---- where is the belt / device in world ----------------------------------
out.append("")
out.append("=== belt + device world extent ===")
for nm in ("P07_STRAP_UPPER", "P07_STRAP_LOWER"):
    o = bpy.data.objects.get(nm)
    if o:
        M = wm(o)
        bb = [M @ Vector(cc) for cc in o.bound_box]
        out.append("  %-20s x %.3f..%.3f y %.3f..%.3f z %.3f..%.3f" %
                   (nm, min(p.x for p in bb), max(p.x for p in bb),
                    min(p.y for p in bb), max(p.y for p in bb),
                    min(p.z for p in bb), max(p.z for p in bb)))
dev = [o for o in sc.objects if o.type == 'MESH' and o.name.startswith("P07R_")]
if dev:
    allb = []
    for o in dev:
        M = wm(o)
        allb += [M @ Vector(cc) for cc in o.bound_box]
    out.append("  device (%d P07R_* meshes) x %.3f..%.3f y %.3f..%.3f z %.3f..%.3f" %
               (len(dev), min(p.x for p in allb), max(p.x for p in allb),
                min(p.y for p in allb), max(p.y for p in allb),
                min(p.z for p in allb), max(p.z for p in allb)))
print("\n".join(out))
