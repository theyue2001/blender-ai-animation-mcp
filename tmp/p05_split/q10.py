import bpy, json
from mathutils import Vector
o = bpy.data.objects["WRN_49.002"]
me = o.data
vs = [v.co.copy() for v in me.vertices]
mn = Vector((min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs)))
mx = Vector((max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs)))
ext = mx-mn
axis = min(range(3), key=lambda i: ext[i])          # disc normal axis (thinnest)
u, w = [i for i in range(3) if i != axis]
# which side protrudes: use the far tail
vals = sorted(v[axis] for v in vs)
hi = vals[-1]; lo = vals[0]
band = 0.012
top = [v for v in vs if v[axis] > hi - band]
# simple grid clustering in (u,w)
clusters = []
for v in top:
    for c in clusters:
        if (v[u]-c["u"])**2 + (v[w]-c["w"])**2 < 0.022**2:
            c["n"] += 1; c["su"] += v[u]; c["sw"] += v[w]; c["sa"] += v[axis]
            c["u"] = c["su"]/c["n"]; c["w"] = c["sw"]/c["n"]
            break
    else:
        clusters.append({"u":v[u],"w":v[w],"n":1,"su":v[u],"sw":v[w],"sa":v[axis]})
clusters = [c for c in clusters if c["n"] >= 12]
clusters.sort(key=lambda c: -c["n"])
out = {"axis": "XYZ"[axis], "u_axis":"XYZ"[u], "w_axis":"XYZ"[w],
       "bbox":[[round(x,4) for x in mn],[round(x,4) for x in mx]],
       "hi": round(hi,4), "n_top": len(top),
       "clusters": [{"u":round(c["u"],4),"w":round(c["w"],4),"n":c["n"],
                     "a":round(c["sa"]/c["n"],4)} for c in clusters[:14]],
       "matrix_basis":[[round(x,4) for x in r] for r in o.matrix_basis]}
print(json.dumps(out, ensure_ascii=False, indent=1))
