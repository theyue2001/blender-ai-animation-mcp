import bpy, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SN = "05_SCN_P07_STRAP_RIG"
sc = bpy.data.scenes[SN]
out = []

def wmat(o):
    m = o.matrix_basis.copy(); p = o.parent; c = o
    while p:
        m = p.matrix_basis @ c.matrix_parent_inverse @ m; c = p; p = p.parent
    return m

def build(names):
    V=[]; F=[]
    for nm in names:
        o = bpy.data.objects[nm]; M = wmat(o); me = o.data
        b = len(V)
        n = len(me.vertices); co=[0.0]*(n*3); me.vertices.foreach_get("co", co)
        for i in range(n): V.append(M @ Vector((co[3*i],co[3*i+1],co[3*i+2])))
        for pg in me.polygons:
            vs=list(pg.vertices)
            for k in range(1,len(vs)-1): F.append((b+vs[0], b+vs[k], b+vs[k+1]))
    return BVHTree.FromPolygons(V,F), V

def bounds(V):
    return (Vector((min(p.x for p in V),min(p.y for p in V),min(p.z for p in V))),
            Vector((max(p.x for p in V),max(p.y for p in V),max(p.z for p in V))))

for nm in ("P07R_59.002","P07R_60.002","P07R_63.002","P07R_64.005"):
    bvh, V = build([nm]); lo, hi = bounds(V)
    out.append("")
    out.append("### %s  x[%.3f %.3f] y[%.3f %.3f] z[%.3f %.3f]" %
               (nm, lo.x,hi.x, lo.y,hi.y, lo.z,hi.z))
    # scan for a through-channel along each axis
    for ax, (u, v) in (("X",(1,2)), ("Y",(0,2)), ("Z",(0,1))):
        NU, NV = 56, 56
        clear = []
        for iu in range(NU):
            for iv in range(NV):
                p = [0.0,0.0,0.0]
                p[u] = lo[u] + (hi[u]-lo[u])*(iu+0.5)/NU
                p[v] = lo[v] + (hi[v]-lo[v])*(iv+0.5)/NV
                a = "XYZ".index(ax)
                p[a] = lo[a] - 0.05
                d = [0.0,0.0,0.0]; d[a] = 1.0
                loc, nrm, idx, dist = bvh.ray_cast(Vector(p), Vector(d), (hi[a]-lo[a])+0.1)
                if idx is None:
                    clear.append((p[u], p[v]))
        if not clear: 
            out.append("  thru-%s: none" % ax); continue
        # keep only interior clear cells (surrounded by solid on the u/v perimeter of bbox is not required);
        # report bbox of the clear set restricted to cells not touching the bbox border
        pad_u = (hi[u]-lo[u])/NU; pad_v = (hi[v]-lo[v])/NV
        inner = [c for c in clear if lo[u]+pad_u*1.5 < c[0] < hi[u]-pad_u*1.5
                 and lo[v]+pad_v*1.5 < c[1] < hi[v]-pad_v*1.5]
        if not inner:
            out.append("  thru-%s: only border clearance (%d cells)" % (ax, len(clear))); continue
        # cluster inner cells into connected groups
        cs = set(); key = {}
        for c in inner:
            iu = int((c[0]-lo[u])/pad_u); iv = int((c[1]-lo[v])/pad_v)
            key[(iu,iv)] = c; cs.add((iu,iv))
        seen=set(); groups=[]
        for s in cs:
            if s in seen: continue
            st=[s]; seen.add(s); g=[]
            while st:
                q=st.pop(); g.append(key[q])
                for dd in ((1,0),(-1,0),(0,1),(0,-1)):
                    r=(q[0]+dd[0], q[1]+dd[1])
                    if r in cs and r not in seen: seen.add(r); st.append(r)
            groups.append(g)
        groups.sort(key=len, reverse=True)
        for g in groups[:3]:
            gu=[c[0] for c in g]; gv=[c[1] for c in g]
            out.append("  thru-%s HOLE cells=%-4d  %s[%.3f..%.3f] (%.3f)  %s[%.3f..%.3f] (%.3f)"
                       % (ax, len(g), "XYZ"[u], min(gu), max(gu), max(gu)-min(gu),
                          "XYZ"[v], min(gv), max(gv), max(gv)-min(gv)))
print("\n".join(out))
