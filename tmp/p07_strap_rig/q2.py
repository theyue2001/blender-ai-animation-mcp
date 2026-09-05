import bpy, math
from mathutils import Matrix, Vector
L=[]
def wmat(o):
    m = o.matrix_basis.copy()
    p = o.parent
    child = o
    while p:
        m = p.matrix_basis @ child.matrix_parent_inverse @ m
        child = p; p = p.parent
    return m
for name in ("64.002","65.002","58.002"):
    o = bpy.data.objects[name]
    M = wmat(o)
    L.append("=== %s ===" % name)
    L.append(" parentchain: %s" % " <- ".join(x.name for x in iter(lambda: None, 1)) if False else "")
    ch=[]; p=o.parent
    while p: ch.append(p.name); p=p.parent
    L.append(" parents: %s" % ch)
    loc,rot,sca = M.decompose()
    L.append(" world loc=%s scale=%s" % (tuple(round(v,4) for v in loc), tuple(round(v,5) for v in sca)))
    me = o.data
    vs = [M @ v.co for v in me.vertices]
    xs=[v.x for v in vs]; ys=[v.y for v in vs]; zs=[v.z for v in vs]
    L.append(" world bbox X %.4f..%.4f  Y %.4f..%.4f  Z %.4f..%.4f" % (min(xs),max(xs),min(ys),max(ys),min(zs),max(zs)))
    L.append(" verts=%d polys=%d edges=%d" % (len(me.vertices), len(me.polygons), len(me.edges)))
    # loose parts count
    L.append(" materials=%s" % [ms.material.name if ms.material else None for ms in o.material_slots])
print("\n".join(L))
