import bpy, math
from mathutils import Vector
SN = "05_SCN_P07_STRAP_RIG"
sc = bpy.data.scenes[SN]
out = []

def wmat(o):
    m = o.matrix_basis.copy(); p = o.parent; c = o
    while p:
        m = p.matrix_basis @ c.matrix_parent_inverse @ m; c = p; p = p.parent
    return m

def bb(o):
    M = wmat(o); me = o.data
    n = len(me.vertices); co = [0.0]*(n*3); me.vertices.foreach_get("co", co)
    ps = [M @ Vector((co[3*i],co[3*i+1],co[3*i+2])) for i in range(n)]
    lo = Vector((min(p.x for p in ps), min(p.y for p in ps), min(p.z for p in ps)))
    hi = Vector((max(p.x for p in ps), max(p.y for p in ps), max(p.z for p in ps)))
    return lo, hi, n, len(me.polygons)

out.append("=== objects in %s (mesh) ===" % SN)
for o in sorted(sc.objects, key=lambda x: x.name):
    if o.type != 'MESH': continue
    lo, hi, nv, nf = bb(o)
    out.append("%-24s v=%-7d f=%-7d size=(%.3f,%.3f,%.3f) ctr=(%.3f,%.3f,%.3f) hide_r=%s"
               % (o.name, nv, nf, hi.x-lo.x, hi.y-lo.y, hi.z-lo.z,
                  (lo.x+hi.x)/2, (lo.y+hi.y)/2, (lo.z+hi.z)/2, o.hide_render))
out.append("")
out.append("=== non-mesh ===")
for o in sorted(sc.objects, key=lambda x: x.name):
    if o.type != 'MESH':
        out.append("%-24s %s parent=%s" % (o.name, o.type, o.parent.name if o.parent else None))
print("\n".join(out))
